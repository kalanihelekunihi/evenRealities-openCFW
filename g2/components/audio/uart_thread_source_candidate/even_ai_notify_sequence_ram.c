/* Stock local EvenAI notification sequence byte at 0x20074ff9. */
#include <stdint.h>

uint8_t audio_even_ai_notify_sequence_20074ff9
    __attribute__((section(".bss.opencfw.evenai.notify.sequence"), used));
