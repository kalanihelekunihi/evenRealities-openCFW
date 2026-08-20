# G2 pathless eAT core/sensor command recovery

Status: complete command-table cluster census and fail-closed behavioral
analysis; exact source-file partition unavailable, no source candidate, and
not production-routed. Run addresses use `run = file_offset + 0x00437FE0`.

## Result

Twelve registered handlers occupy `[0x005A5720,0x005A5984)`, between the
retained `at_fs.c` and `at_tp.c` objects. The bodies contribute 486 bytes with
concatenated SHA-256
`0d22c9e3a24002da78523b336961d3b84f9875be006380e65b28d73da99118c2`.
Four alignment/literal regions contribute 126 bytes with SHA-256
`17f9964ab7af8332ecdec76ce35a1be4e12aa5f85ecaa4cfaf2b72d739efebdb`.
The complete 612-byte physical cluster has SHA-256
`e0eb932297c2b57ba92b7a89b65d4ed5ae22038efb8d6bbf1fecaf4f2ef797a8`.

The 192-byte table `[0x006C92E0,0x006C93A0)` registers, in order, `AT^INFO`,
`AT^RESET`, `AT^PSN`, `AT^IMU_RAWDATA`, `AT^IMU_EULER`, `AT^SCRN_X`,
`AT^SCRN_Y`, `AT^ALS_READ`, `AT^ALS`, `AT^BRIGHTNESS`,
`AT^ALS_SCALE_READ`, and `AT^BRIGHTNESS_READ`. Its SHA-256 is
`e8d55ae6c7fd5e5cad86205eca9d6c1dfca9772ee29d415ad6151f209a7937d5`.
Those twelve odd command-record pointers are the only stored ingress. The
bodies contain 49 direct calls, but no direct entry call. Exhaustive scans find
no strict-interior stored pointer or direct branch and no `B.W` entry/interior
target.

## Command behavior

- `INFO` reports product `S200`, hardware, software `2.2.6.10`, codec and
  touch versions, compile stamp `Jul  6 2026 21:37:47`, PSN, BLE name, and BLE
  address.
- `RESET` emits the retained acknowledgement and invokes reset provider
  `0x0044B0AE`.
- `PSN` accepts exactly fourteen bytes, sends them through provider
  `0x004AF11C`, and rejects every other length.
- `IMU_RAWDATA` accepts parsed integer zero or one and calls provider
  `0x004A6AA8`; other integers emit the retained error and return zero.
- `IMU_EULER` reads three floats through `0x004A5D20` and prints promoted
  roll, pitch, and yaw values.
- `SCRN_X` is a stub-like acknowledgement. `SCRN_Y` rejects values at least
  193 and forwards smaller parsed values to `0x0046C984`. The machine code
  therefore accepts zero even though its retained diagnostic says 1-192.
- `ALS_READ` calls `0x004ADB50`, reads signed `LUX_BASE` at `0x200039BC`, and
  emits the retained UTF-8 response. `ALS` enables on one through `0x004AE10A`
  and disables on zero through `0x004AE218`; other parsed values call neither
  provider but are still acknowledged.
- `BRIGHTNESS` forwards its parsed integer to `0x0046C1C8` without local
  validation. The two read commands report providers `0x004AE946` and
  `0x0046BFE8` respectively.

## Reconstruction boundary

No retained source path partitions this interval. The descriptive handler
names in the manifest are derived from exact command registrations and
behavior, not claimed historical symbols. Consequently the linked cluster is
complete, but the historical source-file inventory, source-only function
count, license, and whole-source identity remain unknown. No clean-room
candidate exists, the cluster is absent from `overlay.json`, and it claims
zero package ownership bytes.

## Clean-room authorship and production routing

`components/apollo_main/core_overlay/at_core_sensor.c` is an independently
authored clean-room replacement (13,890 bytes, SHA-256
`2be0e0f81c74d3ec60f2a44fbcac8f7aff6c3f80e155d66c3c130a698ac285b3`) written
from this specification; no historical source survives. The twelve handlers
bind the retained providers recorded above — the printf-like output provider
at `0x00541430`, the parameter-length and integer-parse helpers at
`0x0044A43C`/`0x0048D868`, the bounded snprintf provider at `0x0044B728`,
and the per-command service providers — and reference every retained format,
response, and identity literal by its stock address, including the `%s` echo
literal at `0x005A5824` inside the owned PSN literal island and the signed
`LUX_BASE` shadow at `0x200039BC`. Recovered quirks are reproduced exactly:
`SCRN_Y` accepts zero through 192 despite its 1-192 diagnostic, the PSN error
reports the required length fourteen rather than the observed length, `ALS`
acknowledges unhandled values without calling either provider, and
`BRIGHTNESS` forwards its parsed integer without local validation. Host tests
pin the emitted byte streams, provider call sequences, and return values
against an oracle fixture; freestanding Thumb compilation exposes exactly the
twelve global handler symbols.

The candidate is routed into the Apollo main overlay under the reviewed
apple-clang profile as twelve relocated leaves (650 bytes plus sixteen
alignment bytes, overlay offsets 147,044-147,708 exclusive), reached through
twelve `B.W` entry redirects with NOP fill that replace the 486 stock body
bytes at `[0x005A5720,0x005A595E)`; the twelve stored registration pointers
in the command table `[0x006C92E0,0x006C93A0)` now reach the source leaves
through the redirects. The four owned alignment/literal islands (126 bytes)
stay retained stock data. Apple Clang 21 overlay/component/package sizes are
`147708/3671104/4449598` with SHA-256
`bcf4098013f7d704bcc2be618ec08e09865c0dc23e1bea232dbbfb6d1d090f36`,
`d1793fce0f3e5fe2707f5ff6257582f8cde35edb3300e0b66ff1d11a8692bd28`, and
`f3655acbe9ee2a5b8b559420c96ed79e7b1d4df2a3887c4caca7b4b22756914c`. The
leaves and redirects are gated `apple-clang`; the linux-clang profile keeps
its recorded pins. Ownership is the 486 stock body bytes. The component
build, source package, `open_cfw` verification, and the fail-closed analyzer
(now asserting the production routing) all pass.
