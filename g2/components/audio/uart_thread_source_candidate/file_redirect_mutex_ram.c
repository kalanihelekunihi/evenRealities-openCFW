/* Companion redirect mutex pointer cell initialized at stock 0x474d9c. */
#include <stdint.h>

void *g2_codec_redirect_mutex
    __attribute__((section(".bss.opencfw.fileheap.redirect_mutex"), aligned(4), used));
_Static_assert(sizeof(g2_codec_redirect_mutex) == 4u, "stock pointer cell");
