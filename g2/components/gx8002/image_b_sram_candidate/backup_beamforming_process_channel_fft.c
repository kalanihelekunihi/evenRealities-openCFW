/* Native process 0x1000dbc2..0x1000dc94, from peak through inverse real
 * FFT and output shift. The peak-headroom decoder maps the highest set
 * magnitude bit 14..0 to shifts 0..14, with 15 for zero. The descriptor at
 * runtime 0x2001700c is source-owned. First-use RAM state remains caller
 * supplied; no initial value is invented by this process slice.
 */
#include <stdint.h>
#include "backup_fft_profile.h"

extern const image_b_rfft_q15 gx8002_image_b_rifft_profile_2001700c;
extern void gx8002_image_b_dsp_peak_1000f134(
    const int16_t *,int16_t *,uint32_t);
extern void gx8002_image_b_dsp_shift_1000f0c0(
    const int16_t *,int32_t,int16_t *,uint32_t);
extern void gx8002_image_b_energy_whole_experimental(
    const uint32_t *,int16_t *,int32_t,int32_t,volatile uint32_t *);
extern void gx8002_image_b_rfft_1000ef64(
    const image_b_rfft_q15 *,int16_t *,int16_t *);

int32_t gx8002_image_b_process_channel_fft_verified_chunk(
    const uint32_t *ctx,int16_t *channel_samples,uint32_t channel_index,
    volatile uint32_t *energy_first_use_word)
{
    int16_t peak_word=0;
    gx8002_image_b_dsp_peak_1000f134(
        channel_samples,&peak_word,ctx[0x18/4]*2u);
    uint16_t peak=(uint16_t)peak_word;
    int32_t headroom=15;
    for (int32_t bit=14;bit>=0;--bit) {
        if ((peak&(uint16_t)(1u<<bit))!=0u) {
            headroom=14-bit;
            break;
        }
    }
    gx8002_image_b_dsp_shift_1000f0c0(
        channel_samples,headroom,channel_samples,ctx[0x18/4]*2u);
    const uint16_t *active=(const uint16_t *)(uintptr_t)ctx[0xb4/4];
    gx8002_image_b_energy_whole_experimental(
        ctx,channel_samples,0,(int32_t)active[channel_index],
        energy_first_use_word);
    int16_t *transformed=(int16_t *)(uintptr_t)ctx[0x84/4];
    gx8002_image_b_rfft_1000ef64(
        &gx8002_image_b_rifft_profile_2001700c,
        channel_samples,transformed);
    const uint16_t *output_shift=(const uint16_t *)(uintptr_t)ctx[0x94/4];
    int32_t final_shift=(int8_t)(uint8_t)
        (9u-(uint32_t)output_shift[channel_index]-(uint32_t)headroom);
    gx8002_image_b_dsp_shift_1000f0c0(
        transformed,final_shift,transformed,ctx[0x14/4]);
    return headroom;
}
