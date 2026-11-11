/*
 * openCFW G2 codec image A (GX8002 CK804EF) linker script -- Wave 13.
 *
 * Evidence:
 * - Stock corpus RUN.json (firmware_codec.bin 2.2.6.10 dual BINH): image_a_sram base
 *   0x10023400 (14716 B, entry 0x10023500), image_a_xip base 0x10203004 (36484 B),
 *   uart_boot_stage1 0x10000000 (10240 B), stage2 0x10002800 (27964 B).
 * - g2/docs/reference/memory-map.md: NPU SRAM reservation [0x10000000,0x10023400)
 *   (NPU_SRAM_SIZE 0x23400); image A SRAM [0x10023400,0x10026D7C), text to
 *   0x100264E4, data from 0x100264E8; stack top 0x2002F7FC (DRAM).
 * - Resident data objects are pinned at the stock addresses carried in their
 *   section names (.gx8002.*.<addr> >= 0x264e4), so a text overflow into the data
 *   span fails the link.
 * - GX8002 datasheet: 208 KB SRAM -> RES/STAGE upper bound 0x10034000.
 *   Evidence (W14, third-party/upstream/nationalchip-lvp-kws/arch/soc/grus): soc_config.h STAGE1/STAGE2 IRAM base 0x10000000 and
 *   DRAM base 0x20000000 with equal sizes; link.ld reserves
 *   ".dummy_for_stage2_sram_text_place_hold { . += SIZEOF(.stage2_sram_text); } > stage2_dram",
 *   so 0x1xxxxxxx (I-bus) and 0x2xxxxxxx (D-bus) are views of ONE SRAM. TOTAL_SRAM =
 *   0x20000+0x10000 (+0x4000 audio-in at 0x20030000), so the I-bus SRAM window ends at
 *   0x10030000 (the datasheet's 208 KB includes the 16 KB audio-in block).
 * - XIP: board gx8002b = 512 KB NOR; CONFIG_FLASH_XIP_BASE 0x10200000 (third-party/upstream/nationalchip-lvp-kws/arch/soc/grus/include/base_addr.h:88);
 *   STAGE2 XIP = base + 0x3000 (stock 0x10203004 = +4 header). XIP ends 0x10280000.
 * - Ownership (W18, from the stock section split: corpus open-2026-09-29 image_a_sram,
 *   image_a_xip and uart_boot_stage{1,2} decomp sets): generic-named units whose stock
 *   body address is known are routed explicitly to RES/STAGE2 (see the comments there).
 *   Plain `*(.text)` is empty in this payload (W17 map: 0 bytes), so it does not decide anything.
 * - FLAG: still unresolved, these stay in XIP: crc32/crc32_no_comp,
 *   __fe_* (resident_fp_environment_csky.c has no stock address), and the
 *   g2_codec_* glue whose cited addresses are all 0x102xxxxx (XIP).
 *   Wave20 upstream match (relocation-masked byte match vs firmware_codec.bin; image_a_xip
 *   file window 0xc590..0x15414, VMA = off + 0x101f6a74, calibrated by 4 unique g2 bodies):
 *   csky-abiv2-gcc-6.3 ck803 libgcc.a bodies sit in stock XIP, so XIP placement is correct for:
 *   __fixunsdfsi 0x10209a6c, __udivdi3 0x10209aa4, __adddf3 0x1020a09c, __subdf3 0x1020a0cc,
 *   __muldf3 0x1020a108, __divdf3 0x1020a308, __gtdf2/__gedf2 0x1020a420, __fixdfsi 0x1020a460,
 *   __floatunsidf 0x1020a4d0, __muldi3 0x1020a528; crc32_no_comp is an exact match at 0x102097f4.
 *   Reconstructed C implementations now provide the compiler entry aliases
 *   for add/sub/mul/divdf3, fixdfsi, fixunsdfsi, floatunsidf, and udivdi3;
 *   the superseded compiler-rt units are compile-only in sources.json. Their
 *   code is not yet byte-identical to the stock libgcc bodies.
 *   The csky_* DSP bodies (upstream libcsky_dsp.a) match stock only at file
 *   0x478a4..0x48164, outside image_a. No image-A code relocates to these
 *   functions, so their upstream units are compile-only in sources.json and
 *   the linker also excludes the unowned DSP sections below.
 *   __ashldi3/__lshrdi3/__cmpdf2/__eqdf2/__unorddf2/__fe_*
 *   have no image_a body. So their codec-a placement has no stock counterpart.
 */
ENTRY(gx8002_resident_reset_entry_23500)

MEMORY
{
  STAGE1 (rwx) : ORIGIN = 0x10000000, LENGTH = 0x00002800
  STAGE2 (rwx) : ORIGIN = 0x10002800, LENGTH = 0x00020c00
  RES    (rwx) : ORIGIN = 0x10023400, LENGTH = 0x00010c00
  XIP    (rx)  : ORIGIN = 0x10203004, LENGTH = 0x0007cffc
  DRAM   (rwx) : ORIGIN = 0x20000000, LENGTH = 0x0002f800
}

SECTIONS
{
  .stage1.vectors 0x10000000 : {
    KEEP(*(.gx8002.uart.stage1.vectors))
  } > STAGE1
  .stage1.reset 0x10000100 : {
    KEEP(*(.text.gx8002_uart_stage1_reset))
  } > STAGE1
  .stage1.traps 0x10000130 : {
    KEEP(*(.text.gx8002_uart_stage1_traps))
  } > STAGE1
  .stage1.irq_traps 0x10000134 : {
    KEEP(*(.text.gx8002_uart_stage1_irq_traps))
  } > STAGE1
  .stage1 : { *(.text.gx8002_uart_stage1_* .rodata.gx8002_uart_stage1_*) } > STAGE1
  ASSERT(SIZEOF(.stage1.vectors) == 0x100 && gx8002_uart_stage1_reset == 0x10000100,
         "UART stage-1 vector and reset placement changed")
  ASSERT(gx8002_uart_stage1_traps == 0x10000130 &&
         gx8002_uart_stage1_irq_traps == 0x10000134,
         "UART stage-1 exception entries changed")
  /* Stage-1 initialized data, in stock order from image offset 0x2004. The
     stock code addresses it through the D-bus view (0x2000xxxx = the same
     SRAM as 0x1000xxxx), and the DMA descriptor chain needs those bus
     addresses, so the VMA is 0x20002004 and the data loads with the stage-1
     image at 0x10002004. Stage 2 reads 0x20002005 and 0x20002010. */
  .stage1.data 0x20002004 : AT(0x10002004) {
    KEEP(*(.stage1.state))
    KEEP(*(.stage1.pmu.table))
    *(.stage1.data.trim_sources)
    *(.stage1.data.clock_sources)
    KEEP(*(.stage1.pmu.aux))
    *(.stage1.data.flash_id)
    *(.stage1.data.dma_base)
    *(.stage1.data.dma_descriptors)
    *(.stage1.data.pll)
    *(.stage1.data.board_sources)
    *(.stage1.data.*)
  }
  ASSERT(ADDR(.stage1.data) == 0x20002004 && gx8002_uart_stage1_state == 0x20002004,
         "stage-1 state must sit at 0x20002004 (read by stage 2)")
  ASSERT(ADDR(.stage1) + SIZEOF(.stage1) <= 0x10002004, "stage-1 code overlaps its data")
  ASSERT(ADDR(.stage1.data) + SIZEOF(.stage1.data) <= 0x20002700,
         "stage-1 data runs into the stage-1 stack (top 0x200027fc)")
  .stage2.vectors 0x10002800 : {
    KEEP(*(.gx8002.uart.stage2.vectors))
  } > STAGE2
  ASSERT(SIZEOF(.stage2.vectors) == 0x100 &&
         gx8002_uart_stage2_vectors == 0x10002800,
         "UART stage-2 vectors must occupy the first 256 bytes")
  .stage2.reset 0x10002900 : {
    KEEP(*(.text.gx8002_uart_stage2_reset_entry))
  } > STAGE2
  ASSERT(gx8002_uart_stage1_second_entry == 0x10002900,
         "UART stage-2 reset must sit at 0x10002900")
  .stage2.trap 0x10002950 : {
    KEEP(*(.text.gx8002_uart_stage2_trap_entry_2950))
  } > STAGE2
  ASSERT(gx8002_uart_stage2_trap_entry_2950 == 0x10002950 &&
         gx8002_uart_stage2_exception_bridge_2994 == 0x10002994,
         "UART stage-2 exception entries changed")
  .stage2.irq 0x10003124 : {
    KEEP(*(.text.gx8002_uart_stage2_irq_entry_3124))
  } > STAGE2
  ASSERT(gx8002_uart_stage2_irq_entry_3124 == 0x10003124,
         "UART stage-2 IRQ entry must sit at 0x10003124")
  .stage2 : {
    *(.text.gx8002_uart_stage2_* .rodata.gx8002_uart_stage2_* .rodata.gx8002_stage2_* .stage2.*)
    /* W18: static helpers of uart_stage2_* units, which are stage-2 by their stock bodies
       (corpus uart_boot_stage2/decomp): combine (fp_add_words 0x100076c4/0x100076f4),
       special (fp_mul_div 0x10007730/0x10007930), unlink_free (pool_free_core 0x10007240),
       parse_argument (command_serialdown 0x10005628). W17 had them in XIP. */
    *(.text.combine .text.special .text.unlink_free .text.parse_argument)
  } > STAGE2

  .res.vectors 0x10023400 : { KEEP(*(.gx8002.vectors.23400)) } > RES
  .res.reset 0x10023500 : { KEEP(*(.text.gx8002_resident_reset_entry_23500)) } > RES
  .res.clear_bss 0x10023528 : { KEEP(*(.text.gx8002_resident_clear_bss_23528)) } > RES
  .res.system_initialize 0x1002354c : { KEEP(*(.text.gx8002_resident_system_initialize_2354c)) } > RES
  .res.trap_c 0x100235f0 : { KEEP(*(.text.gx8002_resident_trap_c_235f0)) } > RES
  .res.trap 0x100235fc : { KEEP(*(.text.gx8002_resident_exception_entry)) } > RES
  /* Group the named pre-IRQ functions and their source-owned literals before
     the stock compact IRQ vector target. The three rodata sections belong to
     pre-IRQ functions and fill the authenticated text span without discarding
     any source body. */
  .res.pre_irq 0x1002364c : {
    *(.text.gx8002_resident_*_23* .text.gx8002_resident_*_24*
      .text.gx8002_resident_*_250* .text.gx8002_resident_*_251*
      .text.gx8002_resident_*_252* .text.gx8002_resident_*_253*
      .text.gx8002_resident_*_254* .text.gx8002_resident_*_2550*
      .text.gx8002_resident_*_2551* .text.gx8002_resident_*_2552*
      .text.gx8002_resident_*_2553* .text.gx8002_resident_*_2554*
      .text.gx8002_resident_*_2555* .text.gx8002_resident_*_2556*)
    *(.rodata.gx8002_resident_flash_getinfo_23858
      .rodata.gx8002_resident_platform_gate_25080
      .rodata.gx8002_resident_platform_read_24810)
    *(.text.g2_codec_critical_save .text.g2_codec_critical_restore)
  } > RES
  .res.irq 0x10025574 : { KEEP(*(.text.gx8002_resident_irq_compact_entry_25574)) } > RES
  .res.text : {
    *(.text.gx8002_resident_* .rodata.gx8002_resident_*)
    /* W18: generically named functions whose stock bodies are in image-A SRAM
       (corpus image_a_sram/decomp/<addr>.c exists for each): critical_save 0x10025560,
       critical_restore 0x1002556c, header_sync 0x10025664, timestamp 0x10025930
       (helper 0x1002585c), queue_enqueue 0x100261b8, cache_lines (shared walk of 0x10025608/0x100256c0).
       W17 had them in XIP. */
    *(.text.g2_codec_header_sync)
    *(.text.g2_codec_timestamp .text.g2_codec_queue_enqueue .text.gx8002_cache_lines)
    *(.text)
    *(.gx8002.clock_boot.*)
    . = ALIGN(4);
  } > RES
  .pin.gx8002.flash_state.264e4 0x100264e4 : { KEEP(*(.gx8002.flash_state.264e4)) } > RES
  .pin.gx8002.flash_api.26504 0x10026504 : { KEEP(*(.gx8002.flash_api.26504)) } > RES
  .pin.gx8002.otp_protect.2657c 0x1002657c : { KEEP(*(.gx8002.otp_protect.2657c)) } > RES
  .pin.gx8002.otp_protect.265a4 0x100265a4 : { KEEP(*(.gx8002.otp_protect.265a4)) } > RES
  .pin.gx8002.otp_protect.265dc 0x100265dc : { KEEP(*(.gx8002.otp_protect.265dc)) } > RES
  .pin.gx8002.flash_catalog.26624 0x10026624 : { KEEP(*(.gx8002.flash_catalog.26624)) } > RES
  .pin.gx8002.flash_otp_config.266cc 0x100266cc : { KEEP(*(.gx8002.flash_otp_config.266cc)) } > RES
  .pin.gx8002.module_table.266e0 0x100266e0 : { KEEP(*(.gx8002.module_table.266e0)) } > RES
  .pin.gx8002.module_config.26880 0x10026880 : { KEEP(*(.gx8002.module_config.26880)) } > RES
  .pin.gx8002.clock_defaults.268c8 0x100268c8 : { KEEP(*(.gx8002.clock_defaults.268c8)) } > RES
  .pin.gx8002.clock_sources.26904 0x10026904 : { KEEP(*(.gx8002.clock_sources.26904)) } > RES
  .pin.gx8002.clock_sources.26954 0x10026954 : { KEEP(*(.gx8002.clock_sources.26954)) } > RES
  .pin.gx8002.board_state.269a4 0x100269a4 : { KEEP(*(.gx8002.board_state.269a4)) } > RES
  .pin.gx8002.uart_channels.26a94 0x10026a94 : { KEEP(*(.gx8002.uart_channels.26a94)) } > RES
  /* Stock image-A SRAM: AOUT route, dispatch, and hardware settings occupy
     the exact gap between the UART channel table and receive configuration. */
  .pin.gx8002.aout_context.26b94 0x10026b94 : { KEEP(*(.gx8002.sram.aout_context)) } > RES
  .pin.gx8002.aout_operations.26bc8 0x10026bc8 : { KEEP(*(.gx8002.sram.aout_operations)) } > RES
  .pin.gx8002.aout_configuration.26c1c 0x10026c1c : { KEEP(*(.gx8002.sram.aout_configuration)) } > RES
  .pin.gx8002.uart_rx_config.26c74 0x10026c74 : { KEEP(*(.gx8002.uart_rx_config.26c74)) } > RES
  .pin.gx8002.kws_keywords.26c7c 0x10026c7c : { KEEP(*(.gx8002.kws_keywords.26c7c)) } > RES
  .pin.gx8002.sample_prestate.26d2c 0x10026d2c : { KEEP(*(.gx8002.sample_prestate.26d2c)) } > RES
  .pin.gx8002.sample_registration.26d30 0x10026d30 : { KEEP(*(.gx8002.sample_registration.26d30)) } > RES
  .pin.gx8002.request_initial.26d5c 0x10026d5c : { KEEP(*(.gx8002.request_initial.26d5c)) } > RES
  .res.data : { *(.data .gx8002.sram.*) . = ALIGN(4); } > RES
  .pinb.gx8002.flash_protection_maps.26ff8 0x10026ff8 (NOLOAD) : { KEEP(*(.bss.gx8002.flash_protection_maps.26ff8)) } > RES
  .res.bss (NOLOAD) : { __bss_start = .; *(.bss) . = ALIGN(4); __bss_end = .; } > RES

  /DISCARD/ : { *(.text.csky_*) }

  .xip : {
    *(.text.gx8002_xip_* .rodata.gx8002_xip_* .gx8002.xip.*)
    *(.text.* .rodata .rodata.* .gx8002.*)
    . = ALIGN(4);
  } > XIP

  .bss.other (NOLOAD) : { *(.bss.* COMMON) } > DRAM
}

ASSERT(SIZEOF(.pin.gx8002.aout_context.26b94) == 0x34,
       "image-A AOUT context must occupy 0x10026b94..0x10026bc8")
ASSERT(SIZEOF(.pin.gx8002.aout_operations.26bc8) == 0x54,
       "image-A AOUT operations must occupy 0x10026bc8..0x10026c1c")
ASSERT(SIZEOF(.pin.gx8002.aout_configuration.26c1c) == 0x58,
       "image-A AOUT configuration must occupy 0x10026c1c..0x10026c74")
ASSERT(gx8002_resident_reset_entry_23500 == 0x10023500,
       "image-A reset vector target changed")
ASSERT(gx8002_resident_exception_bridge_23640 == 0x10023640,
       "image-A exception vector target changed")
ASSERT(gx8002_resident_irq_compact_entry_25574 == 0x10025574,
       "image-A IRQ vector target changed")
ASSERT(SIZEOF(.xip) <= 0x8e84,
       "image-A XIP exceeds the locked 36484-byte section")
