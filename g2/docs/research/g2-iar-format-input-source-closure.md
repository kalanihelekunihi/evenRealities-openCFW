# G2 IAR formatted-input source closure

Status: software-complete for the production-reachable non-secure string-input
route; on-device validation blocked by unavailable authorized responsive G2
hardware. This result does **not** close formatted output or claim Annex-K
`scanf_s`/`printf_s` behavior.

## Result

The only stock caller of the IAR scanf core is the already source-owned
string wrapper. That wrapper always passes `secure = 0`. The stock core at
`0x004D1638` is now protected by its exact 2,778-byte SHA-256 guard and
redirected to `open_cfw_runtime_iar_scanf_core`. The adapter imports the IAR
variadic cursor and enters a freestanding C scanner; it does not call or copy
the proprietary DLIB body.

The production scanner implements:

- literal and whitespace matching, assignment suppression, field widths,
  `%n`, and `hh`/`h`/`l`/`ll`/`j`/`z`/`t`/`L` length handling;
- signed, unsigned, octal, hexadecimal, base-detecting, and pointer input;
- `%c`, `%s`, and normal/inverted scansets using the independently qualified
  stock scanset-table contract;
- decimal and hexadecimal floating input, exponents, `inf`/`infinity`, and
  `nan` payload consumption;
- parse-time field-width enforcement, including rollback of an incomplete
  exponent marker; and
- exact ARM-EABI double-operation providers for the Apollo510 FPv5-D16
  target, leaving the freestanding target objects with no unresolved runtime
  dependency beyond the five explicitly source-owned providers.

The source is ordinary compilable C in
`components/shared/runtime/runtime_format_scan.c` and
`components/shared/runtime/runtime_aeabi_double.c`; no generated instruction
payload or imported IAR object is used.

## Production placement

The canonical Apple-clang profile appends eleven leaves:

| Leaf | Overlay offset | Bytes |
| --- | ---: | ---: |
| `__aeabi_dadd` | 399,292 | 18 |
| `__aeabi_dmul` | 399,312 | 18 |
| `__aeabi_ddiv` | 399,332 | 18 |
| `__aeabi_ui2d` | 399,352 | 14 |
| `__aeabi_d2f` | 399,368 | 14 |
| `open_cfw_runtime_strtod_bounded` | 399,388 | 2,696 |
| `open_cfw_runtime_strtod` | 402,084 | 10 |
| `open_cfw_runtime_scanset_match` | 402,096 | 126 |
| `open_cfw_runtime_vsscanf` | 402,224 | 2,530 |
| `open_cfw_runtime_sscanf` | 404,756 | 28 |
| `open_cfw_runtime_iar_scanf_core` | 404,784 | 12 |

All cross-leaf calls use strict relocation contracts. The manifest owns the
5,504-byte aggregate at application file offset 3,922,688 / runtime address
`0x007F5AE0`. Canonical artifact identities are:

- overlay: 404,796 bytes,
  `a55b20ca90792f195ef8de456a6cb7d90c831575b9aff147676a716844bfc73d`;
- Apollo component: 3,928,192 bytes,
  `5979e515c76aa1601701a01e9c0aa1050a7cc0708d0b7470b94c3d6aac0c9a73`;
- complete EVENOTA package: 4,706,686 bytes,
  `30afcda8c32cc34fb1a1c12df13aff2f97223e12d74425690e67a6e4d81bfddf`;
- flash plan: 4,071,097 bytes,
  `cf46c2b6e6ed099ce9ef240520be8d81847ae219d52479286a373c326d22da6d`,
  with 5,863 placed, 2 unresolved, 5 container-only, and 6 protected regions.

## Verification and limits

Run `make iar-format-input-closure`. The gate rebuilds the complete source
package, exercises host behavior, compiles both sources freestanding for
Thumb, replays the independent scanset oracle, and checks production
placement, redirect, manifest, package, and flash-plan identities.

No device was accessed, signed, installed, or flashed. Execution through the
physical IAR wrapper ABI, SRAM state, and real application call sites cannot
be validated because the authorized right temple is nonresponsive and no
other authorized modifiable G2 is available. The left temple remains stock.
That physical evidence is therefore an explicit hardware-validation block,
not a software-completeness exception.

The input adapter deliberately ignores the dormant `secure` parameter
because the sole reachable wrapper passes zero. Annex-K size arguments,
constraint dispatch, and secure diagnostics remain part of the formatted-I/O
software gap until they are either implemented and routed or proven wholly
unreachable across every output and input ingress. Formatted-output ABI
wrappers and the formatter core are also still open.
