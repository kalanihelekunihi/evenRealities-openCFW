#include <stdint.h>
#include <stdarg.h>

extern int32_t audio_log_policy(uint32_t mask);
extern int32_t audio_log_lock(void *state, uint32_t timeout);
extern void audio_log_format(uint32_t token, const char *copy, va_list args);
extern void audio_log_unlock(void *state);
extern void *audio_log_lock_state;

/* Complete local control flow of stock 0x43ce9e. Lower policy, lock,
 * formatter, unlock and RAM state remain separate source contracts. */
uint32_t audio_log_simple(uint32_t mask, const char *format, const char *copy, ...) {
    if (audio_log_policy(mask) != 0) return 0;
    uint32_t ipsr;
    __asm volatile("mrs %0, ipsr" : "=r"(ipsr));
    if (ipsr || !audio_log_lock_state) return 0;
    uint32_t token = (mask & 0xffc00000u) | ((uint32_t)(uintptr_t)format & 0x003fffffu);
    void *state = audio_log_lock_state;
    if (audio_log_lock(state, 500) == 1) {
        va_list args;
        va_start(args, copy);
        audio_log_format(token, copy, args);
        va_end(args);
        audio_log_unlock(audio_log_lock_state);
    }
    return 0;
}
