# Cordio `attc_read.c` source recovery

## Result

The stock interval `[0x0056C3B0,0x0056C550)` is the complete linked Cordio
optional ATT client read unit. It contains four functions / 414 code bytes and
two terminal alignment bytes. The source inventory has seven definitions;
`AttcReadLongReq`, `AttcReadMultipleReq`, and `AttcReadByGroupTypeReq` have no
bodies, callers, or stored pointers and are dead-stripped. The function at
`0x0056C550` is unrelated ATT server database code, closing the boundary.

The selected Apache-2.0 source is Packetcraft r20.05c commit
`3656312d6b73e2a2c1c8b33ee0385bc199dd97e6`, Git blob
`bd2afa58c92129b5c5c93df31cec5f6c7c52ba87`, 11,426 bytes, SHA-256
`59d30e36b1c9acb9af1659f75af7e8151ef8329772f0de20fb9f9dc6e006517f`.
The blob is invariant through r20.05–r20.05c and is byte-identical to the later
official AmbiqSuite R4.4.1 import. Stock `attcProcReadLongRsp` reads the MTU
from `pMainCcb->sccb[pCcb->slot]`, independently excluding the r19/AmbiqSuite
2.x pre-EATT body, which reads a single connection MTU.

## Boundary and ingress

The physical interval hashes to
`d3286218cfb6d8bfe2a4a3a783073b4d98f67d5c93e91361c313013543a64495`;
the four concatenated bodies hash to
`fadfa806bdf0bfa8a4a02254ca0661f4f2ec3a709a0bbb28471feed859aa554b`.
This source has no retained path or trace literal in the stock image.

The already-closed `attcProcRspTbl` provides stored ingress at `0x00700970`
for `attcProcFindByTypeRsp` and `0x0070097C` for
`attcProcReadLongRsp`. Direct callers are `AttcDiscService`,
`AttcDiscCharStart`, and one application discovery path. Exhaustive scans find
three direct calls, exactly two stored entries, and no branch or pointer into a
strict function interior.

## Behavior

`attcProcFindByTypeRsp` validates ordered handle pairs, advances continuation
state, and rejects truncated or out-of-range responses.
`attcProcReadLongRsp` ends continuation on a short response or advances the
read offset by the callback value length. The two retained public request APIs
allocate and partially encode Find By Type Value and Read By Type packets,
then hand ownership to `attcSendMsg` for per-bearer serialization.

## Reproducibility

`tools/analyze_g2_cordio_attc_read.py` pins the image, four body hashes, body
concatenation, physical interval, terminal alignment, both response-table
cells, all three direct calls, both stored entries, and zero strict-interior
ingress. The full source/body ledger is
`tools/manifests/packetcraft-cordio-attc-read-function-map.tsv`; provenance is
recorded in `tools/manifests/packetcraft-cordio-attc-read-provenance.tsv`.

## Production replacement

`components/shared/cordio/runtime_cordio_attc_read.c` maintains all seven
source definitions. Four guarded redirects replace the complete 414-byte
linked stock body set with 440 compiled Cortex-M55 bytes plus two alignment
bytes under four strict relocations. The three dead-stripped long-read,
multiple-read, and group-type APIs are independently target-compiled without
inventing stock coverage. The maintained response parser also rejects a
trailing partial handle pair before decoding it, closing the public source's
out-of-bounds-read defect while preserving its invalid-response result.

Host execution covers ordered and malformed Find By Type responses,
continuation and next-handle state, per-bearer Read Long MTU behavior, and all
five request encoders. The canonical overlay is 347,724 bytes, SHA-256
`c1c193e775b15c5fe26dbb59eb56ec742828045fc69eaa721fe135c4314c6f5f`;
the Apollo component is 3,871,120 bytes, SHA-256
`ba1ee7f52a5bba817c2e8509721cde444328327e78a8e8e332ea09d7ce412c0f`;
and the deterministic package is 4,649,614 bytes, SHA-256
`a7d2627341cd8603e607a37c19d70ed42f7f5ba501fb6c76826664cb322de06d`.
Live ATT peer, controller, negotiated-MTU, continuation, and buffer-lifetime
validation remains blocked by unavailable authorized responsive G2/EM9305
physical evidence. No image was signed, flashed, or installed.
