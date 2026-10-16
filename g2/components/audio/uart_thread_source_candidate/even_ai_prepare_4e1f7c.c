/* Apollo main 0x4e1f7c: lazy EvenAI synchronization cell creation. */
#include <stdint.h>

extern uint32_t audio_even_ai_mutex_20074580;
extern uint32_t audio_even_ai_mutex_create_44971c(uint32_t);
extern void audio_os_interrupt_mask_5fa0a4(void);

void audio_even_ai_prepare_4e1f7c(void) {
    if (audio_even_ai_mutex_20074580 != 0u) return;
    audio_even_ai_mutex_20074580 = audio_even_ai_mutex_create_44971c(0u);
    if (audio_even_ai_mutex_20074580 == 0u) {
        audio_os_interrupt_mask_5fa0a4();
        *(volatile uint32_t *)(uintptr_t)0xffffffffu = 0u;
        for (;;) { }
    }
}
