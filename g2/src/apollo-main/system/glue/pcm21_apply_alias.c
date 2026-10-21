/* Direct caller name for the validated PCM2.1 apply entry. */
#include "../../audio/pcm21/pcm21-children/apply.c"

__asm__(".global stock_apply\n.set stock_apply, pcm21_apply\n");
