/* SPDX-License-Identifier: MIT */
#include <core_ck804.h>
extern void gx_icache_enable(void);
extern void gx_dcache_disable(void);
extern void gx_dcache_enable(void);

/* Recovered package 0xd1cc. The pinned Apache-2.0 CSI implementation
 * supplies the cache-region encoding and register layout. */
void open_cfw_gx8002_cache_initialize(void)
{
    gx_icache_enable();
    gx_dcache_disable();
    csi_cache_set_range(3,0x20000000u,CACHE_CRCR_256K,1);
    gx_dcache_enable();
}
