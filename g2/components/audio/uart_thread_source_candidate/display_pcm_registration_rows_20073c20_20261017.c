/* Two native 12-byte PCM registration rows at 0x20073c20..0x20073c37.
 * The following terminal timer state begins at 0x20073c38. */
#include <stdint.h>

__attribute__((used, aligned(4), section(".g2_bss_20073c20")))
uint32_t g2_pcm_registration_rows[2u * 3u];

_Static_assert(sizeof(g2_pcm_registration_rows) == 24u,
               "stock PCM registration extent");
