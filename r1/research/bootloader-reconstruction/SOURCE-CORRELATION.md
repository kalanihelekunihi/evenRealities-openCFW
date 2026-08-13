# Function-name and source correlation

## Result

All 304 recovered bootloader functions now have stable names. The canonical ledger is
[`generated/function-names.csv`](generated/function-names.csv):

| Name class | Count | Meaning |
| --- | ---: | --- |
| recovered, high confidence | 268 | vector/source/instruction/audit evidence or strong corroborated BSim match |
| recovered, medium confidence | 36 | coherent SDK/library candidate with weaker uniqueness or compiler outlining |
| synthetic descriptive | 0 | the final compiler-outlined Nordic, nanopb, CryptoCell, and ArmCC entries are source-routed |

The former structural labels were promoted without changing the address oracle. The closing batch
includes ArmCC scatter/runtime entries, CC310 PKA/HAL/PAL symbols, Nordic scheduler/DFU/fstorage/BLE
helpers, and nanopb's `iter_from_extension` and `read_raw_value` internals.

## Provider closure

All 304 bootloader functions now have an implementation disposition:

| Provider family | Functions | Reconstruction rule |
| --- | ---: | --- |
| Nordic nRF5 SDK 17.1.0 | 218 | compile the pinned SDK source |
| Arm CryptoCell CC310 | 41 | link Nordic's supplied CC310 provider; do not recreate it |
| Nordic-bundled nanopb 0.3.x | 30 | compile the pinned bundled source |
| ArmCC/toolchain runtime | 12 | use the selected toolchain runtime or semantic equivalent |
| R1 product-specific | 3 | clean-room only: `dfu_advertising_name_get`, `gap_params_init`, and `bootloader_adv_name_record_valid` |

Thus, the bootloader has no unclassified provider entry. The three local behaviors remain
fail-closed and preserve the security-audit bounds; they are not substitutions for Nordic,
CryptoCell, nanopb, or compiler-runtime code.

## Evidence ranking

Names are chosen in this order:

1. Cortex-M vector position or instruction-identical SDK assembly;
2. behavior already recovered and validated in the R1 firmware security audit;
3. distinctive constants and direct source semantics;
4. high-separation BSim match plus coherent call topology/library cluster;
5. medium BSim match corroborated by neighboring functions and data flow; or
6. a temporary synthetic subsystem/role/address name, retained only until source closure.

BSim ranking alone is never treated as proof. Very small wrappers can be semantically identical,
and one compiler may outline a helper that another inlines. The raw candidate table is retained so
each decision is independently reviewable.

## Reproduction

Build the pinned official reference, then run:

```sh
scripts/firmware/run_r1_bootloader_source_correlation.sh /absolute/nrf52840_xxaa_s140.out
```

The script creates an isolated Ghidra project, imports the reference ELF and raw bootloader,
reapplies all function-boundary seeds, emits the name ledger, computes 3,576 ranked comparison
rows, records logs, and hashes the inputs/outputs.
