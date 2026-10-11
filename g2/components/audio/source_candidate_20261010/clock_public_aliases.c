/* HAL caller names for the validated public clock request/release entries. */
#include "../clock_public_dispatch_offline/dispatch.c"

__asm__(".global am_hal_clkmgr_clock_request\n"
        ".set am_hal_clkmgr_clock_request, audio_clock_request\n"
        ".global am_hal_clkmgr_clock_release\n"
        ".set am_hal_clkmgr_clock_release, audio_clock_release\n"
        ".global audio_power_clock_acquire\n"
        ".set audio_power_clock_acquire, audio_clock_request\n"
        ".global spot_timer_clock_request\n"
        ".set spot_timer_clock_request, audio_clock_request\n"
        ".global audio_power_clock_release\n"
        ".set audio_power_clock_release, audio_clock_release\n"
        ".global audio_i2s_clock_release\n"
        ".set audio_i2s_clock_release, audio_clock_release\n");
