#include <stdint.h>
/* SDK object extents independently bound through native defaults and accessor.
 * Dedicated BSS sections expose required stock placement to the final linker.
 * This relocatable source does not establish placement or runtime ownership. */
_Alignas(4) uint8_t opencfw_em9305_scan_context_8035dc[704]
    __attribute__((section(".bss.opencfw_scan_context_8035dc")));
_Alignas(4) uint8_t opencfw_em9305_scan_context_802a60[704]
    __attribute__((section(".bss.opencfw_scan_context_802a60")));
_Alignas(4) uint8_t opencfw_em9305_scan_context_80389c[704]
    __attribute__((section(".bss.opencfw_scan_context_80389c")));
uint8_t *const opencfw_em9305_stream_objects_3357b4[3] = {
    opencfw_em9305_scan_context_8035dc,
    opencfw_em9305_scan_context_802a60,
    opencfw_em9305_scan_context_80389c,
};
_Static_assert(sizeof(opencfw_em9305_scan_context_8035dc) == 704, "context extent");
_Static_assert(sizeof(opencfw_em9305_stream_objects_3357b4) == 12, "ARC pointer table extent");
