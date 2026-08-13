# G2 Hongshi/A6N-G ULED driver recovery

Status: complete linked-object census and protocol/ABI characterization;
historical source, clean-room implementation, and production routing pending.
Run addresses use `run = file_offset + 0x00437FE0`.

## Result

The retained first-party path
`driver\uled\hongshi_a6ng\drv_mspi_a6ng.c` owns the physical interval
`[0x005BBD48,0x005BD3A0)`. Its 22 linked bodies contribute 5,276 bytes with
SHA-256
`067122a8e2f85e5837971a237602bacda5106e9b3c82f79f19d9629da15ab88c`;
nine alignment/literal regions contribute the remaining 444 bytes with
SHA-256
`f8d5c55d7b44585bcf4774d784ed19f9ad7eb17cddc1ad24b0930a226cb08caa`.
The complete 5,720-byte object has SHA-256
`b4fc94ee5c7b645975b89e50425e5b400e7525e28721894c3f3517113dc52846`.

Five real Thumb entries at `0x005BBD48`, `0x005BBD70`, `0x005BCC10`,
`0x005BCC18`, and `0x005BD39C` were absent from the discovered-function set.
Raw prologue-to-return disassembly, source order, internal callers, retained
diagnostics, and the external callback table recover them without promoting
literal data to code.

## Linked surface

The exact body boundaries and hashes are pinned in
`tools/manifests/g2-uled-a6ng-function-map.tsv`.

| Group | Functions |
|---|---|
| lifecycle | `am_devices_mspi_a6ng_term`, `am_devices_mspi_a6ng_init`, `am_devices_mspi_hongshi_init` |
| register transport | `driver_a6ng_write_register`, `driver_a6ng_read_register`, `am_devices_mspi_hongshi_read_bank` |
| configuration | `am_devices_mspi_hongshi_configure`, `am_devices_hongshi_set_display_offset`, `driver_a6ng_set_gpio_output` |
| display control | `setBrightness`, `clear_framebuffer`, blocking and asynchronous `QSPI_PartialReflash`, `set_current_6bit`, `set_mode` |
| identification | `read_chipId`, `read_sn` |
| power and recovery | power-on/off sequences, `status_recovery`, mirror read, and `status_check_and_recovery` |

Several helper labels are descriptive clean-room names. Exact names are used
only where retained strings or current authenticated behavior establishes
them. Historical decompilation is semantic corroboration only, not a source
candidate or whole-source identity claim. Because the historical source
inventory is unavailable, this linked-object census is complete while the
source-only function count remains unknown.

## Ingress and ownership closure

Ninety-nine direct BL sites reach exact function entries, all from within the
object. The bodies contain 366 genuine direct calls in total. Four additional
four-byte windows at `0x005BC6CA`, `0x005BC6E6`, `0x005BC70E`, and
`0x005BCC90` satisfy a raw BL bit-pattern decoder but are VFP/other 32-bit
instruction encodings, not calls. Their exact bytes are pinned in the closure
manifest and analyzer. No direct BL or `B.W` reaches a strict body interior.

The ULED manager owns a separate 68-byte operations object at
`[0x0070AFE0,0x0070B024)`, SHA-256
`ec5c1f936d6fb6967cd8ec6c2f5756de67e17c4c872bd20b8ae5ce16fa73304a`.
It contains panel ID zero, 15 intentional odd Thumb pointers to Hongshi
entries, and final capability word one. The adjacent retained path belongs to
`driver\uled\drv_mspi_uled.c`, so this dispatch object is manager-owned and
excluded from the panel object's physical interval.

An exhaustive bytewise scan found two strict-interior-looking values at odd
byte offsets `0x00643447` and `0x00644B47`. They are overlapping byte windows,
not aligned pointers. After those qualifications, stored or direct
strict-interior ingress is zero.

## Common-driver request ABI

The driver uses four immutable 28-byte request templates at `0x0076B12C`,
`0x0076B148`, `0x0076B164`, and `0x0076B180`; their concatenated SHA-256 is
`e25b08f08ee39a2376c7d8eb46f5e2fe9aa06549d735624fe6a10beecb413549`.
Five calls cross into the separately closed common MSPI object:
initialization, serial write, serial read, asynchronous QSPI write, and the
status-preamble write.

The panel-owned live state is:

| Address | Meaning |
|---:|---|
| `0x20074510` | published MSPI handle |
| `0x20074514` | framebuffer base |
| `0x20074518` | optional clear callback |
| `0x2007451C` | three-byte register-command scratch |
| `0x20074520` | brightness state/context |
| `0x2007501A` | conditional offset-mode flag |
| `0x20074130` | eight-byte status-preamble buffer |

The exact common request and HAL-transfer layouts are documented in
`g2-uled-mspi-common-recovery.md`.

## Configuration and display behavior

The panel is 640 by 480 pixels with packed four-bit pixels, hence 320 bytes per
scanline. Partial refresh caps the requested end coordinates at 639 and 479;
the asynchronous path submits the packed framebuffer through the dedicated
request template.

Configuration interprets the exact 50-byte stream at
`[0x00728ED8,0x00728F0A)`, whose SHA-256 is
`817aab4e4b6763d2f1eccc26599caad6d867a3e42a8e6d4ac1f16fbcb3e96e13`.
Ordinary triples select bank/register/value; `0xFF` markers delay and `0xEE`
markers exercise the timer path. The routine then probes panel registers,
clears the framebuffer, applies brightness, and programs offsets.

Offsets saturate X and Y at 16. If `0x2007501A` is nonzero and the BLE state is
two, X is first increased by five. Registers `EF` and `F0` are updated while
preserving their high bits, and each update is latched by writes `D9=BF` then
`D9=FF`.

Brightness below two maps to five; values 2 through 100 use
`(input * 250 - 451) / 98 + 5`; values above 100 map to 255. The routine
combines stored/user brightness with the side-specific adjustment and writes
register `E2`. The exported six-bit-current function merely masks its input
and returns zero, and the four-byte set-mode function is also an intentional
no-op returning zero.

## Identity and recovery protocol

Chip identification reads bank-zero register `0x06`, accepts value `0x01`,
then enters the serial-number sequence. That sequence selects banks through
registers `65..67/64` and reads registers `6C..6F`; the stock diagnostic path
collects 19 bytes.

Status checking first writes the exact preamble `02 00 2A 00 00 00 01 DF`
from `[0x0078D484,0x0078D48C)`. Register `BE` must equal `0x84`; register
`62` must equal `0x77` or `0x57`; and mirror register `D8` must have bit `0x20`
set. A mismatch invokes the power-down, power-up, reconfigure, redraw, and
brightness-restoration sequence.

## Reconstruction boundary

No authenticated historical Hongshi/A6N-G source is available, so no license
or whole-source identity is inferred. The current evidence pins the complete
linked object, dispatch roots, request templates, configuration stream,
status preamble, runtime globals, common-driver seam, and panel protocol. No
Hongshi source appears in `overlay.json`; the stock package retains all 5,720
bytes and OpenCFW claims zero production ownership.

Run the fail-closed audit and focused tests with:

```sh
python3 tools/analyze_g2_uled_a6ng.py
python3 -m unittest tests.test_analyze_g2_uled_a6ng
```

The analyzer pins all three manifests, official image identity, every body
and non-code region, retained path and diagnostics, BL and stored-pointer
closure, VFP/unaligned-overlap qualifications, operations object, templates,
configuration/status bytes, display contract, and absent production routing.
