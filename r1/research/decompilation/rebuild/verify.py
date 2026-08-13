#!/usr/bin/env python3
import hashlib
import json
import subprocess
from pathlib import Path

root = Path(__file__).resolve().parent
manifest = json.loads((root / "manifest.json").read_text())
for name, metadata in manifest["images"].items():
    output = root / f"rebuilt-{name}.bin"
    subprocess.run([str(root / "emit_image"), name, str(output)], check=True)
    digest = hashlib.sha256(output.read_bytes()).hexdigest()
    if digest != metadata["sha256"] or output.stat().st_size != metadata["bytes"]:
        raise SystemExit(f"verification failed for {name}")
    print(f"verified {name}: {metadata['bytes']} bytes {digest}")
