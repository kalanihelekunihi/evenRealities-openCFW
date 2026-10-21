/* Final Main RAM placement contract for the two observed PDM pin words. */
SECTIONS {
  .g2_pdm_clock_pin_words 0x2007421c (NOLOAD) : {
    KEEP(*(.g2_pdm_clock_pin_words))
  }
}
INSERT AFTER .bss;
ASSERT(SIZEOF(.g2_pdm_clock_pin_words) == 8, "PDM pin words require 8 bytes")
ASSERT(g2_pdm_clock_pin_50 == 0x2007421c, "PDM pin 50 RAM address")
ASSERT(g2_pdm_clock_pin_51 == 0x20074220, "PDM pin 51 RAM address")
