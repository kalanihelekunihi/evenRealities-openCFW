/* Apollo MAIN 0x442030: timer daemon's diagnostic name is the same entry
 * as the independently verified queue restricted-wait source. */
#include "../../rtos/timer/timer-queue-wait.c"
__asm__(".global stock_queue_restricted_wait\n"
        ".set stock_queue_restricted_wait, audio_timer_restricted_wait\n");
