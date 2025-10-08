#!/usr/bin/env python3
"""
Metrics Analysis and Comparison Tool

Analyzes LLM inference metrics and compares performance across different models.
"""

import json
import argparse
import glob
import os
from pathlib import Path
from typing import Dict, List, Any
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MetricsAnalyzer:
    """Analyzes LLM inference metrics from JSON files"""
    
    def __init__(self, metrics_dir: str = "metrics"):
        """
        Initialize metrics analyzer
        
        Args:
            metrics_dir: Directory containing metrics JSON files
        """
        self.metrics_dir = metrics_dir
        self.metrics_data = {}
    
    def load_metrics(self, device_name: str = None) -> Dict[str, Any]:
        """
        Load metrics from JSON files
        
        Args:
            device_name: Specific device to load metrics for (or None for all)
            
        Returns:
            Dictionary of loaded metrics by device
        """
        pattern = f"{self.metrics_dir}/"
        if device_name:
            pattern += f"{device_name}/"
        pattern += "**/*.json"
        
        files = glob.glob(pattern, recursive=True)
        
        if not files:
            logger.warning(f"No metrics files found in {self.metrics_dir}")
            return {}
        
        logger.info(f"Found {len(files)} metrics files")
        
        for filepath in files:
            try:
                with open(filepath, 'r') as f:
                    data = json.load(f)
                    
                    # Extract device name from path or summary
                    if 'summary' in data:
                        device_id = data['summary'].get('device_id', 'unknown')
                        model_name = data['summary'].get('model_name', 'unknown')
                        
                        key = f"{device_id}_{model_name}"
                        self.metrics_data[key] = data
                        
            except Exception as e:
                logger.error(f"Error loading {filepath}: {e}")
        
        return self.metrics_data
    
    def print_summary(self, device_key: str = None):
        """
        Print summary statistics
        
        Args:
            device_key: Specific device_model key (or None for all)
        """
        if not self.metrics_data:
            logger.warning("No metrics data loaded")
            return
        
        devices_to_print = [device_key] if device_key else list(self.metrics_data.keys())
        
        print("\n" + "="*80)
        print("LLM INFERENCE METRICS SUMMARY")
        print("="*80)
        
        for key in devices_to_print:
            if key not in self.metrics_data:
                logger.warning(f"No data found for {key}")
                continue
            
            data = self.metrics_data[key]
            summary = data.get('summary', {})
            
            print(f"\n📱 Device: {summary.get('device_id', 'unknown')}")
            print(f"🤖 Model: {summary.get('model_name', 'unknown')}")
            print(f"📊 Total Inferences: {summary.get('total_inferences', 0)}")
            
            # Inference time
            if 'inference_time_ms' in summary:
                time_stats = summary['inference_time_ms']
                print(f"\n⏱️  Inference Time (ms):")
                print(f"   Min: {time_stats.get('min', 0):.2f}")
                print(f"   Max: {time_stats.get('max', 0):.2f}")
                print(f"   Avg: {time_stats.get('avg', 0):.2f}")
            
            # Memory usage
            if 'memory_usage_mb' in summary:
                mem_stats = summary['memory_usage_mb']
                print(f"\n💾 Memory Usage (MB):")
                print(f"   Min: {mem_stats.get('min', 0):.2f}")
                print(f"   Max: {mem_stats.get('max', 0):.2f}")
                print(f"   Avg: {mem_stats.get('avg', 0):.2f}")
            
            # CPU usage
            if 'cpu_usage_percent' in summary:
                cpu_stats = summary['cpu_usage_percent']
                print(f"\n🖥️  CPU Usage (%):")
                print(f"   Min: {cpu_stats.get('min', 0):.2f}")
                print(f"   Max: {cpu_stats.get('max', 0):.2f}")
                print(f"   Avg: {cpu_stats.get('avg', 0):.2f}")
            
            # Energy consumption
            if 'energy_consumption_mj' in summary:
                energy_stats = summary['energy_consumption_mj']
                print(f"\n⚡ Energy Consumption:")
                print(f"   Min: {energy_stats.get('min', 0):.2f} mJ")
                print(f"   Max: {energy_stats.get('max', 0):.2f} mJ")
                print(f"   Avg: {energy_stats.get('avg', 0):.2f} mJ")
                print(f"   Total: {energy_stats.get('total', 0):.2f} mJ ({energy_stats.get('total', 0)/1000:.4f} J)")
            
            print("\n" + "-"*80)
    
    def compare_models(self, model_keys: List[str] = None):
        """
        Compare metrics across different models
        
        Args:
            model_keys: List of device_model keys to compare (or None for all)
        """
        if not self.metrics_data:
            logger.warning("No metrics data loaded")
            return
        
        keys_to_compare = model_keys if model_keys else list(self.metrics_data.keys())
        
        if len(keys_to_compare) < 2:
            logger.warning("Need at least 2 models to compare")
            return
        
        print("\n" + "="*80)
        print("MODEL COMPARISON")
        print("="*80)
        
        # Build comparison table
        print(f"\n{'Model':<40} {'Avg Time (ms)':<15} {'Avg Memory (MB)':<15} {'Avg CPU (%)':<12} {'Total Energy (mJ)':<18}")
        print("-"*100)
        
        comparison_data = []
        
        for key in keys_to_compare:
            if key not in self.metrics_data:
                continue
            
            data = self.metrics_data[key]
            summary = data.get('summary', {})
            
            model_name = summary.get('model_name', 'unknown')
            device_id = summary.get('device_id', 'unknown')
            
            # Extract short model name
            short_name = model_name.split('/')[-1] if '/' in model_name else model_name
            label = f"{short_name} ({device_id[:8]})"
            
            avg_time = summary.get('inference_time_ms', {}).get('avg', 0)
            avg_memory = summary.get('memory_usage_mb', {}).get('avg', 0)
            avg_cpu = summary.get('cpu_usage_percent', {}).get('avg', 0)
            total_energy = summary.get('energy_consumption_mj', {}).get('total', 0)
            
            print(f"{label:<40} {avg_time:<15.2f} {avg_memory:<15.2f} {avg_cpu:<12.2f} {total_energy:<18.2f}")
            
            comparison_data.append({
                'label': label,
                'model': model_name,
                'device': device_id,
                'avg_time': avg_time,
                'avg_memory': avg_memory,
                'avg_cpu': avg_cpu,
                'total_energy': total_energy
            })
        
        # Find best performing model for each metric
        if comparison_data:
            print("\n" + "="*80)
            print("BEST PERFORMERS")
            print("="*80)
            
            fastest = min(comparison_data, key=lambda x: x['avg_time'])
            print(f"\n⚡ Fastest Inference: {fastest['label']}")
            print(f"   Time: {fastest['avg_time']:.2f} ms")
            
            most_efficient_memory = min(comparison_data, key=lambda x: x['avg_memory'])
            print(f"\n💾 Most Memory Efficient: {most_efficient_memory['label']}")
            print(f"   Memory: {most_efficient_memory['avg_memory']:.2f} MB")
            
            most_efficient_cpu = min(comparison_data, key=lambda x: x['avg_cpu'])
            print(f"\n🖥️  Lowest CPU Usage: {most_efficient_cpu['label']}")
            print(f"   CPU: {most_efficient_cpu['avg_cpu']:.2f}%")
            
            most_efficient_energy = min(comparison_data, key=lambda x: x['total_energy'])
            print(f"\n⚡ Most Energy Efficient: {most_efficient_energy['label']}")
            print(f"   Energy: {most_efficient_energy['total_energy']:.2f} mJ")
            
            print("\n" + "="*80)
    
    def export_csv(self, output_file: str = "metrics_comparison.csv"):
        """
        Export metrics to CSV for further analysis
        
        Args:
            output_file: Output CSV filename
        """
        if not self.metrics_data:
            logger.warning("No metrics data loaded")
            return
        
        import csv
        
        with open(output_file, 'w', newline='') as f:
            writer = csv.writer(f)
            
            # Header
            writer.writerow([
                'Device ID', 'Model Name', 'Total Inferences',
                'Avg Inference Time (ms)', 'Min Inference Time (ms)', 'Max Inference Time (ms)',
                'Avg Memory (MB)', 'Min Memory (MB)', 'Max Memory (MB)',
                'Avg CPU (%)', 'Min CPU (%)', 'Max CPU (%)',
                'Total Energy (mJ)', 'Avg Energy (mJ)', 'Min Energy (mJ)', 'Max Energy (mJ)'
            ])
            
            # Data rows
            for key, data in self.metrics_data.items():
                summary = data.get('summary', {})
                
                row = [
                    summary.get('device_id', ''),
                    summary.get('model_name', ''),
                    summary.get('total_inferences', 0),
                    summary.get('inference_time_ms', {}).get('avg', 0),
                    summary.get('inference_time_ms', {}).get('min', 0),
                    summary.get('inference_time_ms', {}).get('max', 0),
                    summary.get('memory_usage_mb', {}).get('avg', 0),
                    summary.get('memory_usage_mb', {}).get('min', 0),
                    summary.get('memory_usage_mb', {}).get('max', 0),
                    summary.get('cpu_usage_percent', {}).get('avg', 0),
                    summary.get('cpu_usage_percent', {}).get('min', 0),
                    summary.get('cpu_usage_percent', {}).get('max', 0),
                    summary.get('energy_consumption_mj', {}).get('total', 0),
                    summary.get('energy_consumption_mj', {}).get('avg', 0),
                    summary.get('energy_consumption_mj', {}).get('min', 0),
                    summary.get('energy_consumption_mj', {}).get('max', 0)
                ]
                
                writer.writerow(row)
        
        logger.info(f"Exported metrics to {output_file}")
        print(f"\n✅ Metrics exported to: {output_file}")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Analyze and compare LLM inference metrics"
    )
    parser.add_argument(
        '--metrics-dir',
        type=str,
        default='metrics',
        help='Directory containing metrics JSON files (default: metrics)'
    )
    parser.add_argument(
        '--device',
        type=str,
        help='Analyze metrics for specific device only'
    )
    parser.add_argument(
        '--compare',
        action='store_true',
        help='Compare metrics across all models'
    )
    parser.add_argument(
        '--export-csv',
        type=str,
        help='Export metrics to CSV file'
    )
    
    args = parser.parse_args()
    
    # Create analyzer
    analyzer = MetricsAnalyzer(args.metrics_dir)
    
    # Load metrics
    logger.info(f"Loading metrics from: {args.metrics_dir}")
    analyzer.load_metrics(args.device)
    
    if not analyzer.metrics_data:
        logger.error("No metrics data found")
        return
    
    # Print summary
    analyzer.print_summary()
    
    # Compare models if requested
    if args.compare:
        analyzer.compare_models()
    
    # Export to CSV if requested
    if args.export_csv:
        analyzer.export_csv(args.export_csv)


if __name__ == "__main__":
    main()
