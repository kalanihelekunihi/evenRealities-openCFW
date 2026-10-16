/* Two stock pointer cells shared by file heap alloc/free/realloc. */
#include <stdint.h>

void *g2_codec_heap_mutex
    __attribute__((section(".bss.opencfw.fileheap.mutex"), aligned(4), used));
void *g2_codec_heap_pool
    __attribute__((section(".bss.opencfw.fileheap.pool"), aligned(4), used));

_Static_assert(sizeof(g2_codec_heap_mutex) == 4u, "Cortex-M pointer cell");
_Static_assert(sizeof(g2_codec_heap_pool) == 4u, "Cortex-M pointer cell");
