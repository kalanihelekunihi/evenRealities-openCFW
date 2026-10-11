#!/usr/bin/env python3
"""Replay the recorded source-only object census with hash checks."""
import hashlib
import json
from pathlib import Path
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    inventory = json.loads((HERE / 'inventory.json').read_text())
    compiler = inventory['compiler']
    if digest(compiler['path']) != compiler['sha256']:
        raise RuntimeError('Compiler identity changed')
    outputs = {}
    for unit in inventory['units']:
        if unit['status'] != 'compiled':
            continue
        for filename, expected in unit['dependencies'].items():
            if digest(filename) != expected:
                raise RuntimeError('Input identity changed: ' + filename)
        command = unit['command']
        output = Path(command[command.index('-o') + 1])
        output.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(command, cwd=ROOT, check=True)
        actual = digest(output)
        if actual != unit['object_sha256']:
            raise RuntimeError('Object identity changed: ' + str(output))
        outputs[str(output.relative_to(ROOT))] = actual
    receipt = {'status': 'PASS', 'objects': len(outputs),
               'inventory_sha256': digest(HERE / 'inventory.json'),
               'outputs': outputs,
               'scope': 'Separate source objects; no firmware link or hardware proof'}
    (HERE / 'rebuild-receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps({'status': 'PASS', 'objects': len(outputs)}))


if __name__ == '__main__':
    main()
