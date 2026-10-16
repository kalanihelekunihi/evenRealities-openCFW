/* Stock TLSF backing region zeroed by 0x5eda64 before pool creation. */
#include <stdint.h>

uint8_t g2_file_tlsf_backing_20208e70[0x70800]
    __attribute__((section(".bss.opencfw.fileheap.tlsf.backing"), aligned(16), used));

_Static_assert(sizeof(g2_file_tlsf_backing_20208e70) == 0x70800u,
               "stock TLSF backing extent");
