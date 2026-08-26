# Cordio `attc_proc.c` source recovery

## Result

The stock interval `[0x004B5230,0x004B59C0)` is the complete linked Cordio
ATT client mandatory-PDU processor. It contains 15 functions / 1,884 code
bytes and a 52-byte trace/literal tail. Of the 16 public definitions, only
`AttcCancelReq` has no body, caller, or stored pointer and is dead-stripped.
The immediately preceding code belongs to ATT client core support; the next
function at `0x004B59C0` belongs to another translation unit.

The selected Apache-2.0 public source is Packetcraft r20.05c commit
`3656312d6b73e2a2c1c8b33ee0385bc199dd97e6`, Git blob
`edb846b41398a2580162a35063e3dc0955822804`, 24,074 bytes, SHA-256
`eff902813acebd98bf0ea4ef0540400a8f094d31dde81d2f5e4ae788ee876d10`.
The same blob spans r20.05 through r20.05c. The stock variable-length
multiple-read handlers, 17-entry response table, per-bearer state, and
bearer-aware CCB lookups exclude the r19/AmbiqSuite 2.x source family.

Official AmbiqSuite R4.4.1 source later imported by AmbiqAI/neuralSPOT is the
closest behavioral oracle: Git blob
`f189110a32de691dfd18a332d4aed6b7e74d8b30`, SHA-256
`9a6cbac237c70d9595b5f167cbc28cbbe535f131641779adfed4266a4738eb5f`.
Stock implements its response-method bound, minimum-PDU checks, and indication
length check, and the retained diagnostic reports line 794, exactly the R4
layout. The import is later corroboration, not a claim about the unresolved
historical generating commit. Product diagnostics further expand
`AttcIndConfirm`.

## Boundary and ingress

The physical object hashes to
`7e521c5695399e2c58d626a65ba261349de066bb0ac79a430105a0a5b4beb73a`;
the 15 concatenated bodies hash to
`aa8095e5a8fc97cf677e25c77b66bbcafec262642d54154672ec547266deec57`.
The retained source path occupies `[0x006DC874,0x006DC8D4)` and its only word
reference is the object-tail cell at `0x004B59B8`.

Raw Thumb decoding closes 20 direct calls. The response table at `0x00700964`
has 17 entries, 13 non-null: ten cells target six local processors and three
target processors in other ATT translation units. Exhaustive odd-pointer and
direct-BL scans find exactly those local stored entries and no strict-interior
ingress. Five odd-valued byte windows in packed data are explicitly pinned as
unaligned false positives. A sixth aligned collision is the literal ASCII word
`IRK\0` (`49 52 4B 00`), not a pointer-bearing object.

The response-table entries also prove the tiny boundaries omitted by Ghidra:
`attcProcReadRsp` and `attcProcReadMultVarRsp` are distinct two-byte `bx lr`
bodies, while the six-byte leaf between them is `attcProcWriteRsp`.

## ABI and behavior

The object references `attCb=0x200610AC`, `attcCb=0x2006F904`,
`pAttCfg=0x200004B4`, the response table at `0x00700964`, and the minimum-PDU
table at `0x00785270`. It parses and validates ATT error, MTU, discovery,
read, write, variable-read, notification, indication, and confirmation PDUs;
drives callbacks; manages continuation and flow control; and builds public
find/read/write/MTU requests through the serialized client request path.

The stock faithfully exposes an inherited R4 bounds defect. The method check
accepts methods through `ATT_METHOD_SIGNED_WRITE_CMD` (17), but the processing
table has entries only 0–16 and the minimum-PDU table only 0–12. Method 16
therefore reads the first byte of the following string (`0x61`, `'a'`) as its
minimum length, while method 17 reads the following `"Inva"` bytes as a
function pointer. These are fail-closed audit facts, not a claim of practical
reachability in normal response traffic, and reconstruction should preserve or
deliberately remediate them rather than silently treating adjacent bytes as
owned tables.

## Reproducibility

`tools/analyze_g2_cordio_attc_proc.py` pins the official image, every linked
body, body concatenation, physical object, retained path and literals, the
17-entry response table, the 13-byte minimum-PDU table and adjacent bytes, all
20 direct calls, all ten local stored entries, and zero strict-interior ingress.
The complete ledger is
`tools/manifests/packetcraft-cordio-attc-proc-function-map.tsv`; release
identity is recorded in
`tools/manifests/packetcraft-cordio-attc-proc-provenance.tsv`.

## Production replacement

`components/shared/cordio/runtime_cordio_attc_proc.c` maintains all sixteen
source definitions. Fifteen linked entries replace all 1,884 stock body bytes
with 1,694 compiled Cortex-M55 bytes plus 22 alignment bytes under 38 strict
relocations. Thirteen entries use guarded redirects; the two authenticated
two-byte `bx lr` leaves use exact in-place source copies because a four-byte
branch cannot fit. The source-only cancel API is target-compiled without
inventing stock coverage.

Bounded method dispatch and minimum-length switches deliberately remediate the
authenticated method-16/17 adjacent-table overrun. One-based connection IDs
now index the three on-deck slots as `connection_id - 1`, and the authenticated
cancel event is 19. Host tests cover response,
error, MTU, callback, indication/confirmation, message serialization, MTU and
timeout failure, public request encoding, and the rejected method-17 path.
The canonical overlay/component/package sizes are 353,336 / 3,876,732 /
4,655,226 bytes; the package SHA-256 is
`b10166d4f1c1f91f348c3ee360afb2af1499df59715491a1256a1d0545f548bc`.
Live ATT/EATT peer, controller, timer, flow-control, and buffer-lifetime
validation remains blocked by unavailable authorized responsive G2/EM9305
physical evidence. No image was signed, flashed, or installed.
