ENTRY(Cy_SysLib_Delay)
EXTERN(Cy_SysLib_DelayUs)
cy_delay32kMs = 0x2000086C;
cy_delayFreqMhz = 0x20000870;
cy_delayFreqKhz = 0x20000874;
SECTIONS {
 .assembly 0x4480 : { *assembly.o(.text) }
 .delay 0xA2F0 : { *(.text.Cy_SysLib_Delay) }
 .delay_us 0xA324 : { *(.text.Cy_SysLib_DelayUs) }
 /DISCARD/ : { *(.ARM.exidx*) *(.comment*) }
}
