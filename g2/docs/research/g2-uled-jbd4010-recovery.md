# G2 JBD4010 ULED driver recovery

Status: complete linked-object census and protocol/ABI characterization;
historical source, clean-room implementation, and production routing pending.
Run addresses use `run = file_offset + 0x00437FE0`.

## Result

The retained first-party path
`driver\uled\jbd4010\drv_mspi_jbd4010.c` owns the physical interval
`[0x00592658,0x005939A0)`. Its 24 linked bodies contribute 4,588 bytes with
SHA-256
`282897dacb6bac34ce77cfa56e28ebdefc318589bfb1363c753e7c86d418d83a`;
eight alignment/literal regions contribute the remaining 348 bytes with
SHA-256
`9383f55824c401b734170954caf85267a6a55a26a47b64a8406b803e93c8f258`.
The complete 4,936-byte object has SHA-256
`0dc52441e3eb2272fc97972eee102f01a3d3e9f59499e4708d8f95be565e5391`.

Five real Thumb entries at `0x00592658`, `0x00592680`, `0x0059308C`,
`0x00593334`, and `0x00593750` were absent from the discovered-function set.
Raw prologue-to-return disassembly, source order, exact callers, retained
diagnostics, and the external callback table recover them without treating
literal data as code.

## Linked surface

The exact per-body boundaries and hashes are pinned in
`tools/manifests/g2-uled-jbd4010-function-map.tsv`. In source order the linked
surface is:

| Group | Functions |
|---|---|
| lifecycle | `am_devices_mspi_jbd4010_term`, `am_devices_mspi_jbd4010_init`, `jbd4010_vtable_init` |
| transport helpers | `jbd4010_write_command`, `jbd4010_write_data_block`, `jbd4010_read_response`, `jbd4010_read_die_response` |
| configuration | `am_devices_mspi_jbd4010_configure`, `am_devices_jbd4010_set_display_offset`, `jbd4010_configure_gpio_pins` |
| refresh and display control | blocking and asynchronous `QSPI_PartialReflash`, `setBrightness`, `clear_display`, `set_current_6bit` |
| identification | `read_chipId`, `read_dieId` |
| power and recovery | `power_off_sequence`, `power_on_sequence`, `jdb4010_status_check`, `jdb4010_status_recovery`, `standby_mode`, `status_check_and_recovery` |
| mode control | `am_devices_jbd4010_set_mode` |

Several helper labels are descriptive clean-room names. Exact names are used
only where retained strings or current authenticated behavior establish them;
the historical decompilation listed in the provenance manifest is semantic
corroboration, not a redistribution source or whole-source identity claim.
Because the historical source inventory is unavailable, the linked-object
census is complete but the number of source-only functions is unknown.

## Ingress and ownership closure

Seventy-seven direct BL sites reach exact function entries: 75 are internal
and two are external (`0x0057E5CC -> 0x0059308C` and
`0x0057E610 -> 0x00592F9A`). The bodies contain 289 direct calls in total.
No direct BL or `B.W` reaches a strict body interior.

The ULED manager owns a separate 64-byte operations object at
`[0x0070B024,0x0070B064)`, SHA-256
`7eecc0a32f95c8d1d712327198d4b473a7f065eeb1c2e8132f98526debef4418`.
Its first 14 words are intentional odd Thumb pointers to JBD4010 entries and
its final two words are zero. The adjacent retained source path belongs to
`driver\uled\drv_mspi_uled.c`, so the object is manager-owned and is not
included in the JBD4010 physical interval.

An exhaustive bytewise value scan found seven strict-interior-looking windows.
Five begin at odd byte offsets. The remaining two aligned words lie inside the
packed ASCII block `W0`, `W0X`, `W0Y`, `W1`, `W1X`, `W1Y` at
`[0x0078F388,0x0078F3A0)`. None is executable ingress. After these
qualifications, stored or direct strict-interior ingress is zero.

## Common-driver request ABI

The panel object uses four immutable 28-byte request templates at
`0x0076B244`, `0x0076B260`, `0x0076B27C`, and `0x0076B298`; their concatenated
SHA-256 is
`568d17202d90a57a652a07e99cce0780372261cc61910ade92ededad20a2e015`.
The word templates are respectively:

```text
{0,0,1,0,0,0,0}
{0,0,1,0,0,0,0}
{0,0,1,0,1,0,0}
{1,0,1,0,1,0,0}
```

Six calls cross into the separately closed common MSPI object: initialization,
serial write, blocking QSPI write, two reads, and asynchronous QSPI write.
The panel-owned live state is:

| Address | Meaning |
|---:|---|
| `0x20074524` | published MSPI handle |
| `0x20074528` | framebuffer base |
| `0x2007452C` | optional clear callback |
| `0x2007501A` | conditional offset-mode flag |

The exact common request and HAL-transfer layouts are documented in
`g2-uled-mspi-common-recovery.md`.

## Display and protocol behavior

The panel is 640 by 480 pixels with packed four-bit pixels, hence 320 bytes per
scanline. Partial refresh validates the requested region and writes each
half-byte scanline; the asynchronous path submits a full-frame transfer and
latches it with command `0x97`.

Display offsets are constrained to X `2..22` and Y `2..18`. When the flag at
`0x2007501A` is set and the BLE connection state equals two, the driver adds
five to X before programming the panel. The configuration, brightness,
standby, and recovery flows use the observed command family `0x66`, `0x99`,
`0x06`, `0x01`, `0xC0`, `0x97`, `0x73`, `0x36`, `0x46`, `0x31`, `0xA3`, and
`0xA9`.

Chip identification issues command `0x9F` and returns two bytes. Die
identification issues command `0x81` through the alternate request template
and returns 12 bytes. Status checking reads registers `0x05` and `0x35`;
failure recovery power-cycles, reconfigures, redraws, and restores brightness.
Mode control accepts only `0x71`, `0x72`, `0x73`, and `0x74`.

## Reconstruction boundary

No authenticated historical JBD4010 source is available, so no license or
whole-source identity is inferred. The current evidence is sufficient to pin
the complete linked object, its external dispatch roots, protocol constants,
request templates, globals, and common-driver seam, but not to promote a
source candidate safely. No JBD4010 source appears in `overlay.json`; the
stock package retains all 4,936 bytes and OpenCFW claims zero production
ownership.

Run the fail-closed audit and focused tests with:

```sh
python3 tools/analyze_g2_uled_jbd4010.py
python3 -m unittest tests.test_analyze_g2_uled_jbd4010
```

The analyzer pins the three manifests, official image identity, every body and
non-code region, retained path and diagnostics, BL and stored-pointer closure,
the packed-ASCII collision qualification, request templates, manager-owned
operations object, runtime globals, display contract, and absent production
routing.
