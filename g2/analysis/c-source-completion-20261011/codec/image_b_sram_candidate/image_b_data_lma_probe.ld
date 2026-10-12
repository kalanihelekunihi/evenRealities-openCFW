/* Data-only final-link experiment. These three relocation-free typed
 * records have authenticated stock load/runtime addresses. This script
 * is not a stage2 firmware link and has no executable entry. */
SECTIONS
{
  .audio_runtime_state 0x20016f64 : AT(0x10016f64) {
    KEEP(*(.data.image_b.audio_runtime_state))
  }
  .audio_uart_tx 0x20016f98 : AT(0x10016f98) {
    KEEP(*(.data.image_b.audio_uart_tx))
  }
  .kernel_coefficients 0x20017034 : AT(0x10017034) {
    KEEP(*(.data.image_b.kernel_coefficients))
  }
}
ASSERT(SIZEOF(.audio_runtime_state) == 16, "audio state size");
ASSERT(SIZEOF(.audio_uart_tx) == 32, "TX packet size");
ASSERT(SIZEOF(.kernel_coefficients) == 88, "kernel coefficient size");
