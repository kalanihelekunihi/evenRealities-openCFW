# G2 BQ25180 charger-driver recovery

Status: complete linked-object census and host/Thumb-qualified clean-room
candidate; production-routed under the reviewed apple-clang profile. Run
addresses use `run = file_offset + 0x00437FE0`.

## Result

The retained first-party path `driver\chg\drv_bq25180.c` owns 28 contiguous
linked bodies at `[0x0053A670,0x0053AF4C)`. They total 2,268 logical code
bytes, SHA-256
`7ddab9a21b4394ca80bbedcac0fee1141f4e407c7c86038f4aa52b9f50fc8620`.
The owned 116-byte literal pool at `[0x0053AF4C,0x0053AFC0)` has SHA-256
`1709443848efd8bb84f60e554b5d07002e4d74f32a13a5288ea6e1dd2b3da4cf`.
The complete 2,384-byte physical object has SHA-256
`a2886fb69c9abc85bfa25a1d71db3c9c040a47d0609751f71c9f5c305c6c1f30`.

Fifty-four intra-object calls and two exterior calls root every body. The
exterior sites are `0x004C6886 -> 0x0053AE66` (status refresh) and
`0x00509438 -> 0x0053AE7E` (hardware initialization). The bodies contain 93
direct calls in total. An exhaustive image scan finds no stored entry pointer,
stored strict-interior pointer, direct strict-interior branch, `B.W` ingress,
or even an unaligned raw interior-value window.

## Hardware and ABI contract

The stock low-level wrappers use I2C bus 7 and seven-bit address `0x6A`.
Writes ignore the backend result and return zero. Reads initialize their byte
to zero, invoke the backend, and return the resulting byte. The shared field
helper reads the register, clears `mask << shift`, ORs `value << shift`
without first masking `value`, writes the result, and returns the input value.

The public register layout and field encodings agree with TI's
[BQ25180 datasheet](https://www.ti.com/lit/ds/symlink/bq25180.pdf). The
datasheet is used only as a public register-map oracle; the implementation was
reconstructed from authenticated firmware behavior.

The driver runtime pointer is stored at `0x200744FC`. Status refresh writes
the raw FLAG0 byte at runtime offset `0x14` and the little-endian STAT0/STAT1
word at offset `0x16`. It also caches `(state & 0x7F) >> 5` at `0x20073B18`.
The device check reads MASK_ID (`0x0C`), rejects raw values below one, and
otherwise accepts only low-nibble device ID zero.

## Configuration behavior

The recovered setters preserve the stock encodings:

- battery regulation accepts 3500–4650 mV and writes `(mV - 3500) / 10`;
- fast-charge current accepts 5–1000 mA, encodes 5–35 mA as `mA - 5`, then
  uses `mA / 10 + 27`, saturated to `0x7F`;
- battery undervoltage accepts 2000–3000 mV and selects code 2 through 7 at
  the stock 2801/2601/2401/2201/2001 mV boundaries;
- input-current limit selects codes 0–7 at 0/100/200/300/400/500/700/1100
  mA; and
- event bits zero through six map to CHARGECTRL1 bits 2, 1, 0 then MASK_ID
  bits 7, 6, 5, 4, with inverse enable polarity.

Hardware initialization performs exactly 19 configuration calls. Beginning
with zeroed registers and MASK_ID `0xC0`, the final 13-byte register image is
`00 00 00 5A 24 24 1F 44 06 00 21 00 F0`. This includes 4.4 V regulation,
91 mA fast charge, the 1000 mA input bucket, 2.8 V undervoltage/precharge
thresholds, masked events, and charging enabled at exit.

## Reconstruction boundary

`components/apollo_main/core_overlay/chg_bq25180.c` is an independently
authored candidate (10,714 bytes, SHA-256
`0291aa058fd90a957b97fd0066e2d49bf16676b761662a32bdb5d717be74067b`).
Host tests cover raw status layout, voltage/current/bucket encodings, exact
defaults, the device-ID rejection path, and runtime refresh. A freestanding
Thumb build with warnings as errors exposes exactly 22 intended global text
symbols. The analyzer and manifests pin all 28 stock bodies, the pool, retained
names/assertions/path, call closure, runtime globals, and zero-interior result.

No historical source for this first-party file has been authenticated. The
candidate is production-routed in `overlay.json` as twenty-two relocated
leaves under the reviewed apple-clang profile. The concrete provider
bindings, recovered from the stock body call sequences, are the retained I2C
read backend at `0x0050436E`, the retained I2C write backend at
`0x005044B4`, and the retained `memset` provider at `0x0043C0E4`; the
assertion-diagnostic sink is compiled out by the pinned
`-DOPEN_CFW_BQ25180_ASSERT` no-op fail-stop binding (the same treatment the
ULED display-preprocess routing gives its assertion log), and the diagnostic
binding stays inert. Placement appends the twenty-two relocated leaves to the
overlay; every static helper inlines at `-O2`, so no leaf needs a local
symbol class or bound static data.

Twenty-two entry redirects with NOP fill replace the twenty-two stock bodies
that have a candidate leaf (1,792 ownership bytes). The six intra-TU-only
helper bodies (`bq25180_write_register`, `bq25180_read_register`,
`bq25180_update_field`, `bq25180_configure_event_mask`,
`bq25180_mask_events`, `bq25180_apply_defaults`, 476 bytes) have no exterior
or surviving caller and stay as dead retained stock; the 116-byte owned
literal pool stays retained stock. The candidate therefore claims 1,792
package ownership bytes. The linux-clang profile pins await Linux toolchain
regeneration.
