/* Shared original timer-stop entry under the PCM2.1 caller name. */
#include "../../audio/transition-timer/transition.c"

__asm__(".global stock_timer_stop\n.set stock_timer_stop, pcm22_timer_stop\n");
