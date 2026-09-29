# Tool bootstrap

`bootstrap.py` installs the freely available analysis tools listed in
[`versions.json`](versions.json) and checks each one against a pinned SHA-256.
[`docs/tooling.md`](../../docs/tooling.md) explains why each tool is needed.

```sh
tools/bootstrap/bootstrap.py --list                       # pinned table
tools/bootstrap/bootstrap.py --prefix /opt/opencfw-tools   # everything
tools/bootstrap/bootstrap.py --prefix /opt/opencfw-tools --group ghidra
tools/bootstrap/bootstrap.py --prefix /opt/opencfw-tools --record objdiff-cli
tools/bootstrap/bootstrap.py --licensed                    # detect IAR / MetaWare / armcc
python3 -m venv .venv && .venv/bin/pip install -r tools/bootstrap/requirements.txt
```

Rules:

- Installs fail closed. An artifact is refused if its hash does not match, or
  if it has never been pinned (a `null` hash in `versions.json`).
- The first time a tool is pinned, run `--record <id>`, check the upstream
  release notes or signature yourself, then commit the updated `versions.json`.
  Several entries still carry `null` hashes. Their download URLs follow each
  vendor's naming pattern but must be confirmed when they are recorded.
- Licensed compilers (IAR EWARM, Synopsys MetaWare, Arm Compiler 5) are never
  downloaded. `--licensed` records each installed compiler's version output and
  binary hash in `build/toolchains.local.json`. That file is local and is not
  tracked.
- The bootstrap writes only to the prefix and to `build/`. It never touches
  firmware sources, evidence or submodules.
