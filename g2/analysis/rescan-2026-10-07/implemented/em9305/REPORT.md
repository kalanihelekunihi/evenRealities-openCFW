# EM9305 archive and DWARF shortcut probe

The reusable tool [em9305_shortcut.py](em9305_shortcut.py) inventories archive-member hashes and symbol counts without retaining SDK objects, summarizes selected QP/C DWARF structures as size/member-count/layout digests, and compares attributed QP/C function extents against the locked stock EM9305 record. It authenticates the selected v4.6 ELF and controller archive against `sdk-probe-evidence.json`, and requires the stock package hash recorded in its provenance.

The checked run used `emcore_standard_fpga_di03.elf` (authenticated SHA-256 `51e5aaee…4acb`) and `lib_emb_controller_iso.a` (`5626d3b3…5188`). The archive has 342 ELF members. Ten historically attributed QP/C functions were compared against the actual locked `s200_v2.2.6.10` EM9305 package (`91a38f7f…eca9`): two have identical names, extents, and bytes; eight have the same names but changed extents or bytes. The validated exact code rows are `IRQHandler_SWI1` and `QEQueue_init`. These results do not extend the historical 1,494-function attribution count.

Four QP/C interface types were summarized: `QActive`, `QEQueue`, `QHsmVtbl`, and `QTimeEvt`. Their extracted sizes, member counts, and layout digests are recorded in [run-di03/report.json](run-di03/report.json). Every v4.6 layout remains **unknown for stock v4.2 compatibility** because this checkout has no independently established v4.2 layout proof. Matching function bytes alone does not validate the associated type layout.

The SDK archive comparison history identifies SDK v4.2 from a third-party mirror whose repository has no license; the local v4.6 evaluation SDK is covered by its recorded EM agreement. This probe emits no SDK source, object, header, field list, or detailed layout. It does not use or install MetaWare. A stock-compatible MetaWare rebuild therefore remains blocked by MetaWare compiler availability, while source and type compatibility remain separate gaps.

Run from the repository root with the configured Python environment:

```sh
/Users/kalani/.local/share/opencfw/venv/bin/python \
  g2/analysis/rescan-2026-10-07/implemented/em9305/em9305_shortcut.py \
  --elf third-party/local-vendor/sources/em9305-v4.6/EM9305_SDK/EM9305_EM_BLEU_SDK_v4.6/emcore/bin/v4.6/standard/internal/emcore_standard_fpga_di03.elf \
  --archive third-party/local-vendor/sources/em9305-v4.6/EM9305_SDK/EM9305_EM_BLEU_SDK_v4.6/libs/third_party/emb/lib_emb_controller_iso.a \
  --stock-package g2/blobs/official/g2-2.2.6.10/firmware_ble_em9305.bin \
  --stock-symbols g2/symbols/ble_em9305.tsv \
  --out g2/analysis/rescan-2026-10-07/implemented/em9305/run-di03
```
