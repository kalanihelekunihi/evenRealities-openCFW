/* Recovered main-image failure/logger wrapper, not full formatter attribution. */
#include <stdint.h>
#include <stdarg.h>
/* Stock-RAM literals rewritten to named objects (sim-test wave 2026-10-26,
 * .waves/sim-fix/apply.py): g2ref_X is the linker symbol X. */
#include <stdint.h>
extern unsigned char g2ref_audio_uart_stdio_print_char_cell_200742f0[] __asm__("audio_uart_stdio_print_char_cell_200742f0");
extern unsigned char g2ref_g2_flashdb_print_buffer[] __asm__("g2_flashdb_print_buffer");
extern uint32_t audio_heap_formatter(char *,const char *,va_list);
/* audio_heap_log is an alias of audio_sdk_printf (am_util_stdio_printf) in
 * system/log/main-formatter/format.c. */
extern uint32_t audio_heap_log(const char *format,...);
__attribute__((noreturn)) void audio_heap_malloc_failed(void){
 audio_heap_log("MallocFailed: cannot malloc memory\n" /* stock 0x758f70 */);
 for(;;){}
}
