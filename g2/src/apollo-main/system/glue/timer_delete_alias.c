/* The selected source entry is the complete stock osTimerDelete wrapper. */
#include "../../rtos/timer/timer-aux-lifetime.c"

__asm__(".global audio_timer_delete\n"
        ".set audio_timer_delete, audio_timer_delete_selected\n");
