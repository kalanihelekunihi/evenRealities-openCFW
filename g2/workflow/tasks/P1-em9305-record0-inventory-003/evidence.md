# P1 EM9305 record 0 evidence packet

Evidence packet for `P1-em9305-record0-inventory-003`. This is a bounded excerpt set, not authority for decompilation. Source file hashes are pinned in `contract.json`.

## Target and scope

`g2/workflow/target.json` pins the complete official artifact as `s200_v2.2.6.10`, bundle SHA-256 `f4dfb0b49ad3de3c2daf17f8a27a157c3dc98411d6a0d3ab2cfd0918f41b9afa`. Its `ble_em9305` component entry pins `g2/blobs/official/g2-2.2.6.10/firmware_ble_em9305.bin`, size 211948, SHA-256 `91a38f7fc05555f86181ecb22b363e3239bfcaaa2ff6171e98524ae64821eca9`. Campaign target lock hash is `7312f4b855ff41ec823cc977485a8cc5e59a7235f834880b2217bf1f3ab138ff`.

## Parser boundaries

Pinned parser: `g2/components/em9305/source_image/record_package.py`, SHA-256 `33c4be40013dfcfcc786dc569e3fd108a1b9845aba211458b252a9d527e85ee4`. Relevant declarations: `HEADER = struct.Struct("<4sIII")`; `DESCRIPTOR = struct.Struct("<III")`; `MAGIC = bytes.fromhex("00020404")`; `parse_package` checks the magic, aligned metadata size, total payload length, canonical contiguous record slices, complete payload consumption, zero metadata alignment padding, and non-overlapping/non-wrapping target intervals. Parser import and `parse_package` are in-memory/read-only; `build_package` returns bytes and has no file-writing effect.

The package summary `g2/tools/manifests/em9305-record-package-summary.json` (SHA-256 `947bd35ff79c88e3f7386a4966ab50173589223efc76f1ce1b6bbec42df03b19`) reports metadata 124 bytes, payload 211824, four records and pins record 0 size 224, address 3145728, SHA-256 `137944c2c57f7114638d16c3be1c95a54afb9a4be600bc42a2b543add11571ee`.

## Record 0 reference

Pinned source manifest `g2/manifests/g2-2.2.6.10.json` (SHA-256 `1e6f7da11f63cf063098de2213a304e0a15fe99e9a932cdef9fedf32d2856c61`) names region `record_0`, package file offset 124, size 224, target `em9305`, target address 3145728, address status `confirmed_from_record_table`. Therefore this assignment maps package `[124,348)` to payload `[0,224)` and runtime `[0x00300000,0x003000e0)`. The latter mapping is a load address from the record descriptor, not a package offset.

## Decoder and ISA qualification

The procedure requires image-bound processor/ISA/endianness evidence and pinned decoder/spec/tool configuration before treating bytes as code. The workflow's `inventory_secondary_payloads.py` explicitly calls ARCv2 EM an inventory lead and says exact endian/ISA configuration remains to be checked against direct image-bound decoder evidence; it does not qualify the record-0 ISA mode or entry semantics. The local environment exposes `/opt/homebrew/bin/ghidraRun`; that executable's presence alone does not qualify a processor specification, language ID, project configuration, or exact disassembly. No verified record-0-specific toolchain manifest or processor-spec receipt was found in the bounded evidence reviewed for this task. Treat mode, entry point, and all code/data intervals as unknown unless separately authenticated during the task.

## Prior evidence and reuse scope

The pinned package summary proves wrapper-level identity, record mapping/count/length/hash, and stock round-trip for the entire package. It is reusable only for those wrapper claims. Its source inventory claims no record-0 code classification or pseudocode. Historical progress/research narratives and unpinned decoder output are not accepted as byte-bound architecture or instruction evidence.
