# G2 Touch project-source license readiness

The I2C protocol and sensing C/header pairs are original openCFW clean-room
works. Their own source comments identify independent behavioral
reconstruction from authenticated machine-code evidence and explicit provider
ports; they contain no copied upstream GPL or vendor source body.

The repository `NOTICE` grants an MIT option to contributor-owned original
work even when a file previously carried GPL solely because of aggregation or
linking. It also explicitly excludes material derived from another GPL work.
Applying that narrow grant, these four files now declare:

```text
SPDX-License-Identifier: MIT OR GPL-3.0-only
```

The expression preserves the original GPL option and makes the contributor
MIT option machine-readable. It does not relicense official firmware evidence,
resident ABI/tables, Infineon EULA providers, Apache-2.0 CAT2 source, or any
other upstream/GPL-derived file. The exact four source/header hashes and both
source-audit results are pinned by the license-readiness analyzer.

Hardware validation remains blocked by unavailable physical evidence and is independent
of this software-license conclusion.

```sh
python3 g2/tools/analyze_g2_touch_project_license_readiness.py --write-manifests
python3 -m unittest \
  g2.tests.test_analyze_g2_touch_project_license_readiness \
  g2.tests.test_analyze_g2_touch_i2c_source \
  g2.tests.test_analyze_g2_touch_sensing_source \
  g2.tests.test_analyze_g2_touch_software_readiness
```
