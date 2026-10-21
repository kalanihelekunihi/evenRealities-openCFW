# G2 evidence read by tools

Data produced by earlier analysis campaigns that current tools, manifests or
the build still read. They were moved here from `g2/analysis/` when that tree
was removed on 2026-10-21; the original locations are in Git tag
`pre-consolidation`. Treat them as inputs: regenerate them with the tool that
owns them rather than editing by hand.

| Path | Origin (`pre-consolidation:g2/analysis/...`) | Read by |
| --- | --- | --- |
| `bundle-accounting/full-accounting.json`, `bundle-accounting/resource-expansion/` | `coverage-audit-parallel-2026-10-09/bundle-accounting-2026-10-13/` | `tools/build/firmware_coverage.py`, `catalog_resources.py`, `resources.json`, `resource-inventory.json`, `resources/build_g2_catalog.py` |
| `instructions-current/` (Git LFS) | `rescan-2026-10-06T140235Z/instructions-current/` | `tools/build/catalog_disassembly.py`, `disassembly-evidence.json` |
| `case-semantic-strings.json` | `c-source-completion-20261011/m0/` | `resources/g2/s200-v2.2.6.10/manifest.json` |
| `mapped-readonly-data.json` | `source-replacement-ledger-2026-10-08-readonly/` | resources manifest |
| `touch-msclp-unique-exact-sections.json` | `touch-msclp-attribution-2026-10-08/unique-exact-sections.json` | `tools/build/touch_gcc.py`, `source-plan.json` |
| `l8-resource-extraction.json` | `shortcut-batch-2026-10-05/resources/extraction.json` | `g2/tools/manifests/g2-l8-resource-map.json` |
| `codec-dsp-table-provenance.json` | `xuantie-csky-dsp-execution-20261009T201800Z/table-provenance.json` | resources manifest |
| `tinyframe-checksum-verification.json` | `tinyframe-checksum-build-gap-20261010-implementation/verification.json` | resources manifest |
| `bootloader-manual-body-bindings.json` | `c-source-completion-20261011/apollo/manual_body_bindings.json` | 483 bootloader body bindings, a superset of `g2/symbols/bootloader.tsv`; not yet merged into it |
| `em9305-rom/` | `c-source-completion-20261011/em9305/` | `g2/src/em9305/qpc-scheduler/resident_rom_bindings.json` |

The hash-pinned Ghidra corpus is separate, in [`../research/`](../research).
