/* Diagnostic caller shares Apollo MAIN 0x4745F4 file-close entry. */
#include "../file_close_offline/close.c"

__asm__(".global audio_file_close\n"
        ".set audio_file_close, audio_file_close_selected\n");
