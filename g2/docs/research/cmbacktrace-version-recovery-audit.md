# CmBacktrace exact-version and configuration recovery audit

Status: this document preserves the original read-only, evidence-first
recovery for the official G2 `2.2.6.10` Apollo-main image. A later reviewed
tranche added a production-excluded authenticated snapshot and promoted the
bounded current-thread-name helper to production source; see
[`cmbacktrace-get-cur-thread-name-source-candidate-audit.md`](cmbacktrace-get-cur-thread-name-source-candidate-audit.md).
The interval evidence below remains the reason `73714489` is described only as
an openCFW compatibility baseline. Neither tranche claims an exact vendor
checkout, signs firmware, or performs a hardware action.
The reproducible checker is
[`../../tools/analyze_g2_cmbacktrace_version.py`](../../tools/analyze_g2_cmbacktrace_version.py).

## Result

The image is definitively armink/CmBacktrace, but it does **not** identify one
exact tagged release or Git commit. The narrowest defensible match to an
**unmodified upstream mainline state** is:

| Boundary | Upstream commit | Date | Meaning |
|---|---|---:|---|
| first compatible | `4abadfa0c4f86f22352aa5ab9ebbb4f687125a1c` | 2023-08-20 | introduces all four byte-visible lower-bound features |
| last compatible | `73714489f9d8af130aacb515586b397b604a5768` | 2024-07-03 | last mainline state before the incompatible stack-alignment fix |
| first incompatible | `55e7b6990640c481e83ae8a3c0f3af2092b9f7a6` | 2025-02-18 | adds stacked-xPSR bit-9 realignment handling absent from G2 |

This interval is the untagged, post-`1.4.1` line whose `cmb_def.h` advertises
`CMB_SW_VERSION "1.4.2"`. There is no upstream `1.4.2` tag. The preceding
tag is `1.4.1` at `a8973df098d60f7572e839d7456b69e3c2fcf4f9`; the following
tag is `1.5.0` at `3be35d99673805f258de5c2f156fac94eb896da4`.

It would be incorrect to relabel the G2 code as exact `1.4.1`, exact `1.5.0`,
or one exact commit within the interval. A vendor fork could also cherry-pick
or omit upstream changes, so the interval bounds compatible upstream states;
it does not prove the vendor fork's checkout date.

## Decisive version discriminators

The authenticated image is
`ota_s200_firmware_ota.bin`, SHA-256
`36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863`.
Run addresses use `run = file_offset + 0x00437FE0`.

### Lower bound: `4abadfa`

Four independent features first coexist at `4abadfa`:

1. The call-stack diagnostic uses `-afpiC %.*s`. G2 prepends its vendored
   Windows executable path but otherwise exactly retains the upstream format:
   `third_party/CmBacktrace/tools/addr2line/win64/addr2line.exe -e %s%s -afpiC %.*s`.
2. `print_call_stack` allocates/passes 32 entries, proving
   `CMB_CALL_STACK_MAX_DEPTH=32`; earlier `1.4.1` defaults to 16.
3. `dump_stack` initializes its word cap to 16, proving the new
   `CMB_DUMP_STACK_DEPTH_SIZE=16` behavior.
4. `cm_backtrace_init` performs three 40-byte name copies into globals spaced
   44 bytes apart. This proves `CMB_NAME_MAX=40` combined with the new
   `CMB_NAME_MAX + 1` arrays (rounded to four-byte alignment).

The exact bodies are pinned by the analyzer. The most useful anchors are:

| Function | Run interval | Bytes | SHA-256 |
|---|---:|---:|---|
| `cm_backtrace_init` | `0x005939AE..0x00593A38` | 138 | `93eff95cb05fe0c6ae3cf21949ca56c5bad9a589e39ac110f5aa6eca96e0a696` |
| `dump_stack` | `0x00593AFE..0x00593C34` | 310 | `cc4c4017f27aa0ac2a0a64af7fc1cd51de560cdef6051a1b85c57daa8ce4fea6` |
| `print_call_stack` | `0x00593D4A..0x00593E0C` | 194 | `7c27c35c89f1a9d410c75470202ce6a95616429362cdf1b913ca01201b36a905` |

### Upper bound: the `55e7b69` fix is absent

Upstream `55e7b69` adds this operation after the FPU-frame adjustment and
before the stack bounds check: load saved xPSR (`saved_regs_addr[7]`), test bit
9, and add four to `stack_pointer` when exception entry inserted an alignment
word.

G2 instead goes directly from its FPU-frame helper to comparisons against the
stack start/end. The exact G2 window is
`0x005945F0..0x0059460C`, SHA-256
`08ce49570848f40675fc29cd6f442c759799443ca5804b5e73662de48f2bdd66`.
The complete `cm_backtrace_fault` body is
`0x005944BC..0x005947CE` (786 bytes), SHA-256
`741e40d38b66bc5047db4744604c4ea9e7d2a06cf29ebedf1d10cfe7314061e5`.
Because the xPSR value is runtime data, a normal compiler cannot optimize the
upstream fix away. A source port should consciously decide whether to preserve
this historical behavior for binary parity or adopt the later safety fix with
targeted exception-frame tests.

### Why the interval cannot be narrowed further

Between `4abadfa` and `7371448`, upstream changes add RT-Thread 5 support,
custom-language selection, an RTX5 correction, GHS assembly, user-config
inclusion, and ThreadX support. These touch preprocessor branches or files that
are absent from the recovered FreeRTOS/English/IAR build. They therefore leave
no distinguishing code or data in this image.

As a focused reference check, the upstream enum plus unmodified en-US message
header at `4abadfa`, `7371448`, and `55e7b69` were each compiled with Clang for
`arm-none-eabi`, Cortex-M33 selection, C99, freestanding, and `-Os`. All three
message-table objects were byte-identical, SHA-256
`71763744daa5cac939c69a28f644f8d34f61c5cb8b945866571fc6e0ea44a440`.
This confirms that strings alone cannot establish the upper bound; the focused
fault disassembly is required.

## Recovered effective configuration

| Setting | Recovered value | Evidence |
|---|---|---|
| `CMB_USING_OS_PLATFORM` | on | thread assert/fault paths and current-TCB adapters are retained |
| `CMB_OS_PLATFORM_TYPE` | `CMB_OS_PLATFORM_FREERTOS` | adapters at `0x0045601F/27/2F` load current TCB fields `+0x30`, `+0x54`, `+0x34` for stack base, depth, and name |
| `sizeof(StackType_t)` | 4 | stack depth is shifted left two before use as bytes |
| `CMB_USING_DUMP_STACK_INFO` | on | bounded stack dumper and both thread/main stack diagnostics are retained |
| `CMB_CALL_STACK_MAX_DEPTH` | 32 | 32-word call-stack buffer and count passed to unwinder |
| `CMB_DUMP_STACK_DEPTH_SIZE` | 16 | dump loop's initialized word counter |
| `CMB_NAME_MAX` | 40 | all three `strncpy` calls use `0x28` |
| compiler branch | IAR / `__ICCARM__` | effective ELF extension is `.out`; upstream maps `.out` to IAR |
| language content | English | all 39 effective messages match upstream en-US except the vendor path prefix |
| language selector macro | unresolved | patched en-US and post-2023 custom-English produce the same retained bytes |
| CPU behavior | M33-class | STKOF UsageFault diagnostic and FPU-frame/lazy-state paths are compiled |
| CPU selector macro | likely upstream M33, not proven exact | a vendor-added M55 alias with the same branches cannot be excluded |

The linked ranges recovered by `cm_backtrace_init` are main stack
`0x2007D000..0x20080000` (12 KiB) and code
`0x00438400..0x005FA056` (`0x1C1C56` bytes). Its single caller passes:

- firmware name: `product/s200/app/Release/Exe/s200_app`;
- hardware version: `V1.0.0`;
- software version: `2.2.6.10`.

These are application identity arguments. They do not contain the library's
`CMB_SW_VERSION` macro.

## Corrected `print_info[]` boundary

The table begins at `0x006D3718`, not `0x006D371C`. It contains 39 pointers;
index 0 is the main-stack configuration error and index 1 is the firmware
banner. Its 156 pointer bytes have SHA-256
`d1134ec65af98c0d6f2826f9cfe5086f4f0296e154c86fa3437db46e9375a9e0`.
The analyzer verifies every pointer and every complete ASCII string, including
the M33-only STKOF entry.

## Upstream provenance and license correction

Repository: <https://github.com/armink/CmBacktrace.git>

The official upstream `LICENSE` is **MIT**, not Apache-2.0. Its content
SHA-256 is
`e8ed0e84184d2130bd1fcf5a52ce8c16b5bf338c272cab6bbd7993a9d723934e`
at both compatible boundaries. The later snapshot and bounded production
helper therefore use the MIT terms; the earlier openCFW identity audit's
Apache-2.0 statement is superseded and must not be reused.

Pinned boundary identities:

| Item | `4abadfa` floor | `7371448` ceiling |
|---|---|---|
| Git tree | `545881132a4e538d53f260876d295896674bf541` | `541c20dbeb1165f9b2862e2b84cdc63b3d7c718f` |
| `cm_backtrace.c` SHA-256 | `b13da2eb10c26bff3e81628f44fd70b6b3f3d2e2b33ef29d014400a64c44e81e` | `6e444224af3ef223067849b88f61281ec0661e3f38425e84758bf12be057e01c` |
| `cmb_def.h` SHA-256 | `34c2b4e0d481404431ba444679f2638051674ca470c8235d5b42cc8b3062d548` | `897c0818d0e062866edecb467e655d5b02494d7ee1612b036035be08809e75eb` |
| en-US header SHA-256 | `ad77299fecaa9a63c766bfbe9d17099c7542751fc11084bf88520bc88c35a844` | same |

For a future source import, `7371448` is the newest upstream state that
matches the observed historical fault behavior. Pinning that commit would be
a project choice, not a claim that G2 used that exact commit. Alternatively,
current `1.5.0` may be used if the stack-realignment semantic change is
explicitly accepted and tested.

## Remaining unknowns

- Exact vendor-fork commit inside the compatible interval.
- Patched English header versus the upstream custom-language selector.
- Upstream M33 selector versus a vendor-added Cortex-M55 alias.
- Vendor `cmb_println` implementation details beyond its retained dual logging
  calls; those are integration seams, not version discriminators.

No hardware was connected, signed, erased, programmed, or flashed.
