/* Native GSC energy adaptation prefix 0x1000ccfc..0x1000cd36.
 * This executes only when the source caller's mode word r3 is nonzero.
 * The active frame's scaled-energy row at context +0x98 is updated from
 * itself and the energy row at +0xa0. Signed shifts are arithmetic, and
 * products/addition retain native 32-bit wraparound.
 */
#include <stdint.h>

void gx8002_image_b_energy_smoothing_verified_chunk(
    const uint32_t *ctx, int32_t frame_index, int32_t mode)
{
    if (mode==0) return;
    int32_t frames=(int32_t)ctx[0x18/4];
    uint32_t offset=(uint32_t)frame_index*(uint32_t)frames*4u;
    uint32_t *scaled=(uint32_t *)(uintptr_t)(ctx[0x98/4]+offset);
    const uint32_t *energy=(const uint32_t *)(uintptr_t)(ctx[0xa0/4]+offset);
    for (int32_t i=0;i<frames;++i) {
        uint32_t old_product=scaled[i]*107u;
        int32_t previous=(int32_t)old_product>>7;
        int32_t energy_shift=(int32_t)energy[i]>>7;
        uint32_t new_product=(uint32_t)energy_shift*19u;
        int32_t fresh=(int32_t)new_product>>7;
        scaled[i]=(uint32_t)previous+(uint32_t)fresh;
    }
}
