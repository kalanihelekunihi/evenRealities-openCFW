#!/usr/bin/env python3
"""Reset-entry variant of the shared instruction comparison fixture."""
import sys
from verify_manager_bridge import main
if __name__ == "__main__":
    sys.argv.append("--reset")
    main()
