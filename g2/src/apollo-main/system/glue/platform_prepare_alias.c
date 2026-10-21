/* Direct caller name for the validated platform prepare-state entry. */
#include "../platform-callbacks/prepare.c"

__asm__(".global callback_prepare_state\n"
        ".set callback_prepare_state, audio_platform_prepare_state\n"
        ".global stock_stimer_running\n"
        ".set stock_stimer_running, audio_platform_auxiliary_active\n");
