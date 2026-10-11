# Touch round-two source composition

## Result

The source-only archive compiles **45/45 C translation units** from **28/28
existing bounded touch offline modules** for ARMv6-M Cortex-M0+. All 28 module
`DELIVERABLES.json` file-hash contracts were checked against current files:
**0 mismatches**. The official locked touch binary still hashes to
`0d13d8bb1337bf22989dc16143e3d5eca29a31cc1ed753ff624668750ea9470d`.
The archive is ELF32 ARM EABI and has no duplicate global definitions.

The round-three build receipt is
`g2/components/touch/source_candidate_20261010/build/receipt.json`; its
deterministic archive SHA-256 is `a913135b17f33a86a83346dc8e4f4c145169832255546407b273cb80e17c0c01`.
The build records exact per-unit command lines, transitive local input hashes,
and per-object hashes. It uses Apple
Clang 21 with `-target armv6m-none-eabi -mcpu=cortex-m0plus -mthumb -Og`,
freestanding/no-builtin/function/data sections, and the pinned PDL/CMSIS/core
headers already present in the research tree. Five GNU14.2 MSCLP, SysLib and
libgcc objects are **rebuilt on every invocation** in a pinned offline Docker
image from their retained source/config/compiler, then checked against earlier
authenticated object hashes. Pinned SCB I2C/common source and reset data are
also compiled on every invocation with the same
target/device definitions. This is compile/object evidence,
not a claim of original compiler identity or original byte equality.

## Original-byte contract

The sealed modules' current bytes match their own `DELIVERABLES.json` hashes.
Their earlier original/native comparisons remain bounded evidence; for example,
`touch-gesture-machine-closure-2026-10-08/REPORT.md` records 4,373 passing
machine comparisons and 874/874 original instruction bytes visited, and
`touch-scan-isr-closure-2026-10-08/REPORT.md` records its selected source and
public SDK byte checks. This round did not rerun every machine fixture or
derive an image-wide byte match from the new Clang archive. It did reauthenticate
the locked source binary and all sealed module file contracts.

## Initial eight imports: source and contract disposition

| Import | Source/provider evidence | Candidate disposition |
| --- | --- | --- |
| `Cy_MSCLP_Capture` | Pinned PDL `cy_msclp.c`; GNU14.2 full 48-byte section matches stock at `0x8FA0` (`touch-compiler14-successor-2026-10-09/results.json`) | Authenticated source-built object included |
| `Cy_MSCLP_Configure` | Same source/receipt; full 424-byte section matches stock at `0x8FD0` | Same object included |
| `Cy_SCB_I2C_SlaveConfigReadBuf` | Pinned PDL `cy_scb_i2c.c` declaration and implementation, original app/report call ABI in `touch-callback-ownership-2026-10-08` | Compiled in candidate; no full original-section equality claim |
| `Cy_SCB_I2C_SlaveConfigWriteBuf` | Same source, original RX rearm call ABI/behavior in `touch-callback-ownership-2026-10-08` | Same object included; no full original-section equality claim |
| `Cy_SysLib_EnterCriticalSection` | Pinned PDL `cy_syslib_gcc.S`; exact eight stock bytes at `0x4492` (`touch-syslib14-assembly-2026-10-09/results.json`) | Authenticated source-built object included |
| `Cy_SysLib_ExitCriticalSection` | Same source; exact six stock bytes at `0x449A` | Same object included |
| `__aeabi_uidiv` | Exact-release GCC `lib1funcs.S` and true divide-zero hook rebuilt in `touch-libgcc14-source-rebuild-2026-10-09`; original 98-case ABI/zero comparison in `touch-libgcc14-division-2026-10-09` | Authenticated source-built `uidiv.o` and `zero.o` included |
| `__aeabi_uidivmod` | Same source/rebuild; genuine remainder register and zero-divisor behavior, no invented C undefined-case policy | Same objects included |

All eight initial imports now resolve inside the archive. The SCB source also
requires `Cy_SCB_ReadArray`, `Cy_SCB_WriteArray`, and
`Cy_SCB_WriteDefaultArray`, supplied by the pinned `cy_scb_common.c` compiled
here. MSCLP requires `Cy_SysLib_DelayUs`, supplied by the previously
source-built and original-byte matched `cy_syslib.c` object
(`touch-syslib14-delay-linkage-2026-10-09/results.json`).

**Reset-data closure:** the expanded archive has **zero unresolved global/weak
symbols** under `arm-none-eabi-nm -g`, with zero duplicate strong globals. The
three delay globals are defined in `source_candidate_20261010/reset_data.c`.
The locked reset routine at `0x4692..0x46D6` reads a copy-table descriptor at
`0xB578`: source `0xB58C`, target `0x200004C0`, count `0xF1` words. It copies
the following proven initial data:

| Symbol | RAM target | Flash source | Reset bytes | Value |
| --- | --- | --- | --- | ---: |
| `cy_delay32kMs` | `0x2000086C` | `0xB938` | `00 00 E0 2E` | 786,432,000 |
| `cy_delayFreqMhz` | `0x20000870` | `0xB93C` | `18` | 24 |
| `cy_delayFreqKhz` | `0x20000874` | `0xB940` | `C0 5D 00 00` | 24,000 |
| `SystemCoreClock` (corroborating clock word) | `0x20000878` | `0xB944` | `00 36 6E 01` | 24,000,000 |

The candidate build independently checks the stock copy descriptor, target
mapping, bytes and authenticated firmware hash before compiling these data
definitions. The official `system_cat2.c` retained under
`source-discovery-parallel-2026-10-09/acquisitions/infineon-cy8cproto-040t/`
defines and updates them; its 24 MHz default formulas yield the same reset
values. The G2 runtime `SystemInit` update path, clock transitions and final
linker placement have **not** been proved, so these definitions assert reset
initializers only. Their true original RAM targets are recorded above; the
relocatable archive does not force those addresses.

## Coverage and next tasks

The touch stored-payload denominator is **34,464 bytes**. The existing
coverage audit reports 308/308 raw pseudocode-export function entries,
27,879/34,464 export-associated bytes, and a 15,616-byte validated listing
lower bound. Those are different measures. This composition proves **45/45
bounded source units compile**, but there is no defensible C-compilable byte
numerator for the 34,464-byte image and no whole-payload source build.

The remaining counted integration tasks are **one runtime delay-global lifecycle
and clock proof, one whole-payload source/section inventory, one link/layout
and byte comparison, and one hardware/runtime validation task**. This is **four
counted tasks**, not a claim that four tasks suffice to finish: the first complete
inventory may reveal additional missing source units and data. A bounded effort
estimate for those known tasks is several focused research/build rounds; image-wide completion
cannot be estimated from the present evidence. Concrete missing evidence is a
verified full touch source map (including data/CRT/CapSense), exact vendor
configuration and compiler/linker options, provider byte matches at original
addresses, and a complete linked image equality proof. Hardware behavior
requires physical captures after source closure.

The current archive combines bounded touch C with source-owned provider and
reset-data objects; it does not package an executable firmware image. No existing module,
canonical gate, official firmware, or staged work was changed.
