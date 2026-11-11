#include <stdint.h>

/* Native 0x312bc0..0x312be4: per-PHY packet duration term; 1M uses
 * 262+8n, 2M uses 210+4n, coded uses 1126+64n, unknown PHYs give 150. */
uint32_t opencfw_em9305_dispatch_child_312bc0(uint32_t phy, uint32_t length)
{
    if(phy==3u)return (length<<6)+1126u;
    if(phy==2u)return 210u+(length<<2);
    if(phy==1u)return 262u+(length<<3);
    return 150u;
}
