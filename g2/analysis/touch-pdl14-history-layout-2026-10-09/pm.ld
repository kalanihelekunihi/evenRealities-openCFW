ENTRY(Cy_SysPm_ExecuteCallback)
SECTIONS {
 .execute 0xA444 : { *(.text.Cy_SysPm_ExecuteCallback) }
 .last 0x20000F24 (NOLOAD) : { *(.bss.lastExecutedCallback.0) }
 .failed 0x20000F28 (NOLOAD) : { *(.bss.failedCallback) }
 .root 0x20000F34 (NOLOAD) : { *(.bss.pmCallbackRoot) }
 /DISCARD/ : { *(.ARM.exidx*) *(.comment*) }
}
