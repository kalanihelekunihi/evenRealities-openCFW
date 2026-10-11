# Main archive integration receipt

The source-only builder at `g2/components/main/source_candidate_20261010/build.py` now includes policy, append, and output units. Its 2026-10-10 run compiled **17** Cortex-M55 translation units and produced `g2/build/source-candidates/20261010-main/main-candidates.a` (SHA-256 `99d1e618dfdf4120d6a697c3124576e5a2c4a7493051f0b9a441a614e7cc3e48`) and relocatable `main-candidates.o` (SHA-256 `e4f77250f6ed9f101ad29dc03228d7df80b751e3506a8823cf1dec0c0a710a6c`). The generated `receipt.json` records all input and tool hashes, commands, output hashes and unresolved symbols.

The defined-symbol census confirms `g2_log_candidate_mask_normal`, `g2_log_candidate_optional_128_normal`, `g2_log_candidate_optional_32_64_normal`, `g2_log_candidate_append_normal`, and `g2_log_candidate_output` as `T` symbols in the combined object. `arm-none-eabi-ar t` lists the three new component objects. The only unresolved direct link symbols remain `g2_flashdb_candidate_compress`, `g2_flashdb_candidate_get_blob`, `g2_flashdb_candidate_literals`, and `g2_flashdb_candidate_log`. Function pointer providers do not appear in that list.

This integration changes the source candidate archive only. The direct logger body remains 10/11 complete and still needs the five named formatter/shared-buffer contracts in `extended-log-policy-20261010/REPORT.md`.
