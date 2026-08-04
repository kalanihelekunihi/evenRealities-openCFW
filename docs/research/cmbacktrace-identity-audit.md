# CmBacktrace identity and isolation audit

Status: research-only identification. No production overlay, manifest, release
pin, shared coverage document, or firmware artifact changed. Run addresses use
the confirmed load base `run = file_offset + 0x00437FE0`.

Scope: identify and isolate the last remaining vendored third-party component
in the G2 `2.2.6.10` Apollo-main image, so the third-party inventory is
complete before first-party functionality is addressed.

## Identity — armink CmBacktrace (definitive)

| Evidence | Run address / value |
|---|---|
| Vendored path `third_party/CmBacktrace/tools/addr2line/win64/addr2line.exe` | in the call-stack helper string |
| Call-stack helper `Show more call stack info by run: … addr2line.exe -e %s%s -afpiC %.*s` | `0x0069E9FC` |
| Fault handler symbol string `cm_backtrace_fault` | `0x0077E8E8` |
| `cm_backtrace_fault` implementation (references its own name for logging) | `~0x005944BC` (name loaded at `0x00594838`) |
| `print_info[]` message-pointer table | `0x006D3718` (39 entries) |

These strings are verbatim CmBacktrace (armink) diagnostics; the
`third_party/CmBacktrace` path and the `cm_backtrace_fault` entry make the
identification unambiguous.

## Recovered `print_info[]` table (`0x006D3718`)

| Index | Message | Run |
|---:|---|---|
| 0 | main-stack configuration error | see exact table audit |
| 1 | `Firmware name: %s, hardware version: %s, software version: %s` | `0x007099A4` |
| 2 | `Assert on thread %s` | `0x0077E8C0` |
| 3 | `Assert on interrupt or bare metal(no OS) environment` | `0x0071C700` |
| 4 | `===== Thread stack information =====` | `0x007481EC` |
| 5 | `====== Main stack information ======` | `0x00748214` |
| 6 | `Error: Thread stack(%08x) was overflow` | `0x0074823C` |
| … | `Dump call stack has an error` | present |

## Configuration and version

The message set fixes the build-time configuration:

- **FreeRTOS/RTOS support on** — the thread-stack information and
  `Assert on thread %s` / thread-stack-overflow messages are only emitted when
  CmBacktrace is built with an OS platform (`CMB_USING_OS_PLATFORM`,
  `CMB_OS_PLATFORM_FREERTOS`), consistent with the source-integrated
  FreeRTOS-Kernel V10.5.1.
- **Firmware-info dump on** — `CMB_FIRMWARE_NAME` / hardware / software version
  banner (index 0) is compiled in.
- **Cortex-M / dump-stack on** — the CFSR/HFSR fault decode and stack unwinding
  drive the call-stack print consumed by the external `addr2line`.

CmBacktrace exposes no runtime `CMB_SW_VERSION` string, so one exact vendor
commit is not byte-visible. Focused source-history comparison and fault-body
disassembly narrow compatible unmodified upstream to
`4abadfa0…73714489`, the untagged post-1.4.1 line advertising `1.4.2`.
Commit `55e7b69` and later are excluded because G2 lacks their stacked-xPSR
bit-9 realignment fix. The complete proof and remaining vendor-fork ambiguity
are recorded in `cmbacktrace-version-recovery-audit.md`.

## Isolation boundary

CmBacktrace is confined to the fault/assert diagnostic path: `cm_backtrace_fault`
(`~0x005944BC`) is reached from the Cortex-M fault handlers (HardFault and
friends) and the assert hook, reads the CFSR/HFSR/MMFAR/BFAR fault registers,
unwinds the exception and thread stacks, and prints through the shared log sink.
It does not participate in normal operation and holds no mutable global state
outside the fault path, so it isolates cleanly as a self-contained
MIT-licensed leaf: a source port needs only the recovered
`CmBacktraceConfig` (RTOS platform, firmware-info strings, CPU/FPU profile) plus
the Cortex-M55 fault-register and stack-unwinding glue.

## Third-party inventory status

With CmBacktrace identified, every vendored third-party component embedded in
the G2 `2.2.6.10` build tree is now accounted for: FreeRTOS-Kernel,
FreeRTOS-Plus-CLI, littlefs, TLSF, EasyLogger, TinyFrame, Cordio/Packetcraft,
LVGL v9.3 (with its bundled FreeType 2.9.1, LZ4 1.10.0, bin_decoder/bmp/fsdrv),
FlashDB 2.1.1, nanopb (pristine-upstream-compatible 0.4.7–0.4.9),
mpaland/printf, AmbiqSuite 5.1.0 / CMSIS, the
generic `ringBuffer`, and CmBacktrace. The Even-proprietary `fw_event_loop` and
the `platform`/`app`/`framework`/`driver`/`product`/`service` trees are
first-party.

This audit does not sign, flash, connect to, or mutate hardware.
