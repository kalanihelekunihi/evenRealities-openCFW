/* Direct caller name for the validated PCM2.1 apply entry. */
#include "../pcm21_children_offline/apply.c"

__asm__(".global stock_apply\n.set stock_apply, pcm21_apply\n");
