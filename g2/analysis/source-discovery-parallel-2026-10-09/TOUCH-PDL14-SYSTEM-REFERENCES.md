# Finite PDL14 census missing system interface

Failures inspected in touch-pdl14-finite-census-2026-10-09/results.json: cy_sysint.c lacks cy_israddress and RAM/Flash vector declarations; cy_syslib.c lacks three delay globals; cy_systick.c lacks RAM vector declaration. Existing dependency-followup-2026-10-08/touch-source/system_cat2.h is only three lines (stdint, SystemCoreClock, SystemInit), not the full official interface.

## Newly acquired official source

https://github.com/Infineon/TARGET_CY8CPROTO-040T.git at `3f680f7660f7dbf16d4e75c4f57b24a3c030cb54`, isolated acquisition `acquisitions/infineon-cy8cproto-040t`. Apache-2.0 LICENSE with separate EULA retained. No code run. File hashes in touch-system-provenance.json.

- system_cat2.h:287–289 declares uint32_t cy_delayFreqKhz, uint8_t cy_delayFreqMhz, uint32_t cy_delay32kMs.
- system_cat2.h:292 typedef void (*cy_israddress)(void).
- system_cat2.h:293–296 sets vector size48 / bytes192 and declares RAM vector array and const Flash vector array.
- system_cat2.c:70–75 defines the delay globals from default clock frequency;147–149 updates them from SystemCoreClock. Declarations suffice for object compilation; actual definitions/relocations matter when linking/comparing.
- startup_psoc4000t.c:37–48 defines RAM vector storage; GCC uses CY_SECTION(".ram_vectors").101–102 defines Flash vectors with __VECTOR_TABLE_ATTRIBUTE.189–196 copies to RAM and writes VTOR when __VTOR_PRESENT==1. These are official startup references, not an authenticated target startup reconstruction.

## Retain authenticated device and compiler

Keep `-DCY8C4046FNI_T412` and fixed GNU14.2.1. BSP bsp.mk:44–52 selects CY8C4046LQI-T452, a different package: DO NOT import that board DEVICE, board pin config or linker layout as target evidence.
Pinned PDL `35f1714623cfea682d5e285af80d50416b4c7bbc` device header devices/include/cy8c4046fni_t412.h sets Cortex-M0+ revision1, NVIC priority bits2, vendor SysTick0, VTOR1, MPU0, includes core_cm0plus.h at79; SRAM8KB, Flash64KB. Downloaded exact header is pdl-t412-device.h.
Existing registered CMSIS5.9 source `third-party/upstream/cmsis-5-590`, commit `2b7495b8535bdcb306dac29b9ded4cfb679d7e5c`, CMSIS/Core/Include/cmsis_gcc.h:177–182 defines __VECTOR_TABLE as __Vectors and GCC .vectors attribute if not overridden. Keep normal CMSIS/device/system include order so the macro applies to extern declarations; do not invent vector aliases or force a premature header declaration.
Official PDL cy_syslib.h:194–199 includes stdint, stdbool, cy_utils.h, cy_result.h, cy_device.h, cy_device_headers.h. Owner should put full official system_cat2.h at the existing expected include path and preserve header dependency chain, rather than append invented extern stubs.

No newly required CMSIS or PDL repository is needed. Official BSP system interface is the useful acquisition. This closes declaration provenance only: owner compilation, relocation accounting, startup target identity and independent review remain.
