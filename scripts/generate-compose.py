#!/usr/bin/env python3
"""
Entry point script for generating docker-compose.yml
This is a wrapper that calls the main generate_compose module
"""

import sys
from pathlib import Path

# Add src directory to Python path
src_path = Path(__file__).parent.parent / 'src'
sys.path.insert(0, str(src_path))

from generate_compose import main

if __name__ == '__main__':
    main()
