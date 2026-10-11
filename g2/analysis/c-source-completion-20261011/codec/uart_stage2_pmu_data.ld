OUTPUT_ARCH(csky)
SECTIONS
{
  .stage2.pmu.table 0x200092b4 : { KEEP(*(.stage2.pmu.table)) }
  .stage2.pmu.aux 0x20009454 : { KEEP(*(.stage2.pmu.aux)) }
}
