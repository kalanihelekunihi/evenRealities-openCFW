/* Direct caller names for the validated PCM2.1 children. */
#include "../../audio/pcm21/pcm21-children/children.c"

__asm__(".global stock_prepare\n.set stock_prepare, pcm21_prepare\n"
        ".global stock_change_state\n.set stock_change_state, pcm21_change_state\n"
        ".global stock_plan\n.set stock_plan, pcm21_plan\n");
