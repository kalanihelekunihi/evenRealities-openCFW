/* Clock recovery oscillator control enters Apollo 0x4809c4. */
#include "../../runtime/info-memory/oscillator.c"

__asm__(".global stock_mcuctrl\n"
        ".set stock_mcuctrl, audio_oscillator_control\n");
