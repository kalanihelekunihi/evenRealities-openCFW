#include "../../drivers/codec-host/i2s-stop/stop.c"

/* Diagnostic callback uses the same Apollo 0x590c62 entry. */
__asm__(".global audio_i2s_dma_stop\n"
        ".set audio_i2s_dma_stop, audio_i2s_dma_stop_selected\n");
