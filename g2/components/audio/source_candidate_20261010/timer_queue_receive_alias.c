#include "../queue_cmsis_offline/queue.c"

/* Timer command drain uses original xQueueReceive entry 0x441b0a. */
__asm__(".global audio_timer_queue_receive\n"
        ".set audio_timer_queue_receive, xQueueReceive\n");
