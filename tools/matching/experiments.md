# Compiler-identification experiments

## 2026-09-29 — G2 case: `uxListRemove` (FreeRTOS `list.c`)

**Target:** `firmware_box.raw.bin` (`773b6d4c…`) at `0x0800BF2C`, 38 bytes:
`0169436882689a60836842685a604a68824201d182684a60002202610868401e086008687047`.

**Why this function:** it is short, has no relocations, and depends on
almost no configuration.

| Matrix | Result |
| --- | --- |
| Arm GNU 6-2017-q2, 7-2018-q2, 8-2019-q3, 9-2020-q2, 10.3-2021.10, 13.3.Rel1 × FreeRTOS V10.2.1, V10.3.0, V10.3.1, V10.4.3, V10.4.6, V10.5.1 × `-O0/-O1/-Og/-Os/-O2/-O3` × `cortex-m0`/`cortex-m0plus` (432 builds) | no match; different register allocation |
| the same GCC set with `-DconfigLIST_VOLATILE=volatile` (144 builds) | same length and instruction sequence; register allocation still differs |
| LLVM clang 11.0.0, 13.0.0 (official release binaries) and 14–20 × `-Os/-Oz/-O1/-O2/-O3` with `configLIST_VOLATILE=volatile` | **identical register allocation**; the only difference is the order of the two leading loads (`pxNext` and `pxPrevious`) |
| clang with `cortex-m0`, generic `thumbv6m`, `cortex-m1`, `-misched=source` | no exact match |

**Corroborating evidence in the image:**
- the reset handler at `0x08000144` is the Keil `startup_stm32g0xx.s`
  sequence `LDR R0,=SystemInit; BLX R0; LDR R0,=__main; BX R0`;
- `__aeabi_uidiv` at `0x08000160` is the Arm C library shift-subtract
  loop, not libgcc.

**Conclusion (Strong):** the case firmware was built with **Keil MDK: Arm
Compiler 6 (armclang, LLVM-based), armlink and the Arm C library**, with
`configLIST_VOLATILE=volatile`. The earlier "GNU Arm GCC plus newlib"
attribution is superseded. Every open LLVM release from 11 to 20 makes the
same single scheduling choice, so the remaining difference is specific to
Arm's proprietary armclang. Open clang reproduces this function except for
one scheduling decision, so it is a close proxy for analysis. Byte identity
needs armclang, now registered as blocker `TC-ARMCLANG6`.

**Reproduce:** compile `third-party/upstream/freertos-kernel/list.c` (or the
matching FreeRTOS tag) with a minimal `FreeRTOSConfig.h` and
`-ffunction-sections`, then run `compare_function.py --image
g2/blobs/official/g2-2.2.6.10/firmware_box.raw.bin --base 0x08000000
--address 0x0800BF2C --size 38 --section .text.uxListRemove`.

## 2026-09-29 — G2 touch: `Cy_SCB_ReadArrayNoCheck` (Infineon PDL `cy_scb_common.c`)

**Target:** touch image (payload offset + `0x3300`) at flash `0x9218`, 56
bytes.

**Source:** `third-party/upstream/infineon-mtb-pdl-cat2` (release-v2.21.0),
with `-DCY8C4046FNI_T412`, `third-party/upstream/infineon-core-lib`
(release-v1.8.0), CMSIS Core, and a stub `system_cat2.h` that carries only
declarations.

| Matrix | Result |
| --- | --- |
| Arm GNU 6-2017-q2, 7-2018-q2, 8-2019-q3, 9-2020-q2 × `-O1/-Og/-Os/-O2/-O3` | no match |
| Arm GNU 10.3-2021.10, 11.3.Rel1, 12.2.Rel1, 13.3.Rel1 × `-Og` | **exact byte match** |
| the same releases × `-O1/-Os/-O2/-O3` | no match |

**Conclusion (Proven for this function):** the touch firmware is built with
open-source Arm GNU GCC, release 10.3 or later, at `-Og`. `-Og` is
ModusToolbox's default Debug configuration. The official Infineon PDL
source reproduces the stock bytes exactly. Matching more functions is
needed to choose between the 10.3–13.3 releases. No licensed tool is
involved, so the touch payload is fully unblocked.
