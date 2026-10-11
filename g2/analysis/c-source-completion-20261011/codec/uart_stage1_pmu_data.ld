OUTPUT_ARCH(csky)
SECTIONS
{
  .stage1.pmu.table 0x20002018 : { KEEP(*(.stage1.pmu.table)) }
  .stage1.pmu.aux 0x20002228 : { KEEP(*(.stage1.pmu.aux)) }
}
