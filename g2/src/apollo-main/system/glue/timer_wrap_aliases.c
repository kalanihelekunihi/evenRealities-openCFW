#include "../../rtos/timer/timer-wrap.c"

/* Original Apollo entries 0x47ea90 and 0x47e916. */
__asm__(".global stock_timer_switch_lists\n"
        ".set stock_timer_switch_lists, audio_timer_switch_lists_selected\n"
        ".global audio_aux_sample_time\n"
        ".set audio_aux_sample_time, audio_timer_sample_time_selected\n");
