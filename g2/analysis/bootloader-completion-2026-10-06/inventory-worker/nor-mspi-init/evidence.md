# MSPI initializer source slice

This component implements `opencfw_provider_420254`, the MSPI constructor
called by the NOR initializer, and the directly called module-state helper
`0x424a5a`. The emitted source symbol `opencfw_provider_420254` can be linked
at the parent call site without a thunk.

## Locked reference and range identity

- Blob: `g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin`
- SHA-256: `f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5`
- Load base: `0x00410000`; file offset is virtual address minus the base.
- Full initializer control-flow range: `[0x420254,0x420476)`, 546 bytes.
- Handle constructor: `[0x424a5a,0x424aea)`, 144 bytes.
- Exact bytes and SHA-256 values are in `original-ranges.json`; disassembly is
  in `original-disassembly.txt`.

The Ghidra export also labels `0x42029a` as `boot_mspi_initialize`; raw control
flow falls through that address from `0x420254` and returns through the shared
epilogue at `0x420470..0x420476`. The implementation and fixture therefore
follow executed instruction flow rather than treating the fallthrough label
as an independent call.

## Recovered data and state contract

The `0x420254` entry receives `(module, device_config, current_device_out,
reserved)`. Its caller supplies `(1, 0, 0x200270d8, unspecified)`. The reserved
fourth word is not consumed. The single device-slot record begins at
`0x20026fd0`; a nonzero byte at `+0x0c` causes immediate return `0xffffffff`.

The internal handle constructor uses state base `0x2001caa0` and stride
`0x8d0`. It initializes the module handle and stores its address through the
fixed handle slot `0x200270dc`. Its statuses are `5` for module `>= 4`, `6`
for null handle output, and `7` when the module's initialization bit is
already set. The initialized handle for module 1 is `0x2001d370`.

The general MSPI configure record passed to `0x424af0` is exactly 12 bytes:

| Offset | Value | Meaning supported by the Apollo510 HAL header |
| --- | --- | --- |
| `+0` | `0x100` | TCB size in words |
| `+4` | `0x200f4c00` | TCB pointer |
| `+8` | `0` | `bClkonD4` false |
| `+9..+11` | `0` | zero padding from the local initialization |

The device configuration is the caller-provided pointer when nonzero, otherwise
`0x20000224`. On successful registration, the record at `0x20026fd0` receives
module number, one mode byte, handle pointer, and active byte. For the default
device case, that mode byte is read from `0x2000020c + 8`; the firmware uses
this separate source address from the device-configuration pointer.
`0x200270d8` is set to `0x20026fd0` only after the interrupt setup succeeds.

## Error behavior and providers left outside this source

After handle construction, the source calls power-control `(handle,0,0)`.
Failure logs line `0x22a` and returns `1`. General configure failure logs
`0x233`, deinitializes, and returns the HAL status; device-configure failure
logs `0x23f`, deinitializes, and returns its status; enable failure logs
`0x246`, deinitializes, and returns its status. Interrupt-clear failure returns
`1` without a log or deinitialize call. Interrupt-enable failure logs `0x269`
and returns `1`. Success configures interrupt 21 at priority 4, unmasks it,
initializes the IRQ guard, publishes the record, logs line `0x27a`, and returns
zero.

The source leaves these exact-address providers explicit: power-control
`0x426808`, base configure `0x424af0`, device configure `0x424be4`, enable
`0x425066`, deinitialize `0x42516c`, interrupt clear/enable `0x426506` and
`0x426450`, XIP/control update `0x41ff34`, mode publication `0x41fadc`,
register-ID read `0x41d90e`, interrupt priority/unmask `0x41fdde` and
`0x41fdc0`, IRQ guard `0x41b8e0`, and logger `0x4176ce`. Their tested callbacks
are synthetic; they do not exercise MMIO or physical interrupts.

The exact Apollo510 public HAL header in
`../upstream-worker/ambiqhal-apollo510/ambiqhal/mcu/apollo510/hal/mcu/am_hal_mspi.h`
defines `am_hal_mspi_config_t` fields as TCB word count, TCB pointer, and
`bClkonD4`; this directly supports the 12-byte configuration layout used by
the candidate. The hardware-specific implementation providers above remain
separate from that layout recovery.

## Validation

`make -C g2/components/bootloader/nor_mspi_init all` builds the ARM Cortex-M4
source module. The original/source Unicorn comparison passes 13 cases across
default and custom device configuration, occupied slot, module-state errors,
power/configure/device-configure/enable failures, interrupt failures, and
direct helper null-output/success paths. It compares returned status, ordered
provider/log events, the full initialized module-state object, the device
record, current-device slot, and handle slot. The original trace covers 690
distinct bytes: the full 546-byte initializer range plus all 144 bytes of the
constructor range. The saved, source-hashed result is
`nor-mspi-init-comparison.json`.

No MSPI hardware, DMA, clock, interrupt controller, or flash is exercised; the
source module is not a bootable image and does not claim byte-identical rebuild.
