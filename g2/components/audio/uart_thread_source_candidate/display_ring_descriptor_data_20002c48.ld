SECTIONS
{
  .data.opencfw.ring.primary 0x20002c48 : { KEEP(*(.data.opencfw.ring.primary)) }
  .data.opencfw.ring.secondary 0x20002c78 : { KEEP(*(.data.opencfw.ring.secondary)) }
}
ASSERT(SIZEOF(.data.opencfw.ring.primary) == 48, "primary ring size")
ASSERT(SIZEOF(.data.opencfw.ring.secondary) == 48, "secondary ring size")
