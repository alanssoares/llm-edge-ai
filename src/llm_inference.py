#!/usr/bin/env python3
"""
LLM Inference Module for Edge Devices
Handles model loading, inference, and metrics collection
"""

import os
import time
import json
import logging
import psutil
import threading
from typing import Dict, Any, Optional, List
from datetime import datetime
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline

logger = logging.getLogger(__name__)


class LLMInferenceEngine:
    """Manages LLM inference on edge devices with metrics collection"""
    
    def __init__(
        self,
        model_name: Optional[str] = None,
        device_id: str = "unknown",
        max_length: int = 512,
        temperature: float = 0.7
    ):
        """
        Initialize the LLM inference engine
        
        Args:
            model_name: Hugging Face model identifier (e.g., "microsoft/Phi-3.5-mini-instruct")
            device_id: Device identifier for tracking
            max_length: Maximum token length for generation
            temperature: Sampling temperature for generation
        """
        self.model_name = model_name or os.getenv('LLM_MODEL_NAME', 'microsoft/Phi-3.5-mini-instruct')
        self.device_id = device_id
        self.max_length = max_length
        self.temperature = temperature
        
        # Model components
        self.model = None
        self.tokenizer = None
        self.pipeline = None
        
        # Metrics storage
        self.metrics_history: List[Dict[str, Any]] = []
        self.total_inferences = 0
        
        # Device info
        self.process = psutil.Process()
        self.cpu_count = psutil.cpu_count()
        
        # Determine compute device (CPU vs GPU)
        self.compute_device = "cuda" if torch.cuda.is_available() else "cpu"
        
        logger.info(f"Initializing LLM Engine for device: {device_id}")
        logger.info(f"Model: {self.model_name}")
        logger.info(f"Compute device: {self.compute_device}")
        logger.info(f"CPU cores: {self.cpu_count}")
    
    def load_model(self) -> None:
        """Load the LLM model and tokenizer"""
        try:
            logger.info(f"Loading model: {self.model_name}")
            start_time = time.time()
            
            # Get initial memory
            initial_memory = self._get_memory_usage()
            
            # Load tokenizer
            logger.info("Loading tokenizer...")
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_name,
                trust_remote_code=True
            )
            
            # Load model with optimizations for edge devices
            logger.info("Loading model...")
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                torch_dtype=torch.float32 if self.compute_device == "cpu" else torch.float16,
                trust_remote_code=True,
                low_cpu_mem_usage=True
            )
            
            # Move model to device
            self.model.to(self.compute_device)
            self.model.eval()  # Set to evaluation mode
            
            # Create pipeline for easier inference
            self.pipeline = pipeline(
                "text-generation",
                model=self.model,
                tokenizer=self.tokenizer,
                device=0 if self.compute_device == "cuda" else -1
            )
            
            load_time = time.time() - start_time
            final_memory = self._get_memory_usage()
            memory_delta = final_memory - initial_memory
            
            logger.info(f"Model loaded successfully in {load_time:.2f}s")
            logger.info(f"Memory increase: {memory_delta:.2f} MB")
            
            # Store model loading metrics
            self._log_model_loading_metrics(load_time, memory_delta)
            
        except Exception as e:
            logger.error(f"Error loading model: {e}", exc_info=True)
            raise
    
    def _get_memory_usage(self) -> float:
        """Get current memory usage in MB"""
        try:
            mem_info = self.process.memory_info()
            return mem_info.rss / (1024 * 1024)  # Convert to MB
        except Exception as e:
            logger.warning(f"Could not get memory info: {e}")
            return 0.0
    
    def _get_cpu_percent(self) -> float:
        """Get current CPU usage percentage"""
        try:
            return self.process.cpu_percent(interval=0.1)
        except Exception as e:
            logger.warning(f"Could not get CPU percent: {e}")
            return 0.0
    
    def _estimate_energy_consumption(
        self,
        inference_time: float,
        cpu_percent: float
    ) -> float:
        """
        Estimate energy consumption in millijoules (mJ)
        
        This is a simplified estimation based on:
        - CPU power consumption (assuming ~15W TDP for edge devices)
        - Inference time
        - CPU utilization
        
        Args:
            inference_time: Time taken for inference in seconds
            cpu_percent: Average CPU utilization during inference
            
        Returns:
            Estimated energy in millijoules
        """
        # Typical edge device power consumption
        # Raspberry Pi 4: ~5-7W idle, ~15W max
        # Jetson Nano: ~5-10W
        base_power_watts = 5.0  # Base power consumption
        max_power_watts = 15.0   # Maximum power under load
        
        # Calculate power based on CPU utilization
        power_watts = base_power_watts + (max_power_watts - base_power_watts) * (cpu_percent / 100.0)
        
        # Energy (J) = Power (W) × Time (s)
        energy_joules = power_watts * inference_time
        
        # Convert to millijoules
        energy_millijoules = energy_joules * 1000
        
        return energy_millijoules
    
    def analyze_telemetry(self, telemetry_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze telemetry data using the LLM and collect metrics
        
        Args:
            telemetry_data: Dictionary containing sensor telemetry data
            
        Returns:
            Dictionary containing analysis results and metrics
        """
        if self.model is None or self.tokenizer is None:
            raise RuntimeError("Model not loaded. Call load_model() first.")
        
        # Prepare prompt for analysis
        prompt = self._create_analysis_prompt(telemetry_data)
        
        # Collect metrics during inference
        start_time = time.time()
        memory_before = self._get_memory_usage()
        
        # Start CPU monitoring in background
        cpu_samples = []
        monitoring = {'active': True}
        
        def monitor_cpu():
            while monitoring['active']:
                cpu_samples.append(self._get_cpu_percent())
                time.sleep(0.05)  # Sample every 50ms
        
        monitor_thread = threading.Thread(target=monitor_cpu, daemon=True)
        monitor_thread.start()
        
        try:
            # Perform inference
            with torch.no_grad():
                outputs = self.pipeline(
                    prompt,
                    max_length=self.max_length,
                    temperature=self.temperature,
                    do_sample=True,
                    top_p=0.9,
                    num_return_sequences=1
                )
            
            analysis_result = outputs[0]['generated_text']
            
        except Exception as e:
            logger.error(f"Error during inference: {e}", exc_info=True)
            analysis_result = f"Error: {str(e)}"
        finally:
            # Stop CPU monitoring
            monitoring['active'] = False
            monitor_thread.join(timeout=1)
        
        # Calculate metrics
        inference_time = time.time() - start_time
        memory_after = self._get_memory_usage()
        memory_used = memory_after - memory_before
        avg_cpu_percent = sum(cpu_samples) / len(cpu_samples) if cpu_samples else 0.0
        energy_consumed = self._estimate_energy_consumption(inference_time, avg_cpu_percent)
        
        # Create metrics dictionary
        metrics = {
            'timestamp': datetime.now().isoformat(),
            'device_id': self.device_id,
            'model_name': self.model_name,
            'inference_time_seconds': round(inference_time, 4),
            'inference_time_ms': round(inference_time * 1000, 2),
            'memory_used_mb': round(memory_used, 2),
            'memory_total_mb': round(memory_after, 2),
            'cpu_percent_avg': round(avg_cpu_percent, 2),
            'cpu_percent_samples': len(cpu_samples),
            'energy_consumed_mj': round(energy_consumed, 2),
            'energy_consumed_j': round(energy_consumed / 1000, 4),
            'compute_device': self.compute_device,
            'prompt_length': len(prompt),
            'response_length': len(analysis_result)
        }
        
        # Store metrics
        self.metrics_history.append(metrics)
        self.total_inferences += 1
        
        # Log metrics
        logger.info(
            f"Inference #{self.total_inferences} - "
            f"Time: {metrics['inference_time_ms']:.2f}ms, "
            f"Memory: {metrics['memory_used_mb']:.2f}MB, "
            f"CPU: {metrics['cpu_percent_avg']:.2f}%, "
            f"Energy: {metrics['energy_consumed_mj']:.2f}mJ"
        )
        
        return {
            'analysis': analysis_result,
            'metrics': metrics,
            'telemetry_input': telemetry_data
        }
    
    def _create_analysis_prompt(self, telemetry_data: Dict[str, Any]) -> str:
        """
        Create a prompt for the LLM based on telemetry data
        
        Args:
            telemetry_data: Sensor telemetry data
            
        Returns:
            Formatted prompt string
        """
        data = telemetry_data.get('data', {})
        
        prompt = f"""Analyze the following IoT sensor data and provide a brief assessment:

Device ID: {telemetry_data.get('device_id', 'unknown')}
Timestamp: {telemetry_data.get('ts', 'unknown')}

Sensor Readings:
- Temperature: {data.get('temp', 'N/A')}°F
- Humidity: {data.get('humidity', 'N/A')}%
- CO Level: {data.get('co', 'N/A')} ppm
- Smoke: {data.get('smoke', 'N/A')}
- LPG: {data.get('lpg', 'N/A')}
- Light: {'On' if data.get('light') else 'Off'}
- Motion: {'Detected' if data.get('motion') else 'Not detected'}

Assessment: """
        
        return prompt
    
    def _log_model_loading_metrics(self, load_time: float, memory_delta: float) -> None:
        """Log model loading metrics"""
        loading_metrics = {
            'event': 'model_loading',
            'timestamp': datetime.now().isoformat(),
            'device_id': self.device_id,
            'model_name': self.model_name,
            'load_time_seconds': round(load_time, 2),
            'memory_increase_mb': round(memory_delta, 2),
            'compute_device': self.compute_device
        }
        
        # Save to file
        self._save_metrics_to_file(loading_metrics, 'loading_metrics')
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get summary statistics of all inference metrics"""
        if not self.metrics_history:
            return {'message': 'No inference metrics available'}
        
        inference_times = [m['inference_time_ms'] for m in self.metrics_history]
        memory_usage = [m['memory_used_mb'] for m in self.metrics_history]
        cpu_usage = [m['cpu_percent_avg'] for m in self.metrics_history]
        energy_consumption = [m['energy_consumed_mj'] for m in self.metrics_history]
        
        summary = {
            'device_id': self.device_id,
            'model_name': self.model_name,
            'total_inferences': self.total_inferences,
            'inference_time_ms': {
                'min': round(min(inference_times), 2),
                'max': round(max(inference_times), 2),
                'avg': round(sum(inference_times) / len(inference_times), 2)
            },
            'memory_usage_mb': {
                'min': round(min(memory_usage), 2),
                'max': round(max(memory_usage), 2),
                'avg': round(sum(memory_usage) / len(memory_usage), 2)
            },
            'cpu_usage_percent': {
                'min': round(min(cpu_usage), 2),
                'max': round(max(cpu_usage), 2),
                'avg': round(sum(cpu_usage) / len(cpu_usage), 2)
            },
            'energy_consumption_mj': {
                'min': round(min(energy_consumption), 2),
                'max': round(max(energy_consumption), 2),
                'avg': round(sum(energy_consumption) / len(energy_consumption), 2),
                'total': round(sum(energy_consumption), 2)
            }
        }
        
        return summary
    
    def save_metrics(self, filepath: Optional[str] = None) -> str:
        """
        Save all metrics to a JSON file
        
        Args:
            filepath: Optional custom filepath
            
        Returns:
            Path to the saved file
        """
        if filepath is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filepath = f"/app/metrics/inference_metrics_{self.device_id}_{timestamp}.json"
        
        metrics_data = {
            'summary': self.get_metrics_summary(),
            'detailed_metrics': self.metrics_history
        }
        
        self._save_metrics_to_file(metrics_data, filepath)
        return filepath
    
    def _save_metrics_to_file(self, data: Dict[str, Any], filename: str) -> None:
        """Save metrics data to JSON file"""
        try:
            # Create metrics directory if it doesn't exist
            metrics_dir = os.path.dirname(filename) if '/' in filename else '/app/metrics'
            os.makedirs(metrics_dir, exist_ok=True)
            
            filepath = filename if '/' in filename else os.path.join(metrics_dir, f"{filename}.json")
            
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
            
            logger.info(f"Metrics saved to: {filepath}")
            
        except Exception as e:
            logger.error(f"Error saving metrics: {e}", exc_info=True)
