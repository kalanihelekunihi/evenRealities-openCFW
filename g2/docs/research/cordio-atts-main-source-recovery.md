# Cordio ATT server owner/dispatcher source audit

Status date: 2026-08-09  
Target: G2 `s200_v2.2.6.10` Apollo main

## Outcome

The stock `atts_main.c` translation unit is completely partitioned at
`[0x0053498C,0x00535488)`, 2,812 bytes, SHA-256
`bbb2af59b583526d4e63a1e2f18fb8dbeec790518b694922061565cc9b511deb`.
Seventeen linked functions contribute 2,710 code bytes and hash to
`8fd2f55f88f2c162a1278917a5aa0318846d22e59cb8c62700bc4ed5a4a9fd46`
when concatenated. Five alignment/category gaps and the 72-byte trailing
literal pool contribute the remaining 102 bytes.

The source inventory has 21 functions. `AttsAuthorRegister`, `AttsSetAttr`,
`AttsGetAttr`, and `AttsErrorTest` have no standalone stock body, direct
caller, or stored entry and are classified source-only in this image. The
other 17 definitions are linked. Forty-five direct BL sites land on exact
entries. Four registered pointers are the data, control, message, and
connection callbacks in `attsFcnIf`; no accepted pointer or direct BL lands in
a strict body interior. Raw byte scanning finds 40 entry-shaped interior byte
windows, but they are instruction overlaps or ASCII/data fragments rather
than function-pointer roots and are pinned separately rather than promoted.

The retained source path begins at `0x006DC9F4` and its sole pointer cell is
`0x00535458`. Stock remains cut forward; no production bytes changed.

## Live processor dispatch and initialization provenance

`attsProcFcnTbl` is not a flash-resident table. It is a 72-byte initialized
SRAM object at `0x2000045C`, recovered from the authenticated IAR scatter
record whose decoded output hashes to
`df1a1fdf7b2792a7c4ef7a2c5cc6d1423bc7833b556fdfcedb8d6d927fbbb743`.
The live table itself hashes to
`e468091048ea8d3f4b301a8eaf3edce9085c7a136fb33d1407cbe6696209828e`:

| method | processor |
|---:|---|
| 0 | `NULL` |
| 1 | `attsProcMtuReq` (`0x0056C6FD`) |
| 2 | `attsProcFindInfoReq` (`0x0056C931`) |
| 3 | `attsProcFindTypeReq` (`0x0056DC05`) |
| 4 | `attsProcReadTypeReq` (`0x0056DD9D`) |
| 5 | `attsProcReadReq` (`0x0056CAA9`) |
| 6 | `attsProcReadBlobReq` (`0x0056DA9F`) |
| 7 | `attsProcReadMultReq` (`0x0056E0DF`) |
| 8 | `attsProcReadGroupTypeReq` (`0x0056E26D`) |
| 9, 10 | `attsProcWrite` (`0x005A5E3B`) |
| 11 | `attsProcPrepWriteReq` (`0x005A5FC3`) |
| 12 | `attsProcExecWriteReq` (`0x005A6171`) |
| 13, 14 | `NULL` |
| 15 | `attsProcValueCnf` (`0x00533DD9`) |
| 16 | `attsProcReadMultiVarReq` (`0x0056CBCB`) |
| 17 | `NULL` |

The corresponding 18-byte `attsMinPduLen` array at `0x0077E2D0` is
`00 03 05 07 05 03 05 05 05 03 03 05 02 00 00 01 00 0f`, SHA-256
`927697413fa714628e6101c45f23d8a766fecef0384f552deb28b667bab03810`.
Method 17 remaining null independently agrees with the bounded
`atts_sign.c` processing-path exclusion.

The raw word at `0x00791AD0` also contains `0x00533DD9`, but it lies inside the
compressed IAR initializer stream. It is evidence for the decoded table, not
the runtime dispatch-cell address. The live method-15 cell is `0x20000498`.

## Server interface and EATT ABI

`attsFcnIf [0x007852F0,0x00785300)` contains the odd Thumb pointers
`{0x0053498D,0x00534C8B,0x00534C43,0x00534ABB}` for data, L2CAP control,
message, and connection callbacks. Its SHA-256 is
`ac310299eb7761edbb967813e18c633dc21604da0b705b47ff0551656e928e6a`.

`AttsInit` proves the EATT layout directly. `attsCb` is `0x2006E5F0`; its group
queue is at `+0x258`, indication interface at `+0x260`, and signing message
callback at `+0x264`. It initializes nine 64-byte server CCBs (three
connections by three bearers), with connection groups at stride `0xC0`, main
ATT CCB at `+0x10`, connection ID at `+0x24`, and bearer slot at `+0x25`.
Finally it stores `attsFcnIf` at `attCb+0x40`, where `attCb=0x200610AC`.

The data callback resolves the server CCB by connection handle, translates the
ATT opcode to an 18-entry method index, applies CSF/change-awareness policy,
checks the method's minimum PDU length, dispatches through the live processor
table, and emits an ATT error response when required. Connection close clears
prepared writes and fans out to the registered server subinterfaces. The
message path completes database-hash CMAC work and pending database-hash read
responses. Attribute groups remain handle-sorted under the WSF task lock, and
database changes mark the CSF hash stale before recalculation.

## Source lineage

Packetcraft r20.05 through r20.05c provides the public EATT-aware ancestry at
Git blob `998e6300d08ddcb18b2c91c17ca4b90da2b6e04b`, 28,310 bytes, SHA-256
`07f4aaad4f2ef9df3f0e6c9da6bc056e480ce4b60f0f0c787b3acf9791764698`.
It does not contain the three later `ATT_CHECK_DATA_LENGTH` checks in
`attsDataCback`.

Stock contains the hardened behavior: it returns when `len==0` and requires
`len>=3` before extracting an ATT handle on the shared error paths. Those
checks select the later official AmbiqSuite R4.4.1 source family at Git blob
`bb99817115ce4da49ce26b5c52c4dd3418baaf88`, 28,588 bytes, SHA-256
`f28ba51cfb47d360508d5d8eac5187da34f84ac29180e712bcd1591f861eeff1`.
The later neuralSPOT import commit is exact corroboration, not proof of G2's
historical generating commit. The file is Apache-2.0.

## Reproduction

The source inventory, physical partition, callbacks, direct callers, EATT
control block, guarded data path, minimum-length table, decoded live processor
table, compressed-stream provenance, source path, and interior scans are
guarded by:

```sh
python3 tools/analyze_g2_cordio_atts_main.py --json
python3 -m unittest tests.test_analyze_g2_cordio_atts_main
```

## Production replacement

Maintained production source is
`components/shared/cordio/runtime_cordio_atts_main.c`. Seventeen guarded
redirects replace every 2,710 authenticated linked body byte with 2,622
compiled Cortex-M55 bytes plus 30 alignment bytes under 44 strict relocations.
The four public helpers absent from the stock link—authorization registration,
attribute set/get, and error-test control—are also implemented and compile as
isolated Cortex-M55 leaves without inventing stock coverage.

The host oracle covers hardened dispatch and error suppression, CCB lookup,
prepared-write cleanup, idle timers, indication/sign/hash message fanout,
database-hash reversal and pending reads, hashable-attribute state, CMAC input,
sorted group mutation, all public helpers, and the full 3x3 initialization.

The canonical overlay is 347,136 bytes, SHA-256
`06da1ac9a86c55d063b1edc9a780bb1d452e7117e1b3a2acc012daf23b66ce44`;
the Apollo component is 3,870,532 bytes, SHA-256
`a28013165b14cb5a5d9c1901d177828b378c64a48564c37ba0b53d97977e1658`;
and the deterministic package is 4,649,026 bytes, SHA-256
`dd4ae2bbee573322ec0976563b550c2dd462737344fe94ad4a12c24823951fd4`.
No image was signed, flashed, or installed. Live ATT/EATT peer exchange,
controller scheduling, asynchronous CMAC timing, and EM9305 behavior remain
blocked by unavailable authorized responsive physical evidence.

This closes the remaining `atts_*` server software tranche; its remaining
acceptance tail is physical validation rather than missing server C.
