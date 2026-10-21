/* Export the validated early and middle PCM entries under callback names. */
#include "../../graphics/early-pcm/early-pcm-gpu/gpu.c"

__asm__(".global early_other\n.set early_other, pcm_early_on\n"
        ".global early_zero\n.set early_zero, pcm_early_off\n"
        ".global middle_action0\n.set middle_action0, pcm_sleep\n"
        ".global middle_action2\n.set middle_action2, pcm_temperature\n"
        ".global middle_other\n.set middle_other, pcm_middle_on\n"
        ".global middle_zero\n.set middle_zero, pcm_middle_off\n");
