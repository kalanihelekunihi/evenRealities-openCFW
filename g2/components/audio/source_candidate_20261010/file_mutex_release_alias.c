/* File-close caller shares Apollo MAIN osMutexRelease entry 0x44981C. */
#include "../semaphore_take_offline/take.c"

__asm__(".global audio_file_mutex_release\n"
        ".set audio_file_mutex_release, audio_mutex_release\n"
        ".global audio_file_mutex_acquire\n"
        ".set audio_file_mutex_acquire, audio_mutex_acquire\n"
        ".global audio_log_lock\n"
        ".set audio_log_lock, xQueueTakeMutexRecursive\n"
        ".global audio_log_unlock\n"
        ".set audio_log_unlock, xQueueGiveMutexRecursive\n");
