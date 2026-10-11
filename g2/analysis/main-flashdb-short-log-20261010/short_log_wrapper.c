#include <stdarg.h>
#include <stdint.h>

extern uint32_t audio_log_policy(uint32_t token);
extern uint32_t audio_lock_take(uint32_t lock, uint32_t timeout);
extern void audio_lock_give(uint32_t lock);
extern void audio_log_short_format(uint32_t token, const char *format, const uint32_t *args);
extern volatile uint32_t audio_log_lock_state;

/* Stock 0x43ce9e: event logging gate and ARM register/stack varargs bridge. */
uint32_t g2_flashdb_candidate_compress(uint32_t token, uint32_t category,
                                        const char *format, ...)
{
    va_list args;
    va_start(args, format);
    uint32_t ipsr;
    if (audio_log_policy(token) != 0u)
        return 0u;
    __asm volatile("mrs %0, ipsr" : "=r"(ipsr));
    if (ipsr != 0u)
        return 0u;
    uint32_t lock = audio_log_lock_state;
    if (lock == 0u)
        return 0u;
    uint32_t merged = (token & 0xffc00000u) | (category & 0x003fffffu);
    if (audio_lock_take(lock, 500u) == 1u) {
        audio_log_short_format(merged, format,
                               *(const uint32_t * const *)(const void *)&args);
        audio_lock_give(audio_log_lock_state);
    }
    va_end(args);
    return 0u;
}
