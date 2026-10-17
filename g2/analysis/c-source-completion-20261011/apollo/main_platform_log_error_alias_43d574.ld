/* UART instance error logging reaches native 0x43d574 with the same six
 * positional arguments as the selected audio_log_extended C provider.
 * The old UART source prototype's local parameter names are misleading;
 * the literal at 0x7846e4 is the function name and 0x75c1c8 is format. */
INCLUDE "g2/analysis/c-source-completion-20261011/apollo/main_combined_ram_scratch_20261016.ld"
PROVIDE(platform_log_error = audio_log_extended);
ASSERT(platform_log_error == audio_log_extended,
       "UART detailed logger must share extended logger body");
