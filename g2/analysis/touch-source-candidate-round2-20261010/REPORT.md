# Touch round-two source composition

## Result

The source-only archive compiles **45/45 C translation units** from **28/28
existing bounded touch offline modules** for ARMv6-M Cortex-M0+. All 28 module
`DELIVERABLES.json` file-hash contracts were checked against current files:
**0 mismatches**. The official locked touch binary still hashes to
`0d13d8bb1337bf22989dc16143e3d5eca29a31cc1ed753ff624668750ea9470d`.
The archive is ELF32 ARM EABI and has no duplicate global definitions.

The build receipt is
`g2/components/touch/source_candidate_20261010/build/receipt.json`; its
archive SHA-256 is `33c9a64b767a101fe1c374cb0cd7c4863d322981f948ca4e92fc8a49cd2b3d0e`.
The build records exact per-unit command lines, all 129 distinct local input
files found by dependency generation, and per-object hashes. It uses Apple
Clang 21 with `-target armv6m-none-eabi -mcpu=cortex-m0plus -mthumb -Og`,
freestanding/no-builtin/function/data sections, and the pinned PDL/CMSIS/core
headers already present in the research tree. This is compile/object evidence,
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

## Unresolved provider census

The archive has eight undefined global symbols after internal definitions are
subtracted: `Cy_MSCLP_Capture`, `Cy_MSCLP_Configure`,
`Cy_SCB_I2C_SlaveConfigReadBuf`, `Cy_SCB_I2C_SlaveConfigWriteBuf`,
`Cy_SysLib_EnterCriticalSection`, `Cy_SysLib_ExitCriticalSection`,
`__aeabi_uidiv`, and `__aeabi_uidivmod`. The latter six have identifiable
public SDK/toolchain source families in earlier touch work; source-family
identity is not proof that their objects reproduce original bytes. The two
MSCLP providers require a pinned CapSense source/configuration composition and
an original-byte comparison. `touch_flash_write_row` is internally defined by
the 45-unit archive.

## Coverage and next tasks

The touch stored-payload denominator is **34,464 bytes**. The existing
coverage audit reports 308/308 raw pseudocode-export function entries,
27,879/34,464 export-associated bytes, and a 15,616-byte validated listing
lower bound. Those are different measures. This composition proves **45/45
bounded source units compile**, but there is no defensible C-compilable byte
numerator for the 34,464-byte image and no whole-payload source build.

The remaining counted integration tasks are **eight provider-symbol bindings,
one whole-payload source/section inventory, one link/layout and byte comparison,
and one hardware/runtime validation task**. This is **11 counted tasks**, not a
claim that 11 tasks suffice to finish: the first complete inventory may reveal
additional missing source units and data. A bounded effort estimate for those
known tasks is several focused research/build rounds; image-wide completion
cannot be estimated from the present evidence. Concrete missing evidence is a
verified full touch source map (including data/CRT/CapSense), exact vendor
configuration and compiler/linker options, provider byte matches at original
addresses, and a complete linked image equality proof. Hardware behavior
requires physical captures after source closure.

The current archive only combines already delivered bounded C modules. No
module, canonical gate, official firmware, or staged work was changed.
