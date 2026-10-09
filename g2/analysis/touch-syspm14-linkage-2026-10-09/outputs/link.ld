ENTRY(Cy_SysPm_CpuEnterSleep)
EXTERN(Cy_SysPm_CpuEnterDeepSleep Cy_SysPm_RegisterCallback)
SECTIONS {
 .assembly 0x4480 : { *assembly.o(.text) }
 .sleep_direct 0xA374 : { *(.text.Cy_SysPm_CpuEnterSleepNoCallbacks) }
 .deep_direct 0xA388 : { *(.text.Cy_SysPm_CpuEnterDeepSleepNoCallbacks) }
 .register 0xA3B0 : { *(.text.Cy_SysPm_RegisterCallback) }
 .execute 0xA444 : { *(.text.Cy_SysPm_ExecuteCallback) }
 .sleep 0xA528 : { *(.text.Cy_SysPm_CpuEnterSleep) }
 .deep 0xA58C : { *(.text.Cy_SysPm_CpuEnterDeepSleep) }
 .globals 0x20000F34 (NOLOAD) : { *(.bss) }
 /DISCARD/ : { *(.ARM.exidx*) *(.comment*) }
}
