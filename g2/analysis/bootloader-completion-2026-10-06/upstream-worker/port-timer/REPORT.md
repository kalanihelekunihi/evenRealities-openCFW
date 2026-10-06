# Bootloader port timer startup recovery

## Outcome

The new source component exports `opencfw_bl_port_timer_configure()` and
reconstructs each requested callee as linkable C helpers in
`g2/components/bootloader/port_timer/port_timer.c`. The ARM test link includes
only test-only `clock_request`/`clock_release` stubs. The differential runner
intercepts those calls on both stock and source paths and compares their exact
arguments. The external services remain required in a full source link.

`make test` passes 28 original/source cases and reaches all bytes in each
tested function body: the 88-byte configure function, 10-byte OR helper,
36-byte NVIC priority helper, 28-byte NVIC enable helper, 152-byte clock
configuration helper, 28-byte triple-read timer helper, and 108-byte compare
helper. The same run covers all 24 bytes of the clock-source mapping leaf,
28 bytes of the interrupt-protected triple-read primitive, and 8 bytes of the
PRIMASK save helper. Overall the trace contains 510 distinct stock instruction
bytes; the clock-manager request/release targets are intentionally intercepted
before executing their separate implementations.

Run `make test` in this directory. It compiles a freestanding Cortex-M33
Thumb/soft-float test ELF with Clang and local GNU ARM binutils, selects the
Unicorn M33 model before mapping, and runs the locked stock image and compiled
source against matching synthetic register state.

## Recovered addresses and effects

The tested reference is
`g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin`, SHA-256
`f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5`. Function
ranges and SHA-256 values in `out/comparison.json` are cross-checked against
Ghidra's `functions-000.jsonl` and the authenticated image bytes:

| Stock range | Bytes | Function behavior |
|---|---:|---|
| `0x0041b6fa..0x0041b752` | 88 | Startup configure sequence |
| `0x0041f4ac..0x0041f4b6` | 10 | OR a supplied mask into `0x40008900` |
| `0x0041b64c..0x0041b670` | 36 | Write shifted priority byte through the NVIC priority base |
| `0x0041b614..0x0041b630` | 28 | Write an enable bit through NVIC ISER for nonnegative signed-16 interrupt IDs |
| `0x0041f358..0x0041f3f0` | 152 | Update STCFG, request/release mapped clock classes, set ready byte |
| `0x0041f424..0x0041f440` | 28 | Save PRIMASK, read STTMR three times, restore PRIMASK and select a sample |
| `0x0041f440..0x0041f4ac` | 108 | Poll against compare shadow, compute/write compare, refresh shadow under PRIMASK |

The configure function writes the raw value `0x20` to `0x20027124`, computes
`0xffffffff / value - 4` into `0x20027128`, sets bit 0 at `0x40008900`, writes
`0xf0` to NVIC priority byte `0xe000e420`, and writes bit 0 to ISER word
`0xe000e104`. It requests STIMER clock setup through the recovered clock
helper, saves a STTMR sample at `0x20027120`, configures compare index 0 with
the raw `0x20` argument, then applies `(old_STCFG & 0x7ffffff0) | 0x103`.
The configure function's stock epilogue returns the incoming R3 value in R0;
the source preserves that behavior, and callers should ignore the result.

The compare helper first samples STTMR. For valid IDs below 8, it repeats the
sample only while the sampled count equals the compare-shadow entry or that
entry plus one. Under PRIMASK it samples again and, when `(now - start) + 3 <
delta`, writes `start + (delta - now) - 3` to the requested hardware compare
register; otherwise it writes 1 and returns `0x08000000`. It then records one
more sample in the software compare-shadow table at `0x200001c8` and restores
the saved PRIMASK. Invalid IDs return 5 after the initial sample.

The helper’s mapping leaf converts selectors 1 and 2 to clock class 4, selector
6 to class 0, and other selectors to class 7. `clock_request` and
`clock_release` receive the selected class and second argument `0x32`. Test
fixtures confirm calls such as `(7, 50)` and `(4, 50)` but intercept the
providers before their implementation. Their stock entry points are
`0x004222f0` and `0x00422364`, respectively.

## SDK correspondence and boundary

The local public source candidate is pinned at gitlink
`third-party/upstream/ambiqhal-apollo510` commit
`5efc0228528a8adce5eae0d226fac85d2551eb3b`; its release marker is
`release_sdk5p1p0-366b80e084`. Its Apollo510 CMSIS header confirms
`STIMER_BASE == 0x40008800`, `STTMR` at offset `+4`, and `SCMPR0` at `+0x20`.
`am_hal_stimer.h` declares public STIMER configuration and compare APIs and
documents a minimum compare delta of 4. The pinned closure contains no
`am_hal_stimer.c` implementation. The bootloader uses a custom private port
sequence with its own global state and compare scheduling; no exact public
translation-unit implementation was identified or copied.

The same public clock-manager header declares `AM_HAL_CLKMGR_USER_ID_STIMER`
at numeric 50 (`0x32`), which matches the second argument observed at the
bootloader's private clock request/release call sites. Its public clock enum
and available source do not establish the semantics of private selector
classes 0, 4, or 7. The component therefore leaves `clock_request()` and
`clock_release()` as named external providers rather than binding guessed
public enum conversions. The exact remaining link cut is those two services;
their test stubs return zero and have no hardware side effects.

The test uses a deterministic synthetic STTMR read hook, synthetic STIMER/NVIC
register memory, and intercepted clock services. It proves source-vs-stock
state and call-argument agreement for those fixtures. It does not simulate
wall-clock progress, interrupt delivery, clock stability, compare events, or
silicon MMIO behavior. No frequency or milliseconds interpretation is
assigned to raw `0x20`; runtime clock selection and delta semantics still
require the real clock-manager providers and hardware measurements. The
freestanding test build also does not claim the original IAR compiler bytes or
full firmware byte identity.
