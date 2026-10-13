/* Diagnostic source placement: native vector and reset addresses only.
 * Other regions, fill, data and reachability remain unqualified. */
ENTRY(case_reset_entry_0144)
SECTIONS {
  .isr_vector 0x08000000 : { KEEP(*(.isr_vector)) }
  ASSERT(SIZEOF(.isr_vector) == 184, "CASE vector has 46 words")
  .text.reset 0x08000144 : { KEEP(*(.text.case_reset_entry_0144)) }
  ASSERT(ADDR(.text.reset) == 0x08000144, "CASE reset entry address")
  . = ALIGN(4);
  .text : { KEEP(*(.text.case_early_hook_84ae)) *(.text*) *(.rodata*) }
  /DISCARD/ : { *(.ARM.exidx*) *(.comment*) }
}
