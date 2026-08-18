# Health crash-snapshot correlation

## Outcome

OpenR1 implements the product-owned composition of the retained health crash record. Wall-clock
status, timestamp, and UTC offset are caller-supplied values. The optional 896-byte opaque blob is
accepted from a provider callback boundary and is never interpreted by OpenR1. The retail caller
actually obtains a 736-byte (`0x2E0`) GoMore previous-state checkpoint from `0x0006ABE4`; because
the initializer requires exactly 896 bytes, the retail path does not copy or mark that blob.

Eleven recovered entries establish the record lifecycle:

| Recovered extent | Bytes | SHA-256 | Clean-room role |
| --- | ---: | --- | --- |
| `0x00058914..<0x00058936` | 34 | `7eb26f03d7b5a8707bced48531e9ebd2e909621d6aa02acb66f7d75cd9994dbf` | clear opaque blob and its magic, then reseal CRC |
| `0x0005893C..<0x0005895C` | 32 | `e67559e879afb244d2d2bd99ffd5228186b0393fb0fc7667279098895132d2f6` | clear one-shot snapshot, then reseal CRC |
| `0x00058960..<0x0005897C` | 28 | `419bbc925b895acd74a5f927d9382f43766aaa925fc4aceed878c5595973e2d7` | clear time status/offset/timestamp, then reseal CRC |
| `0x00058980..<0x000589AA` | 42 | `c4d522e85c95c8668f46478e869d06446abac404694b569346f2ed95d25b2d6b` | validated opaque-blob accessor |
| `0x000589B0..<0x000589E4` | 52 | `5bd3c20827924f79f7b4a29fe7e0a1bb0ccb1e1a616ff6efeaf19babfda560e4` | validated nonempty snapshot accessor |
| `0x000589E8..<0x00058A1E` | 54 | `1b1762232d1e140abe54b8647965c420ecdbbf3a52dd6493e7e0faa00290b9f9` | validated nonzero time accessor |
| `0x00058A24..<0x00058A3A` | 22 | `b4d552ebdccaceccb6248c11714557bceed132e8a3793852a642be4b21483791` | retained-record pointer binding and magic probe |
| `0x00059EE4..<0x0005A150` | 620 | `2563961270c5aa11adaf0e389b52fc3e7caed342539f9189c39cea9effa4c60a` | activity/HR/SpO2/HRV snapshot restore and one-shot clear |
| `0x0005A28C..<0x0005A2B4` | 40 | `0649b54b32572df04c3e14b66122e968eb8521baafd599740efbdef11b830a7d` | magic/CRC validator |
| `0x0005A2B8..<0x0005A320` | 104 | `c520dab61614b1e4647c24916cb5a06d68ebdb106a401ca18900c667aa1f5078` | record initializer and provider-input adapter |
| `0x0005A324..<0x0005A3CE` plus `0x0003F47C..<0x0003F530` | 350 | `8a1dfa00a7ffb6285c23c4456ccafa2fc0bc932311474dca1eadbfef7b27bbd2` | local-hour, activity, and health-cache snapshot builder address set |

The builder's entry block tail-branches at `0x0005A3CA` to the non-contiguous continuation
`0x0003F47C..<0x0003F530`. That 180-byte continuation is independently pinned by SHA-256
`3e93df87c819a5a0437f0088e8c46044c688c19cd8da4abb644ece9035ce29b3`; it copies HR, SpO2,
and HRV cache fields and snapshots the HR hourly accumulator. The ownership ledger records the
actual Ghidra function entry rather than inventing a second function at the continuation address.

## Exact retained layouts

The complete record is 966 bytes:

| Offset | Bytes | Meaning |
| ---: | ---: | --- |
| `0x000` | 4 | magic `0x5A5A5A5A` |
| `0x004` | 2 | time-status flags; only bit zero is replaced by current clock validity |
| `0x006` | 2 | signed UTC offset in minutes |
| `0x008` | 4 | UTC timestamp |
| `0x00C` | 896 | opaque provider blob, copied only when its length is exactly `0x380` |
| `0x38C` | 4 | provider-blob magic, written only after an exact-length copy |
| `0x390` | 52 | product-owned health snapshot |
| `0x3C4` | 2 | Modbus CRC16 over bytes `0x000..<0x3C4` |

The 52-byte snapshot stores HR latest timestamp and value, HR accumulator sum/count, SpO2 latest
timestamp and value, HRV latest timestamp and UInt16 value, six packed activity buckets for the
selected hour, the selected local hour, HR average/maximum/minimum, and availability bits
`0x01/0x02/0x04/0x08` for HR/SpO2/HRV/activity.

The local-hour calculation clamps the signed offset to `-720...720` minutes, applies it to the
provided UTC timestamp with the recovered UInt32 arithmetic, reduces modulo 86,400 seconds, and
selects one of 24 hours. Activity copies the six ten-minute buckets beginning at `hour * 6` and
packs steps into 12 bits plus active/all kilocalories into independent 10-bit fields.

HR availability is set when either the nonzero latest point or a nonzero hourly average exists.
The current accumulator sum/count is included only when it is nonempty and belongs to the selected
hour. SpO2 and HRV availability follows their recovered nonzero latest-point sentinel. A present
activity cache sets its availability bit even when all six packed words are zero.

The restore function validates the record and the snapshot's nonzero availability flags plus
`0...23` hour. Activity words are added into the six destination buckets with independent
12/10/10-bit wrap. HR restores a nonzero average, maximum-by-greater-value, minimum-by-lower
nonzero value, the latest point, and a nonzero accumulator count. SpO2 and HRV seed the selected
hour only when its existing average is zero, then replace their nonzero latest points. A successful
restore clears the 52-byte snapshot and recomputes the CRC, making the snapshot one-shot.

## Source boundary and verification

The crash-record APIs operate only on caller-owned typed caches and byte buffers. The initializer
accepts time-provider outputs and an optional opaque blob explicitly. `0x0006ABE4` is the already
reconstructed GoMore previous-state export: it reports `0x2E0` bytes and returns the live previous
state, so the initializer's exact `0x380` gate rejects it. The source-built target therefore clears
any old provider-blob marker, passes no provider blob, and creates the next retained one-shot
activity/HR/SpO2/HRV snapshot immediately after database recovery. It does not mislabel the GoMore
checkpoint as Goodix state or pad it to satisfy an unreachable stock branch.

Tests cover exact structure sizes and offsets, offset clamping, all availability bits, activity
packing and wrapped restore, accumulator hour mismatch/restore, HR extrema merge, SpO2/HRV
seed-only aggregation, opaque-blob length gating/access/clear, snapshot access/one-shot clear,
time access/clear, status-bit replacement, record magic, CRC generation, successful validation,
and corruption rejection.
No signing, update-validation, rollback, ACL, hardware-protection, or deployment path is changed.

The retained Nordic symbols link at `0x00032022` (validator), `0x00032054...0x00032168`
(magic probe, clears, accessors, and restore), `0x000324F4` (public snapshot-builder entry, with
its compiler-split body at `0x000323A0`), and `0x000324FE` (record initializer). The
`.openr1_health_api` table is at `0x0003B274` with size `0x110`. The verified unsigned application
is 94,804 bytes text, 236 bytes data, and 132,544 bytes BSS. Its standalone HEX and BIN SHA-256
values are `48e1b3fadfdb956fbdf5f637d48c9a5808db5394848fb4538450c0ff98be80cf` and
`421a42cf37dad04dadcff5d3b1742efcba4ba50fd1d2e52f26bcf00e5df24d35`.
