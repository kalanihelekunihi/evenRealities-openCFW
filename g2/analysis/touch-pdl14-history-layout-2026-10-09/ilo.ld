ENTRY(Cy_SysClk_IloStartMeasurement)
EXTERN(Cy_SysClk_IloStopMeasurement Cy_SysClk_IloCompensate)
SystemCoreClock = 0x20000878;
SECTIONS {
 .start 0x9D90 : { *(.text.Cy_SysClk_IloStartMeasurement) }
 .stop 0x9DDC : { *(.text.Cy_SysClk_IloStopMeasurement) }
 .compensate 0x9E18 : { *(.text.Cy_SysClk_IloCompensate) }
 .division 0xA6C0 : { *uidiv.o(.text) }
 .zero 0xA9A8 : { *zero.o(.text) }
 .comp_state 0x20000F1C (NOLOAD) : { *(.bss.compRunStat.0) }
 .prevent 0x20000F1D (NOLOAD) : { *(.bss.preventIloMeasurment) }
 .measurement 0x20000F1E (NOLOAD) : { *(.bss.iloMeasurment) }
 /DISCARD/ : { *(.ARM.exidx*) *(.comment*) }
}
