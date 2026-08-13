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
