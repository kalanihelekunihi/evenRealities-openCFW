#include <stdint.h>

/* Original 0x454d7c: load literal 0x20074a58, load word, increment,
 * store word, return. No interrupt mask operation is present in the body. */
void audio_suspend(void) {
    volatile uint32_t *const suspended = (volatile uint32_t *)(uintptr_t)0x20074a58u;
    *suspended = *suspended + 1u;
}
void audio_aux_suspend(void) __attribute__((alias("audio_suspend")));
void receiver_suspend(void) __attribute__((alias("audio_suspend")));
