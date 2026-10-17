SECTIONS
{
  .data.opencfw.ring.locale_dispatch 0x200044c0 :
  { KEEP(*(.data.opencfw.ring.locale_dispatch)) }
}
ASSERT(SIZEOF(.data.opencfw.ring.locale_dispatch) == 44, "locale dispatch selected size")
