/* SPDX-License-Identifier: MIT
 * Custom CASE source-image contract, not a stock armlink scatter recipe.
 * Source: g2/docs/reference/memory-map.md section7. Native reset/RAM state
 * independently qualified in producer waves005/010/014.
 * Exclude the entire final4KiB bank page pair containing factory data.
 */
MEMORY {
  FLASH_APP (rx) : ORIGIN = 0x08000000, LENGTH = 0x3f000
  RAM_CONTRACT (rw) : ORIGIN = 0x20000000, LENGTH = 0x2c88
}
ENTRY(case_reset_entry_0144)
__case_preserved_page_start = 0x0803f000;
__case_preserved_slot0 = 0x0803f000;
__case_preserved_slot1 = 0x0803f800;
__case_typed_ram_start = 0x20000000;
__case_typed_ram_end = 0x200001a4;
__case_zero_ram_start = 0x200001a4;
__case_zero_ram_end = 0x20002c88;
__case_initial_sp = 0x20002c88;
SECTIONS {
  .isr_vector ORIGIN(FLASH_APP) : { KEEP(*(.isr_vector)) } > FLASH_APP
  ASSERT(SIZEOF(.isr_vector) == 184, "CASE vector must have46words")
  .text.reset 0x08000144 : { KEEP(*(.text.case_reset_entry_0144)) } > FLASH_APP
  ASSERT(ADDR(.text.reset) == 0x08000144, "CASE reset address")
  .text ALIGN(4) : { KEEP(*(.text.case_early_hook_84ae)) *(.text*) *(.rodata*) } > FLASH_APP
  /* STM32 source update path programs8-byte doublewords. Tail padding is
   * erased-flash data, not a copied instruction/provider or stock-byte claim. */
  .image_tail (READONLY) : { BYTE(0xff) FILL(0xffffffff) . = ALIGN(8); } > FLASH_APP
  __case_flash_load_end = .;
  ASSERT((__case_flash_load_end - ORIGIN(FLASH_APP)) % 8 == 0, "Doubleword image alignment")
  /* Reject newly introduced allocated mutable data until its native RAM
   * binding/initialization is authenticated. Existing RAM consumers use
   * source-derived absolute bindings and typed CRT initialization. */
  .data ORIGIN(RAM_CONTRACT) : { *(.data*) } > RAM_CONTRACT AT> FLASH_APP
  .bss (NOLOAD) : { *(.bss*) *(COMMON) } > RAM_CONTRACT
  ASSERT(SIZEOF(.data) == 0, "Unqualified allocated mutable.data")
  ASSERT(SIZEOF(.bss) == 0, "Unqualified allocated mutable.bss")
  ASSERT(__case_flash_load_end <= __case_preserved_page_start, "Factory pages overlap")
  ASSERT(__case_initial_sp == ORIGIN(RAM_CONTRACT) + LENGTH(RAM_CONTRACT), "RAM/SP contract")
  /DISCARD/ : { *(.ARM.exidx*) *(.comment*) }
}
