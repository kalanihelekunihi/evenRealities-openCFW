# NOR reset, read mode, and timing wrapper evidence

Locked input is `g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin`, SHA-256 `f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5`, mapped at `0x410000` by `g2/components/bootloader/update_core/verify.py`.

The source candidates are `opencfw_provider_42052a`, `opencfw_provider_420f10`, and `opencfw_provider_4201ba` in `g2/components/bootloader/nor_commands/nor_commands.c`. Their stock ranges and hashes are:

| Function | Range | Bytes | SHA-256 |
|---|---:|---:|---|
| reset commands `0x42052a` | `[0x42052a, 0x42059e)` | 116 | `ec592b1db3c6c381036d5c69d065056547b69d870025dd08aef11f34c2b350f0` |
| timing wrapper `0x4201ba` | `[0x4201ba, 0x420254)` | 154 | `a31a24975e2a7de11d5a42b05db91799e7e9656bca2cc22112867efdf9f2b9b7` |
| read-mode `0x420f10` | `[0x420f10, 0x420f6a)` | 90 | `b73005fad7b0cae8e2f2273bae21ab2877963d2d14534b5afc2918c515c26a13` |

The stock reset routine submits instruction `0x66`, logs level 1/line `0x2c4` if it fails, passes raw delay argument `1`, submits `0x99`, logs level 1/line `0x2c9` if it fails, then passes raw delay argument `0x32` (50). Both delays occur even when a command fails. It calls `0x42069e`, whose source candidate constructs the same 24-byte PIO descriptor and calls the injected blocking transfer with timeout `1,000,000`; transfer errors are delegated with module `0x00431468` and the command/address/length/status arguments. PIO bytes are compared against the original; descriptor pointer bytes are intentionally excluded from the event trace.

The read-mode wrapper configures the 32-byte device record at `0x2000020c` through `0x420e08`, calls latency control with argument zero, then calls MSPI control request `0x18` with a pointer to a one-byte zero. The shared `0x420e08` candidate performs disable → device configure → enable; it stops and logs at each failure, then publishes record word at `0x200270d8` and config byte offset 8 after success. Error messages, file/function names, and source lines come from the stock literal pool and are represented in source. `0x420f10` return values are not claimed: stock epilogues pop into `r0/r1/r2/pc`, so they are incidental to this void-like wrapper.

The timing wrapper clears six local bytes, invokes the scan provider `0x420002`, copies eight local bytes to the global record at `0x2000023c` only on scan success, then logs the six record fields with success line `0x1f3`/level 2 or failure line `0x1fb`/level 1. The scan search itself (36×32 settings per existing disassembly/review) remains an explicit provider. Stock copies an eight-byte stack value after clearing only six bytes; the upper two bytes at entry-SP−10 and entry-SP−9 are inherited from caller stack and remain indeterminate. `nor_timing_wrapper.S` preserves stock's `push {r7,lr}; sub sp,#0x28`, passes the local at `sp+0x20` through the exact six-byte clear, calls a C core, and reproduces stock's stack epilogue. The test seeds those caller-stack tail bytes with two distinct nonzero patterns and verifies both scan-success copies (e.g. `112233445566a55a`, `1122334455663cc3`) and scan-failure non-copy behavior against stock. Thus the source matches caller-provided tail bytes; it does not claim a single fixed value for the undefined bytes.

`verify_nor_commands.py` executes the original and ARM-compiled candidate in Unicorn against the locked bytes. All 13 cases pass: four command success/failure combinations, five read-mode configure/control paths, and four timing cases with distinct nonzero caller tails across scan success/failure. It covers 646 distinct original instruction bytes across these paths. HAL, transfer, scan, delay, logger, and publication internals are intercepted as explicit synthetic providers. No flash hardware, MSPI registers, real timing scan, physical delay units, or logging sink is exercised. The test does not interpret delay arguments as microseconds or ticks.

Build and test command: `make -C g2/components/bootloader/nor_commands verify`. Result: PASS, 13 cases, 646 distinct original instruction bytes. The JSON records hashes and full traces.
