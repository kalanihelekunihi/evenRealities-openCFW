# G2 common ULED MSPI recovery

Status: complete linked-object census and ABI/behavior characterization;
clean-room implementation and production routing pending. Run addresses use
`run = file_offset + 0x00437FE0`.

## Result

The retained first-party path
`driver\uled\drv_mspi_uled_common.c` owns 13 linked bodies at
`[0x0059C820,0x0059D156)` and the alignment/literal region
`[0x0059D156,0x0059D244)`. The bodies total 2,358 bytes with SHA-256
`752affeb25a07c832350240ee0ebcdf783cd329b52c6139a9cceb8b6d10fdc71`.
The 238-byte pool has SHA-256
`eb8d630ca20548c42d3d8fdf0fe168e8c0daecfc331e33334460de56d247ff14`.
The complete 2,596-byte physical object has SHA-256
`0429d9a36a81cb2442d958e6c6663e94115aeea1b0f83c95ec01e3d15e2ec836`.

The source boundary starts with compiler-emitted CMSIS `NVIC_EnableIRQ` and
`NVIC_SetPriority` helpers. The preceding function ends at `0x0059C81C` and
belongs to the panel-specific object; the next object begins at `0x0059D244`.
The retained path and every diagnostic literal are in this object's common
pool.

## Linked surface

| Function | Stock span | Bytes | Identification |
|---|---:|---:|---|
| `NVIC_EnableIRQ` | `[0x59C820,0x59C83E)` | 30 | exact CMSIS register semantics |
| `NVIC_SetPriority` | `[0x59C83E,0x59C866)` | 40 | exact CMSIS register semantics |
| transfer callback | `[0x59C866,0x59C876)` | 16 | stored callback and semaphore behavior |
| `am_devices_mspi_device_reconfigure` | `[0x59C876,0x59C980)` | 266 | retained function string |
| `am_devices_mspi_set_serail_mode` | `[0x59C980,0x59CA2C)` | 172 | retained spelling and function string |
| `am_devices_mspi_set_quad_mode` | `[0x59CA2C,0x59CAFC)` | 208 | retained function string |
| transfer builder | `[0x59CAFC,0x59CB42)` | 70 | exact descriptor mapping |
| `uled_rw_param_validate` | `[0x59CB42,0x59CC40)` | 254 | retained function string |
| `am_devices_mspi_read` | `[0x59CC40,0x59CCDC)` | 156 | retained function string |
| `am_devices_mspi_write` | `[0x59CCDC,0x59CD86)` | 170 | retained function string |
| `am_devices_mspi_qspi_write` | `[0x59CD86,0x59CE1E)` | 152 | retained function string |
| `am_devices_mspi_qspi_write_async` | `[0x59CE1E,0x59CF1A)` | 252 | retained function string |
| `am_devices_mspi_init` | `[0x59CF1A,0x59D156)` | 572 | retained function string |

The function-map manifest pins each full body and hash.

## Ingress closure

Thirty direct BL sites reach exact entries: 19 inside the object and 11 from
the two panel-specific ULED drivers. The exterior sites are:

```text
5926A8 -> 59CF1A    592716 -> 59CCDC    592754 -> 59CD86
592786 -> 59CC40    5927BE -> 59CC40    592E2A -> 59CE1E
5BBD98 -> 59CF1A    5BBE36 -> 59CCDC    5BBE78 -> 59CC40
5BCDD4 -> 59CE1E    5BD03C -> 59CCDC
```

The 151 direct body calls include all internal edges, Ambiq HAL operations,
CMSIS-RTOS semaphore calls, cache cleaning, and diagnostics. The sole stored
entry is the intentional Thumb callback word `0x0059C867` at `0x0059D200`.
No direct BL or `B.W` targets a strict body interior. Two raw interior-looking
32-bit values start at odd byte offsets `0x005119B7` and `0x0059D5C7`; neither
is an aligned pointer or executable ingress.

## Request and transfer ABI

The public request object is 28 bytes. Its established fields are:

| Offset | Meaning |
|---:|---|
| `+0x00` | device/direction byte copied into HAL transfer `+0x07` |
| `+0x04` | transfer count/length |
| `+0x08` | command byte |
| `+0x0C` | instruction/address word |
| `+0x10` | instruction-length byte |
| `+0x14` | data pointer |
| `+0x18` | live MSPI handle |

The transfer builder zeroes a 24-byte HAL transfer descriptor, then writes the
instruction at `+0x00`, instruction length at `+0x04`, read/write selector at
`+0x06`, source device byte at `+0x07`, count at `+0x08`, command at `+0x0C`,
an eight-bit length derivative at `+0x0E`, and data pointer at `+0x14`.

Validation rejects a null request, handle, or data pointer and otherwise
returns zero. This exactly explains the three retained diagnostics.

## Mode and transfer behavior

`am_devices_mspi_device_reconfigure` disables the active device, applies a new
device configuration, re-enables MSPI, and reapplies the associated pin
configuration. Any failure is diagnosed and collapsed to `-1`.

The serial and quad helpers both use HAL control request `0x18`. Serial mode
clears the low mode byte in the supplied configuration. Quad mode clones its
24-byte template and sets the mode byte to `0x10` before reconfiguration.

- read: switch to serial, issue a blocking transfer with a 1,000,000-unit
  timeout, then restore quad mode;
- write: switch to serial, clean the data range from pointer/length, issue the
  blocking transfer, then restore quad mode;
- QSPI write: switch to quad, issue the blocking transfer, then restore serial;
- asynchronous QSPI write: switch to quad, enable and clear interrupt mask
  `0x1A80`, clean the range, submit a nonblocking transfer, wait up to 3,000 ms
  for the callback semaphore, then restore serial mode.

The callback stores completion status through context `0x200007EC` and
releases semaphore `0x20074534`. Its only stored code pointer is the pool word
identified above.

## Initialization

Initialization records the serial and quad configuration pointers at
`0x20074538` and `0x2007453C`, creates a binary semaphore with initial count
zero, initializes MSPI module zero, powers it on, applies controller and serial
device configuration, enables it, enables/clears mask `0x1A80`, sets IRQ 20 to
priority four, enables that IRQ, and finally applies the product power-control
transition. On success it publishes the HAL handle; each checked failure
returns `-1`.

## Reconstruction boundary

The historical first-party source is unavailable. The Ambiq HAL and CMSIS
interfaces establish provider and register semantics, but they do not supply
the common driver itself. Both panel consumers are now closed separately in
`g2-uled-jbd4010-recovery.md` and `g2-uled-a6ng-recovery.md`, including all 11
exterior calls and both request-template families. A clean-room implementation
still requires independently named provider bindings and product-specific HAL
control validation. No source in `overlay.json` owns this object, so
production ownership remains zero.

The higher-level selector and both operations-record layouts are closed in
`g2-uled-manager-recovery.md`; together these four audits account for all 11
panel-to-common calls and both panel dispatch records.

Run the fail-closed audit and focused tests with:

```sh
python3 tools/analyze_g2_uled_mspi_common.py
python3 -m unittest tests.test_analyze_g2_uled_mspi_common
```

The analyzer pins all bodies, the physical pool, retained strings and path,
literal globals, direct calls, exterior roots, callback word, raw overlap
qualifications, and absent production routing.
