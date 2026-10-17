SECTIONS
{
  .data.opencfw.font.primary_active 0x20002c00 : { KEEP(*(.data.opencfw.font.primary_active)) }
  .data.opencfw.font.secondary_active 0x20002c24 : { KEEP(*(.data.opencfw.font.secondary_active)) }
}
ASSERT(SIZEOF(.data.opencfw.font.primary_active) == 28, "primary selected size")
ASSERT(SIZEOF(.data.opencfw.font.secondary_active) == 28, "secondary selected size")
