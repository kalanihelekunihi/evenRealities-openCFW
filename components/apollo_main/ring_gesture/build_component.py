#!/usr/bin/env python3
"""Build the pinned ring-gesture Apollo overlay with the common overlay tool."""

from __future__ import annotations

import sys
from pathlib import Path


COMPONENT_ROOT = Path(__file__).resolve().parent
OPENCFW_ROOT = COMPONENT_ROOT.parents[2]
sys.path.insert(0, str(OPENCFW_ROOT / "tools"))

from apollo_overlay import (  # noqa: E402,F401
    BuildError,
    build,
    decode_thumb_bl,
    main as overlay_main,
)


if __name__ == "__main__":
    raise SystemExit(
        overlay_main(
            [
                "--config",
                str(COMPONENT_ROOT / "overlay.json"),
                "--output-dir",
                str(COMPONENT_ROOT / "build"),
            ]
        )
    )
