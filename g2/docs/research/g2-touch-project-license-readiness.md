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

## Wave-0.5 stock-address ownership correction

The final Touch ledger now applies the same distinction to the full 14,510-byte
semantic stock-address candidate union. The union itself is not blanket MIT
and is not production-ELF ownership. Its unchanged address/content digests are
partitioned in
`tools/manifests/g2-touch-final-source-candidate-provenance.tsv` into disjoint
MIT, `MIT OR GPL-3.0-only`, Apache-2.0, and overlap/output-unresolved routes.
Each row records the source-route license separately from stock-byte authority,
which remains `NOASSERTION`, and explicitly sets
`admitted_body_linked_to_stock_address=false` and
`production_elf_ownership=false`.

The nonproduction source-image receipt proves only that a named translation
unit was present when applicable. It does not prove that a semantically
admitted stock body survived linking at the stock address. In particular,
CAT2 bodies identified in public Apache-2.0 upstream source are recorded as
not linked as those bodies; the exact critical-section adapter has a linked
nonproduction translation unit but still no stock-address/output ownership
claim. The independent MIT Em_EEPROM replacement excludes Infineon EULA
comparison source. Current and final summaries bind the same provenance rows,
source-input hashes, and rendered receipts without promoting any candidate
bytes into production source.

Hardware validation is blocked by unavailable physical evidence and is independent of
this software-license conclusion; future qualification requires authorized
device evidence.

```sh
python3 g2/tools/analyze_g2_touch_project_license_readiness.py --write-manifests
python3 -m unittest \
  g2.tests.test_analyze_g2_touch_project_license_readiness \
  g2.tests.test_analyze_g2_touch_i2c_source \
  g2.tests.test_analyze_g2_touch_sensing_source \
  g2.tests.test_analyze_g2_touch_software_readiness
```
