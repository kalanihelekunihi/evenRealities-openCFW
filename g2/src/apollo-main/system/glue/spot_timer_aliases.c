/* Original SPOT timer entries under PCM2.1 caller names. */
#include "../platform-callbacks/timer.c"

__asm__(".global stock_timer_init\n.set stock_timer_init, audio_spot_timer_initialize\n"
        ".global stock_timer_start\n.set stock_timer_start, audio_spot_timer_start\n"
        ".global stock_timer_restart\n.set stock_timer_restart, audio_spot_timer_restart\n");
