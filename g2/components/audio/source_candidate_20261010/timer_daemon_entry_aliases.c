#include "../timer_daemon_order_offline/daemon.c"

/* Original Apollo entries 0x47e83a and 0x47e88c, with identical ABIs. */
__asm__(".global audio_timer_wrap_expire\n"
        ".set audio_timer_wrap_expire, audio_timer_expired\n"
        ".global audio_daemon_process_or_block\n"
        ".set audio_daemon_process_or_block, audio_timer_process_or_block\n");
