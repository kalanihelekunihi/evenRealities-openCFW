/*
 * openCFW G2 touch (PSoC 4000T / CY8C4046FNI-T412) application linker script.
 *
 * Wave 13 evidence:
 * - Flash: datasheet "CY8C40x5, CY8C40x6 PSOC 4000T" sec 1.1.2: 64 KB flash at 0
 *   (Infineon part page CY8C4046FNI-T412T: 64 KB flash / 8 KB SRAM).
 * - App start 0x3300: stock firmware_touch.bin 2.2.6.10 reset vector 0x4675 and
 *   default handler 0x465d decode as handlers only at base 0x3300 (0x465c = "b .");
 *   apollo-main stock set-app-metadata template at 0x78c098 = 01 00330000 (app 1,
 *   start 0x00003300). Flash below 0x3300 holds the resident DFU loader.
 *   App region is 0x3300..0x10000 (LENGTH 0xcd00); stock payload ends 0xb980.
 * - RAM: 8 KB at 0x20000000, stack top 0x20002000 (stock vector word 0).
 *   0x20000000 is the DFU mailbox byte (application.h G2_TOUCH_DFU_MAILBOX) and
 *   stock relocates its vectors to 0x20000400 (reset 0x4686 memcpy, VTOR write),
 *   so 0x20000000..0x20000400 is not app RAM.
 * - Stock reset copies 0xf1 words to 0x200004c0 and zeroes 0x1ac words at
 *   0x200008a8 (tables at 0xb578..0xb58c), so stock app RAM ends near 0x20000f58.
 *   Several units still address those stock objects by absolute address, so
 *   linker-placed data here starts at 0x20000f58, above that span, to avoid aliasing.
 *   Stack recovered W14 (see __touch_stack_top below): stock capacity 0x10a8 above 0x20000f58.
 */
ENTRY(Reset_Handler)

MEMORY
{
  FLASH (rx)  : ORIGIN = 0x00003300, LENGTH = 0x0000cd00
  RAMVEC (rw) : ORIGIN = 0x20000400, LENGTH = 0x000000c0
  RAMDATA (rw) : ORIGIN = 0x200004c0, LENGTH = 0x000003c4
  RAMGAP  (rw) : ORIGIN = 0x20000884, LENGTH = 0x00000024
  RAMBSS  (rw) : ORIGIN = 0x200008a8, LENGTH = 0x000006b0
  RAM   (rwx) : ORIGIN = 0x20000f58, LENGTH = 0x000010a8
}

SECTIONS
{
  .text : {
    __touch_flash_vectors = .;
    KEEP(*(.isr_vector .vectors .intvec))
    *(.text .text.*)
    *(.rodata .rodata.*)
    . = ALIGN(4);
    /* W14: first records equal stock {0xb58c->0x200004c0, 0xf1 words} / {0x200008a8, 0x1ac words}
       (stock Reset_Handler 0x4674 tables); source LMA differs because .text is smaller. */
    __touch_copy_table_start = .;
    LONG(LOADADDR(.touchdata)) LONG(ADDR(.touchdata)) LONG(SIZEOF(.touchdata) / 4)
    LONG(LOADADDR(.data)) LONG(ADDR(.data)) LONG(SIZEOF(.data) / 4)
    __touch_copy_table_end = .;
    __touch_zero_table_start = .;
    LONG(ADDR(.touchbss)) LONG(SIZEOF(.touchbss) / 4)
    LONG(ADDR(.bss)) LONG(SIZEOF(.bss) / 4)
    __touch_zero_table_end = .;
  } > FLASH

  .ARM.exidx : { *(.ARM.exidx*) } > FLASH

  /* PDL Cy_SysInt_Init/Cy_SysTick_Init use __RAM_VECTOR_TABLE (stock 0x20000400). */
  .ramvectors (NOLOAD) : { __touch_ram_vectors = .; __RAM_VECTOR_TABLE = .; . += 0xc0; } > RAMVEC

  INCLUDE g2/src/touch/link/g2-touch-stockram.ld.inc

  /* Last stock zero-table word: optional newlib stdio cleanup callback. */
  __stdio_exit_handler = 0x20000f54;

  /* W15 evidence: stock 0x20000884..0x200008a8 (36 B). The only stock words in that range are
     0x20000884 at 0x33d4/0x33d8/0x33fc/0x3400 = __TMC_END__ (crtbegin deregister/register_tm_clones
     compare start==end, i.e. empty .tm_clone_table at .data end). No stock word points inside
     (0x20000885..0x200008a7) and neither reset table covers it, so it is unused padding; we keep
     it reserved and empty. upstream cy_syslib.c .noinit cy_faultFrame (0x20 B) is unreferenced and
     removed by --gc-sections, consistent with stock having no reference into this span. */
  .touch_stock_pad (NOLOAD) : {
    __TMC_END__ = .;
    KEEP(*(.tm_clone_table))
    __touch_tm_clone_end = .;
    . = 0x24;
  } > RAMGAP
  ASSERT(__touch_tm_clone_end == __TMC_END__, "stock TM clone table is empty")
  /DISCARD/ : { *(.noinit .noinit.*) }

  .data : ALIGN(4) {
    __data_start = .;
    *(.data .data.*)
    . = ALIGN(4);
    __data_end = .;
  } > RAM AT > FLASH
  __data_load_start = LOADADDR(.data);

  .bss (NOLOAD) : ALIGN(4) {
    __bss_start = .;
    *(.bss .bss.* COMMON)
    . = ALIGN(4);
    __bss_end = .;
  } > RAM
  /* Stack: stock vector[0] / crt0 __stack (pool 0x34c4) = 0x20002000; crt0 0x3458 sets
     sl = sp - 0x10000 (newlib default, no linker stack size). Stock RAM above __bss_end
     0x20000f58 is unused, so stock stack capacity = 0x20002000 - 0x20000f58 = 0x10a8 (4264 B).
     Our extra linker data/bss below reduces it; require the stock capacity minus at most 0x200. */
  __touch_stack_top = 0x20002000;
  __touch_stack_limit = __bss_end;
  ASSERT(__touch_stack_top - __bss_end >= 0x10a8 - 0x200, "touch stack below stock capacity - 0x200")
}
