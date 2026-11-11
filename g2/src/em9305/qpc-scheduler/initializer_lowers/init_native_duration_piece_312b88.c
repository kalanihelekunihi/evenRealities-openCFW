#include <stdint.h>

/* Native 0x312b88..0x312bb2: air time in microseconds of a packet with
 * length payload bytes on a PHY: 2M (phy 2) 36 + 4 * length; coded
 * (phy 3) (27 + 8 * length) * (2 for S=2 when coded == 1, else 8) + 376;
 * otherwise (1M) 64 + 8 * length. All arithmetic wraps modulo 2^32 as in
 * the stock 32x16 multiply. */
uint32_t opencfw_em9305_radio_duration_piece_312b88(uint32_t phy,uint32_t coded,
                                                    uint32_t length)
{
    if(phy==2u)return 36u+(length<<2);
    if(phy==3u)return (27u+(length<<3))*(coded==1u?2u:8u)+376u;
    return (length<<3)+64u;
}
