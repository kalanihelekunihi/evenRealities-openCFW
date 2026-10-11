/* The pending-resume import is the queue/CMSIS source's exact next-unblock
 * helper at original 0x455876. Export the same function entry. */
#include "../queue_cmsis_offline/blocking.c"

__asm__(".global audio_resume_next_unblock\n"
        ".set audio_resume_next_unblock, audio_queue_next_unblock\n");
