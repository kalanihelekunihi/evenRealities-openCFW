/* Candidate-only packed source XIP probe. This chooses a test layout for
 * direct named XIP functions, not stock address fidelity or a final image.
 * Remaining helper sections, rodata, and literal-tail ownership are excluded.
 */
SECTIONS
{
  .gx8002_xip_packed 0x10203004 : {
    *(.text.gx8002_xip_*)
    *(.text.gx8002_resident_analog_config_update_10203c74)
  }
}
ASSERT(ADDR(.gx8002_xip_packed) == 0x10203004,
       "packed XIP probe start mismatch")
ASSERT(ADDR(.gx8002_xip_packed) + SIZEOF(.gx8002_xip_packed) <= 0x1020a8aa,
       "direct named XIP sections exceed native code span")
