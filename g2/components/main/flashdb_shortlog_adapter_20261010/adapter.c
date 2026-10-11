#include <stdint.h>
/* Main FlashDB's stock call target 0x43ce9e is the same public entry as
 * audio_log_simple. A Thumb tail branch preserves r0-r3 and stack varargs. */
extern uint32_t audio_log_simple(uint32_t, const char *, const char *, ...);
__attribute__((naked)) uint32_t g2_flashdb_candidate_compress(
    uint32_t token, uint32_t category, const char *format, ...)
{
    __asm volatile("b.w audio_log_simple");
}
