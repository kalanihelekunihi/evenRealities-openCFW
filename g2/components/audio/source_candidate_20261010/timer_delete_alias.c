/* The selected source entry is the complete stock osTimerDelete wrapper. */
#include "../timer_aux_lifetime_offline/aux.c"

__asm__(".global audio_timer_delete\n"
        ".set audio_timer_delete, audio_timer_delete_selected\n");
