/*
 * openCFW G2 charging case (STM32G0B1-class, Cortex-M0+) application image.
 *
 * Memory evidence (docs/hardware/g2-case.md, stock firmware_box.raw.bin 2.2.6.10):
 * - Flash bank 1 is 0x08000000..0x0803ffff (128 x 2 KiB pages). The box keeps
 *   preserved serial/identity words at 0x0803f000 and 0x0803f800 and the OTA
 *   code writes them by absolute address, so the image must end below
 *   0x0803f000 (page 126). Bank 2 (0x08040000..) is the OTA install target.
 * - Stock vector word 0 is 0x20002c88. Stock CRT records at 0x0800d93c fill
 *   0x20000000..0x200001a3 from a run-length image and zero
 *   0x200001a4..0x20002c87; nothing in stock or in g2/src/case addresses RAM at
 *   or above 0x20002c88 (literal-pool scan of both), so stock RAM is
 *   0x20000000..0x20002c88 with the MSP stack growing down from its top.
 *
 * Fixed-address RAM: g2/src/case reaches all of its stock state (scheduler,
 * transport, sensor, heap pools, task stacks) by absolute address inside
 * 0x20000000..0x20002c88; the C startup initialises that span exactly as
 * stock (case_crt_init_known_defaults + case_crt_zero_9200). That span is
 * reserved here (STOCKRAM) and the linker never allocates into it. Named
 * .data/.bss objects go above the MSP top in RAM, so they cannot alias any
 * absolute address and a stack overflow cannot reach them.
 *
 * case_crt_init_0270 (startup/startup_vector_candidate.c) reads the record
 * emitted in .case_crt_regions at the fixed address 0x080000b8 to copy .data
 * and zero .bss; keep the record layout in sync with struct
 * case_crt_link_regions there.
 */
ENTRY(case_reset_entry_0144)

MEMORY
{
  FLASH    (rx)  : ORIGIN = 0x08000000, LENGTH = 0x0003f000
  STOCKRAM (rw)  : ORIGIN = 0x20000000, LENGTH = 0x00002c88
  RAM      (rwx) : ORIGIN = 0x20002c88, LENGTH = 0x00021378
}

__case_msp_top = ORIGIN(STOCKRAM) + LENGTH(STOCKRAM);

SECTIONS
{
  .isr_vector ORIGIN(FLASH) : {
    __case_vectors = .;
    KEEP(*(.isr_vector))
    __case_vectors_end = .;
  } > FLASH

  .case_crt_regions : ALIGN(4) {
    LONG(LOADADDR(.data))
    LONG(ADDR(.data))
    LONG(SIZEOF(.data))
    LONG(ADDR(.bss))
    LONG(SIZEOF(.bss))
  } > FLASH

  .text : ALIGN(4) {
    *(.text .text.*)
    *(.rodata .rodata.* .constdata .constdata.*)
    KEEP(*(.case_retained_entries))
    . = ALIGN(4);
  } > FLASH

  .ARM.extab : { *(.ARM.extab* .gnu.linkonce.armextab.*) } > FLASH
  .ARM.exidx : { *(.ARM.exidx* .gnu.linkonce.armexidx.*) } > FLASH

  /* Reserved stock-layout RAM: absolute-address state and the MSP stack. */
  .case_stock_ram (NOLOAD) : {
    __case_stock_ram = .;
    . = LENGTH(STOCKRAM);
  } > STOCKRAM

  .data : ALIGN(4) {
    __case_data_start = .;
    *(.data .data.*)
    . = ALIGN(4);
    __case_data_end = .;
  } > RAM AT > FLASH
  __case_data_load = LOADADDR(.data);

  .bss (NOLOAD) : ALIGN(4) {
    __case_bss_start = .;
    *(.bss .bss.* COMMON)
    . = ALIGN(4);
    __case_bss_end = .;
  } > RAM

  __case_image_end = LOADADDR(.data) + SIZEOF(.data);

  /DISCARD/ : { *(.comment) *(.note .note.*) *(.llvm_addrsig) }
}

/* Vector table: 46 words at the start of flash, followed by the CRT record. */
ASSERT(__case_vectors == 0x08000000, "g2-case: vector table must be at 0x08000000")
ASSERT(__case_vectors_end - __case_vectors == 46 * 4, "g2-case: vector table must be 46 words")
ASSERT(ADDR(.case_crt_regions) == 0x080000b8, "g2-case: CRT record must be at 0x080000b8 (read by case_crt_init_0270)")
ASSERT(SIZEOF(.case_crt_regions) == 20, "g2-case: CRT record layout changed")
ASSERT(__case_msp_top == 0x20002c88, "g2-case: MSP top must match vector word 0 (0x20002c88)")

/* Image stays in bank 1 below the preserved serial pages. */
ASSERT(__case_image_end <= 0x0803f000, "g2-case: image overlaps preserved pages at 0x0803f000")
ASSERT(__case_image_end - 0x08000000 <= 256K, "g2-case: image exceeds 256 KiB")

/* Linker-placed RAM never overlaps the absolute-address stock span. */
ASSERT(ADDR(.data) >= 0x20002c88, "g2-case: .data overlaps stock fixed RAM")
ASSERT(ADDR(.bss) >= ADDR(.data) + SIZEOF(.data), "g2-case: .bss overlaps .data")
ASSERT(ADDR(.bss) + SIZEOF(.bss) <= 0x20024000, "g2-case: RAM exceeds 144 KiB")
ASSERT(SIZEOF(.data) % 4 == 0 && SIZEOF(.bss) % 4 == 0, "g2-case: CRT copies whole words")
