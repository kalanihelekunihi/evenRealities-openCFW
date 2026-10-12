/* Strict image-B source co-placement probe. Authenticated initialized
 * records and native RAM aliases remain at their stock offsets. This probe
 * may fail until source text/rodata fit before the first fixed record;
 * failure is preferable to silently overlapping live initialized data. */
ENTRY(gx8002_image_b_reset_10003100)
SECTIONS
{
  .vectors 0x10003000 : { KEEP(*(.vectors.image_b)) }
  .text 0x10003100 : {
    KEEP(*(.text.image_b_reset))
    *(.text*)
  }
  __source_rodata_start = ALIGN(ADDR(.text) + SIZEOF(.text), 4);

  .rifft_profile 0x2001700c : AT(0x1001700c) {
    KEEP(*(.rodata.gx8002_image_b_rifft_profile_2001700c))
  }
  .rfft_profile 0x20017020 : AT(0x10017020) {
    KEEP(*(.rodata.gx8002_image_b_rfft_profile_20017020))
  }
  .rodata __source_rodata_start : { *(.rodata*) }
  .clock_state 0x200168c0 : AT(0x100168c0) {
    KEEP(*(.data.image_b.clock_state))
  }
  .clock_boot_records 0x200168fc : AT(0x100168fc) {
    KEEP(*(.data.image_b.clock_boot_records))
  }
  .clock_trim_records 0x2001694c : AT(0x1001694c) {
    KEEP(*(.data.image_b.clock_trim_records))
  }
  .clock_param 0x2001699c : AT(0x1001699c) {
    KEEP(*(.data.gx_clock_param_table))
  }
  .clock_dto 0x20016b3c : AT(0x10016b3c) {
    KEEP(*(.data.gx_clock_dto_table))
  }
  .clock_div 0x20016b40 : AT(0x10016b40) {
    KEEP(*(.data.gx_clock_div_table))
  }
  .uart0_record 0x20016b84 : AT(0x10016b84) {
    KEEP(*(.data.image_b.uart0_record))
  }
  .uart1_record 0x20016c04 : AT(0x10016c04) {
    KEEP(*(.data.image_b.uart1_record))
  }
  .audio_out_root 0x20016c84 : AT(0x10016c84) {
    KEEP(*(.data.image_b.audio_out_root))
  }
  .audio_out_callback_table 0x20016cb8 : AT(0x10016cb8) {
    KEEP(*(.data.image_b.audio_out_callback_table))
  }
  .audio_out_state 0x20016d0c : AT(0x10016d0c) {
    KEEP(*(.data.image_b.audio_out_state))
  }
  .flash_descriptor 0x20016d60 : AT(0x10016d60) {
    KEEP(*(.data.image_b.flash_descriptor))
  }
  .flash_callback_table 0x20016d80 : AT(0x10016d80) {
    KEEP(*(.data.image_b.flash_callback_table))
  }
  .flash_protection_p25q21l 0x20016dfc : AT(0x10016dfc) {
    KEEP(*(.data.image_b.flash_protection_p25q21l))
  }
  .flash_protection_p25q40l 0x20016e24 : AT(0x10016e24) {
    KEEP(*(.data.image_b.flash_protection_p25q40l))
  }
  .flash_protection_p25q80l 0x20016e5c : AT(0x10016e5c) {
    KEEP(*(.data.image_b.flash_protection_p25q80l))
  }
  .flash_profiles 0x20016ea4 : AT(0x10016ea4) {
    KEEP(*(.data.image_b.flash_profiles))
  }
  .flash_geometry 0x20016f4c : AT(0x10016f4c) {
    KEEP(*(.data.image_b.flash_geometry))
  }
  .gsensor_state 0x20016f60 : AT(0x10016f60) {
    KEEP(*(.data.gx8002_image_b_gsensor_workstate_20016f60))
  }
  .audio_runtime_state 0x20016f64 : AT(0x10016f64) {
    KEEP(*(.data.image_b.audio_runtime_state))
  }
  .sample_app_pointer 0x20016f74 : AT(0x10016f74) {
    KEEP(*(.data.image_b.sample_app_pointer))
  }
  .sample_app_record 0x20016f78 : AT(0x10016f78) {
    KEEP(*(.data.image_b.sample_app))
  }
  .audio_uart_tx 0x20016f98 : AT(0x10016f98) {
    KEEP(*(.data.image_b.audio_uart_tx))
  }
  .imcra_profile 0x20016fb8 : AT(0x10016fb8) {
    KEEP(*(.data.gx8002_image_b_imcra_cfg_words_20016fb8))
  }
  .kernel_coefficients 0x20017034 : AT(0x10017034) {
    KEEP(*(.data.image_b.kernel_coefficients))
  }
  .data : { *(.data*) }
  .bss 0x20017090 (NOLOAD) : {
    *(.bss*) *(COMMON)
    /* Stock 0x10003128 clears this entire exact interval. Reserve the
     * unknown interior as uninitialized SRAM, without invented field data. */
    . = 0x1670c;
  }

  .image_b_retained.energy 0x2002d79c (NOLOAD) : {
    KEEP(*(.image_b_retained.energy))
  }
  .image_b_retained.ring 0x2002d7a0 (NOLOAD) : {
    KEEP(*(.image_b_retained.ring))
  }
  .image_b_retained.dsp_operations 0x2002d7a4 (NOLOAD) : {
    KEEP(*(.image_b_retained.dsp_operations))
  }
  .image_b_retained.imcra_setting 0x2002d7b4 (NOLOAD) : {
    KEEP(*(.image_b_retained.imcra_setting))
  }
  /* Experimental post-BSS IRAM source island. Stock stage2 loader size is
   * insufficient until packaging/loader ownership is separately qualified.
   * 0x2002d79c..0x2002d7b8 is retained data; stack top is 0x2002fffc. */
  .late_audio 0x1002d800 : AT(0x1002d800) {
    KEEP(*(.image_b_late_audio))
  }
}
PROVIDE(gx8002_image_b_bss_start = 0x20017090);
PROVIDE(gx8002_image_b_bss_end = 0x2002d79c);
/* Named source-owned slots inside the authenticated reset-zero interval.
 * These aliases bind typed C lvalues to their native RAM addresses. The
 * encompassing .bss reservation owns capacity; no initial value is supplied.
 */
PROVIDE(gx8002_image_b_exception_scratch_20017390 = 0x20017390);
PROVIDE(gx8002_image_b_clock_gate_bits_20017394 = 0x20017394);
PROVIDE(gx8002_image_b_console_port_2001739c = 0x2001739c);
PROVIDE(gx8002_image_b_gpio_irq_masks_200173a0 = 0x200173a0);
PROVIDE(gx8002_image_b_irq_descriptors_200173a8 = 0x200173a8);
PROVIDE(gx8002_image_b_timer_records_200174bc = 0x200174bc);
PROVIDE(gx8002_image_b_flash_probe_state_2001765c = 0x2001765c);
PROVIDE(gx8002_image_b_spi_device_state_20017670 = 0x20017670);
PROVIDE(gx8002_image_b_board_pins_ready_200176d8 = 0x200176d8);
PROVIDE(gx8002_image_b_pmu_record_2002cb88 = 0x2002cb88);
PROVIDE(gx8002_image_b_denoise_mode_state_2002d2bc = 0x2002d2bc);
PROVIDE(gx8002_image_b_denoise_ring_2002d2d8 = 0x2002d2d8);
/* These four words/records lie before the stage2 initialized-data span.
 * Their addresses are authenticated; their stage1/resident producer and
 * initial values are still external contracts, never invented here. */
ASSERT(gx8002_image_b_reset_10003100 == 0x10003100,
       "source reset entry offset");
ASSERT(SIZEOF(.vectors) == 0x100, "vector extent");
ASSERT(ADDR(.rodata) + SIZEOF(.rodata) <= 0x100168c0,
       "source rodata overlaps fixed initialized clock state");
ASSERT(SIZEOF(.clock_state) == 60, "clock runtime state extent");
ASSERT(SIZEOF(.clock_boot_records) == 80, "clock boot record extent");
ASSERT(SIZEOF(.clock_trim_records) == 80, "clock trim record extent");
ASSERT(SIZEOF(.clock_param) == 0x1a0, "clock param extent");
ASSERT(SIZEOF(.clock_dto) == 3, "clock DTO extent");
ASSERT(SIZEOF(.clock_div) == 0x44, "clock div extent");
ASSERT(SIZEOF(.uart0_record) == 128, "UART0 record extent");
ASSERT(SIZEOF(.uart1_record) == 128, "UART1 record extent");
ASSERT(SIZEOF(.audio_out_root) == 52, "audio output root extent");
ASSERT(SIZEOF(.audio_out_callback_table) == 84, "audio output callback table extent");
ASSERT(SIZEOF(.audio_out_state) == 84, "audio output state extent");
ASSERT(SIZEOF(.flash_descriptor) == 32, "flash descriptor extent");
ASSERT(SIZEOF(.flash_callback_table) == 124, "flash callback table extent");
ASSERT(SIZEOF(.flash_protection_p25q21l) == 40, "flash protection 21L extent");
ASSERT(SIZEOF(.flash_protection_p25q40l) == 56, "flash protection 40L extent");
ASSERT(SIZEOF(.flash_protection_p25q80l) == 72, "flash protection 80L extent");
ASSERT(SIZEOF(.flash_profiles) == 168, "flash profile extent");
ASSERT(SIZEOF(.flash_geometry) == 20, "flash geometry extent");
ASSERT(SIZEOF(.gsensor_state) == 4, "gsensor extent");
ASSERT(SIZEOF(.audio_runtime_state) == 16, "audio state extent");
ASSERT(SIZEOF(.sample_app_pointer) == 4, "app selector extent");
ASSERT(SIZEOF(.sample_app_record) == 32, "app record extent");
ASSERT(SIZEOF(.audio_uart_tx) == 32, "audio UART TX extent");
ASSERT(SIZEOF(.imcra_profile) == 84, "IMCRA profile extent");
ASSERT(SIZEOF(.rifft_profile) == 20, "RIFFT descriptor extent");
ASSERT(SIZEOF(.rfft_profile) == 20, "RFFT descriptor extent");
ASSERT(SIZEOF(.kernel_coefficients) == 88, "kernel coefficient extent");
ASSERT(SIZEOF(.data) == 0, "unexpected initialized data");
ASSERT(SIZEOF(.bss) == 0x1670c, "stock BSS clear/reservation extent");
ASSERT(SIZEOF(.image_b_retained.energy) == 4, "energy cell extent");
ASSERT(SIZEOF(.image_b_retained.ring) == 4, "ring cell extent");
ASSERT(SIZEOF(.image_b_retained.dsp_operations) == 16, "DSP table extent");
ASSERT(SIZEOF(.image_b_retained.imcra_setting) == 4, "IMCRA cell extent");

ASSERT(ADDR(.late_audio) == 0x1002d800, "late audio start");
ASSERT(ADDR(.late_audio) + SIZEOF(.late_audio) <= 0x1002e800,
       "late audio exceeds reserved post-BSS island");
