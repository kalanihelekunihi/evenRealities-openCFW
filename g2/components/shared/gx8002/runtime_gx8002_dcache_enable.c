/* SPDX-License-Identifier: MIT */
/* The pinned Apache-2.0 C-SKY CSI header supplies the implementation.
 * Its generated section matches the GX8002 stock function byte for byte.
 * Keep barriers and invalidation ordering in the upstream implementation.
 */
#include <core_ck804.h>

void gx_dcache_enable(void)
{
    csi_dcache_enable();
}
