/* The newer caller's apply callback resolves to the original step entry. */
#include "../platform-callbacks/route.c"

__asm__(".global callback_apply\n.set callback_apply, audio_platform_step\n");
