# YHM2710 complete source-reduction correlation

## Result

All 44 functions classified as `yhmicros_yhm2710_candidate` are now represented by the
transparent C module in `reconstructed/yhm2710/`. The module is independently reconstructed
from the byte-exact application image and is not YHMICROS or Even Realities source. This
reduction is authorized by the repository owner's 2026-08-14 full-reduction policy in
`SOURCE-ADMISSION.md`; the unavailable vendor package is evidence only and is not a build input.

The reconstruction has no firmware blob, binary library, generated object, lookup-table image,
or opaque callback. GPIO, locking, delay, and completion hooks are typed board/RTOS ports. The
portable module is built and tested on the host, under ASan/UBSan, as freestanding Cortex-M4F
objects, and as an nRF5 SDK application translation unit.

## Exact stock closure

The recovered closure is split into the following observable roles:

| Stock entries | Functions | Reconstructed behavior |
| --- | ---: | --- |
| `0x00028BB0`, `0x00028C6C` | 2 | seven-bit command framing, read/write selector, byte transfer, XOR-parity validation |
| `0x00035698`, `0x00056568`, `0x0005657C`, `0x00056590`, `0x0005660C` | 5 | nine-attempt retry, lifecycle flag, exact generic-device adapter status codes and failed-read `0xFF` fill |
| `0x0005CBE4`, `0x0005CC68`, `0x0005CC8C`, `0x0005CCCC`, `0x00087B30`, `0x000968A8`, `0x000969EC` | 7 | 52/13-count pulse encoding, MSB-first bit writing, recovery/idle waveforms, bounded edge sampling, parity and adapter |
| `0x0003510C`, `0x0003530C` | 2 | chip-ID `0xA0` validation and exact five-register initialization sequence |
| `0x00035272`, `0x0003529A` | 2 | register-6 high-nibble status decode and charge-state mapping |
| `0x00035268`, `0x00050748` | 2 | register-9 one-byte read and its branch-only public veneer |
| `0x0003540C`, `0x00035412`, `0x00035760`, `0x00035766` | 4 | typed register read/write and one-byte wrappers |
| `0x000507CC`, `0x00050804` | 2 | complete register read/write dispatch bodies behind the public veneers |
| `0x0003541C`, `0x00050608`, `0x000507A0`, `0x000507AC` | 4 | status-line readiness, lock/release, and completion seams |
| `0x00035508` | 1 | eight-code minimum-distance float ladder with strict-less tie behavior and register-1 upper-field update |
| `0x00035594`, `0x000355A8`, `0x000355BC`, `0x00035684` | 4 | register-2 `0x28`/`0xA8`, register-1 bit-1, and register-2 `0xF8` updates |
| `0x0003543C`, `0x0005074C` | 2 | register-1 bit-1 clear and its branch-only public veneer |
| `0x000350E0`, `0x00050614` | 2 | register-3 charging-event mask update and its branch-only public veneer |
| `0x0005C0FA` | 1 | bounded 209-iteration transport delay |
| `0x0004E9E8`, `0x00050618`, `0x00050750`, `0x0005079C`, `0x00050848` | 5 | pure thunks folded into their typed target functions |

The separate 18-byte `device_stacmd` operation-table binding at `0x000565F4` remains an R1
configuration adapter and is not counted among the 44 provider entries.

Every transport extent and digest is checked by `tools/evidence/summarize_r1_pmic_transport.py`.
The remaining register-policy bodies are checked by the sub-32, 64...127, and 128...202 frontier
summaries plus the named-peripheral digest assertions in `tools/verify_openr1.py`. The generated
ownership ledger assigns all 44 entries
`clean_room_reimplementation_owner_authorized`.

The four added exact starts correct two more legacy noncontiguous Ghidra spans. The direct targets
`0x00035268..<0x00035272` and `0x0003543C..<0x000354A6` have complete tail-call/return boundaries;
their public veneers `0x00050748..<0x0005074C` and `0x0005074C..<0x00050750` are independent
branch-only entries. Their respective body SHA-256 values are
`a642dcfe0dd3a0884d462a09171a1b5ca23c92bc8a304dbae98b2241aef81b7f`,
`aa85adc0508a08b2c558b27437b8d4c357a79494d8df700e071b1c84855777e6`,
`f84e786095a70e3d5a0a9663f8aaee5f065bbae0dea2a0de2de68f171b3d67ee`, and
`051ec761f5abafb4d2b8b922c11c2a6ba681a1de4b861649692f2de6ed2b4ad1`.

Four further Ghidra-omitted entries close the complete register dispatch bodies
and the register-3 charging-event policy. Their byte extents, call topology,
digests, and transparent implementation are pinned in
[`YHM2710-OMITTED-TRANSPORT-ENTRIES-CORRELATION.md`](YHM2710-OMITTED-TRANSPORT-ENTRIES-CORRELATION.md).

## Recovered contract

- single-wire status/command GPIO: absolute pin 33 (`P1.01`);
- command accepted only when bit 6 is set; header `(command & 0xF0) + register`;
- seven header bits followed by a read (`1`) or write (`0`) selector pulse;
- eight data bits MSB first and XOR parity over each byte;
- read responses drive parity after every byte except the final byte;
- bit one and zero use the same edges with recovered 52 and 13 us delays;
- recovery/idle use the recovered 209 us delay primitive; the stock GPIO
  callback is the Nordic `nrf_delay_us` veneer that scales its argument by 64
  core cycles;
- falling and rising edges are each bounded to 1,000 samples;
- adapter retries number 1 through 9 (the prior “ten attempt” prose was corrected);
- chip ID is register 8 and must equal `0xA0`;
- initialization writes `(reg,value)` `(2,01)`, `(0,6A)`, `(1,4C)`, `(2,A0)`, `(3,02)`;
- register-1 ladder scale is `20.080322265625`, with multipliers
  `{0.5,0.2,0.7,0.9,1.0,1.5,2.0,3.0}` and earlier-index tie preference.

## Intentional hardening

Stock code relies on populated registry records and asynchronous RTOS objects. The reconstruction
uses explicit typed bindings, rejects null/unbound requests, propagates transport failures, bounds
all lengths, and makes locking/completion dependencies visible. These guards prevent stock-style
null vtable faults without changing successful wire or register outcomes. Physical pulse timing,
electrical compatibility, shared-conductor arbitration, and installed-part behavior still require
validation on an owned ring before the module is selected by the production board runtime.
