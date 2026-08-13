# TinyFrame wire-format and configuration recovery audit

Status: research-only recovery. No production overlay, manifest, release pin,
shared coverage document, or firmware artifact changed. All findings are
recovered by focused disassembly of the official G2 `2.2.6.10` Apollo-main
image and are independently reproducible from the addresses below.

Scope: recover the complete TinyFrame compile-time configuration named as a
gap in [`../upstream-inventory.md`](../upstream-inventory.md) — ID/length/
type widths, SOF policy, checksum, parser timeout, payload limit, listener
counts, and object layout — so the library can later be vendored under its
MIT license with a reviewed `TF_Config.h` instead of clean-room re-creation.

## Identity evidence

The Apollo-main image embeds the exact vendored source path and the library's
runtime diagnostics, confirming TinyFrame is a third-party import built with
IAR:

| Evidence | Image location (run address) |
|---|---|
| `D:\01_workspace\s200_ap510b_iar_git\third_party\TinyFrame\TinyFrame.c` | `0x006FE474` |
| `[TinyFrame][TF] :error TF_InitStatic() failed, tf is null.` | `0x0071A188` |
| `[TinyFrame][TF] :error TF_Init() failed, out of memory.` | `0x0071A1C4` |
| `[sync.module.framework]TF_Multipart_Payload send, len = %d` | `0x0071924C` |

Load base for the raw `ota_s200_firmware_ota.bin`: file offset `0x20` maps to
run address `0x00438000`, so `run = file_offset + 0x00437FE0`. This base is
independently confirmed: 9,996 image pointers resolve exactly to NUL-preceded
string starts under it.

## Recovered functions

| Function | Run address | Role |
|---|---|---|
| `TF_AcceptChar` (byte parser / state machine) | `0x00491BE4` | Frame decode; reveals SOF, widths, checksum, timeout, payload limit, struct |
| `TF__ResetParser`-equivalent | `0x00491BD0` | Sets state `3`, clears `rxi` |
| `TF_HandleReceivedMessage` | `0x004919E8` | Listener dispatch; reveals listener array bases, entry sizes, and counts |
| `TF_CksumStart` | `0x0049172C` | Returns `0x0000` (checksum seed) |
| `TF_CksumAdd` | `0x00491730` | `crc = table[(crc ^ byte) & 0xFF] ^ (crc >> 8)` |
| `TF_CksumEnd` | `0x0049174E` | Identity (`uxth`), no final XOR |
| CRC-16 table (256 × `uint16`) | `0x006C0950` | Pointer stored at `0x00491EF0` |

## Recovered `TF_Config.h`

| Macro | Recovered value | Disassembly evidence |
|---|---|---|
| `TF_ID_BYTES` | `2` (big-endian on the wire) | ID state assembles two bytes into `+0x14` MSB-first: `orrs r5, r5, [+0x14], lsl #8` at `0x00491C7E`, advancing when `rxi == 2` (`0x00491C90`) |
| `TF_LEN_BYTES` | `2` (big-endian) | LEN state assembles `+0x16` (`0x00491CB2`), `rxi == 2` at `0x00491CC4` |
| `TF_TYPE_BYTES` | `2` (big-endian) | TYPE state assembles `+0x601E` (`0x00491CEA`), `rxi == 2` at `0x00491CFC` |
| `TF_USE_SOF_BYTE` | `1` | SOF state compares the byte and only advances on a match (`0x00491C5E`) |
| `TF_SOF_BYTE` | `0x01` | `cmp r5, #1` at `0x00491C5E`; on match resets to state 3 |
| `TF_CKSUM_TYPE` | `TF_CKSUM_CRC16` | 16-bit running checksum stored `strh` at `+0x601A`; two checksum bytes consumed (`cmp #2`); table-driven `TF_CksumAdd` |
| CRC-16 variant | CRC-16/ARC (poly `0x8005`, reflected `0xA001`, init `0x0000`, no final XOR, no reflect-out) | Extracted 256-entry table at `0x006C0950` byte-exactly regenerates from reflected poly `0xA001`; seed `0x0000` from `TF_CksumStart` |
| `TF_MAX_PAYLOAD_RX` | `0x6000` (24576) | Length bound `cmp #0x6001; blt` at `0x00491DAA`; data buffer spans `+0x18 … +0x6018` = `0x6000` bytes |
| `TF_PARSER_TIMEOUT_TICKS` | `100` | Timeout counter at `+0x12` compared `cmp #0x64` at `0x00491BEC`, reset on expiry |
| `TF_MAX_ID_LST` | `128` | `id_listeners` at `+0x6430`, entry `0x18` bytes (`muls #0x18`); next array at `+0x7030` → `(0x7030-0x6430)/0x18 = 128` |
| `TF_MAX_TYPE_LST` | `32` | `type_listeners` at `+0x7030`, entry `8` bytes (`<< 3`); next array at `+0x7130` → `0x100/8 = 32` |
| `TF_MAX_GEN_LST` | `10` | `generic_listeners` at `+0x7130`, entry `4` bytes (`<< 2`); count block at `+0x7158` → `0x28/4 = 10` |

## Recovered wire frame

```
+-------+---------+---------+---------+-------------+------------------+-------------+
|  SOF  |   ID    |   LEN   |  TYPE   | HEAD_CKSUM  |   DATA (len B)   | DATA_CKSUM  |
| 0x01  | 2 B BE  | 2 B BE  | 2 B BE  |   2 B CRC16 |    0..24576 B    | 2 B only when LEN > 0 |
+-------+---------+---------+---------+-------------+------------------+-------------+
```

- `HEAD_CKSUM` is CRC-16/ARC over `SOF || ID || LEN || TYPE`; the send-side
  composition closure proves the SOF byte is the first checksum input, correcting
  the earlier receive-only interpretation. Verified at
  `0x00491D36` (`TF_CksumEnd`) and compared to the received head checksum in
  `+0x601C` at `0x00491D40`. A mismatch resets the parser to state 0.
- `DATA_CKSUM` is CRC-16/ARC over a nonempty payload; zero-length frames complete
  after `HEAD_CKSUM` and omit this field. Verified at `0x00491E76` and
  compared at `0x00491E8A` before `TF_HandleReceivedMessage` is invoked.

## Recovered `TinyFrame_` object layout (partial, decode + dispatch fields)

| Offset | Type | Field |
|---|---|---|
| `+0x10` | `uint8_t` | `state` (SOF=0, ID=3, LEN=1, TYPE=4, HEAD_CKSUM=2, DATA=5, DATA_CKSUM=6) |
| `+0x12` | `uint16_t` | parser timeout counter |
| `+0x14` | `uint16_t` | `id` (in-progress) |
| `+0x16` | `uint16_t` | `len` (in-progress) |
| `+0x18` | `uint8_t[0x6000]` | `data` receive buffer |
| `+0x6018` | `uint16_t` | `rxi` (receive index) |
| `+0x601A` | `uint16_t` | running checksum |
| `+0x601C` | `uint16_t` | received checksum accumulator |
| `+0x601E` | `uint16_t` | `type` (in-progress) |
| `+0x6020` | `uint8_t` | `discard_data` flag |
| `+0x6430` | `TF_IdListener[128]` | id listeners, 24 B each: `{id@0 (u16), fn@4 (ptr), userdata@0x10, userdata2@0x14}` |
| `+0x7030` | `TF_TypeListener[32]` | type listeners, 8 B each: `{type@0 (u16), fn@4 (ptr)}` |
| `+0x7130` | `TF_GenericListener[10]` | generic listeners, 4 B each: `{fn@0 (ptr)}` |
| `+0x7158` | `uint8_t` | `count_id_lst` |
| `+0x7159` | `uint8_t` | `count_type_lst` |
| `+0x715A` | `uint8_t` | `count_generic_lst` |

The dispatcher returns from a listener are interpreted as `TF_STAY`/`TF_RENEW`
(2 → `TF_Renew`) and `TF_CLOSE` (3 → remove the listener), matching TinyFrame's
`TF_Result` semantics (`0x00491A6A`–`0x00491A94`).

## Closed source checks and remaining hardware validation

1. Confirm the CRC-16 table byte-for-byte equals TinyFrame's stock
   `TF_CksumAdd` table (done here: regenerates from reflected poly `0xA001`).
2. The send-side (`TF_Compose*`, peer bit and `next_id` rollover) is recovered
   and pins the transmit format and `TF_ID` peer-bit policy.
3. Validate with golden captured frames from the EFS/BLE transport before
   integration, per the inventory's "validate golden packets" requirement.
4. Exact core blobs are pinned to their introducing commit `eb75483e`; the
   historical checkout is bounded through core-identical `a29167a` and cannot
   be uniquely selected from linked firmware bytes.

This audit does not sign, flash, connect to, or mutate hardware.
