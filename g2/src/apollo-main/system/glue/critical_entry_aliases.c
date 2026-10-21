/* Build the already reconstructed port body in one translation unit, then
 * export the audio critical-section names at the same entries. No branch is
 * added before the BASEPRI mask or nested critical-count update. */
#include "../../rtos/timer/timer-wake-providers/port.c"

__asm__(".global audio_enter_critical\n"
        ".set audio_enter_critical, stock_enter_critical\n"
        ".global receiver_critical_enter\n"
        ".set receiver_critical_enter, stock_enter_critical\n"
        ".global audio_resume_enter\n"
        ".set audio_resume_enter, stock_enter_critical\n"
        ".global audio_timer_wait_enter\n"
        ".set audio_timer_wait_enter, stock_enter_critical\n"
        ".global audio_resume_exit\n"
        ".set audio_resume_exit, stock_exit_critical\n"
        ".global audio_timer_wait_exit\n"
        ".set audio_timer_wait_exit, stock_exit_critical\n"
        ".global audio_exit_critical\n.set audio_exit_critical, stock_exit_critical\n"
        ".global receiver_critical_exit\n.set receiver_critical_exit, stock_exit_critical\n");
