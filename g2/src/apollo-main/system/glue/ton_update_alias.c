/* The early PCM callers use the original TON dispatch entry directly. */
#include "../../audio/early-pcm/early-pcm-dispatch/dispatch.c"

__asm__(".global stock_ton_update\n.set stock_ton_update, pcm_ton_dispatch\n");
