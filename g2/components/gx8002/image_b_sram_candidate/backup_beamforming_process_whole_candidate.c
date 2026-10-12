/* Experimental complete C entry composition for native 0x1000d46c.
 * The two source-owned product RAM words (ring counter, energy first-use)
 * are explicit parameters here. The stock four-register entry binds them
 * through fixed RAM ownership; this experimental ABI is not an admission
 * of whole-image source or original-call equivalence.
 */
#include <stdint.h>

struct gx8002_image_b_process_band {
    uint32_t mode_count,coefficient_bytes,band_index,active_stages;
};
struct gx8002_image_b_process_prepare {
    uint32_t first_threshold_address,second_threshold_address;
    uint32_t coefficient_address,ring_row_address;
};
extern void gx8002_image_b_process_band_verified_chunk(
    const uint32_t *,struct gx8002_image_b_process_band *);
extern void gx8002_image_b_process_prepare_verified_chunk(
    const uint32_t *,uint32_t,uint32_t,int32_t,
    struct gx8002_image_b_process_prepare *);
extern void gx8002_image_b_process_thresholds_verified_chunk(
    const int16_t *,const int16_t *,const float *,int16_t *,
    int32_t,int32_t);
extern void gx8002_image_b_process_ring_average_verified_chunk(
    const uint32_t *,uint32_t,volatile uint32_t *);
extern void gx8002_image_b_dsp_clear_1000f1ac(
    uint32_t,int16_t *,uint32_t);
extern void gx8002_image_b_process_post_ring_experimental(
    const uint32_t *,uint8_t *,uint32_t,volatile uint32_t *);

void gx8002_image_b_process_whole_experimental(
    const uint32_t *ctx,uint8_t *caller_output,
    uint32_t unused_r2,uint32_t output_frame_index,
    volatile uint32_t *observed_ring_counter,
    volatile uint32_t *energy_first_use_word)
{
    (void)unused_r2;
    struct gx8002_image_b_process_band band;
    gx8002_image_b_process_band_verified_chunk(ctx,&band);
    struct gx8002_image_b_process_prepare prep;
    int32_t stages=(int32_t)ctx[0x08/4];
    gx8002_image_b_process_prepare_verified_chunk(
        ctx,*observed_ring_counter,band.mode_count,stages,&prep);
    uint32_t first=prep.first_threshold_address;
    uint32_t second=prep.second_threshold_address;
    uint32_t spectrum_stride=ctx[0x18/4]*4u;
    for (int32_t stage=0;stage<stages;++stage) {
        uint32_t ring_row;
        if (stage==0) {
            ring_row=prep.ring_row_address;
        } else {
            uint32_t counter=*observed_ring_counter;
            uint32_t row=counter%ctx[0x48/4];
            ring_row=ctx[0xac/4]+row*ctx[0x1c/4]*2u;
            gx8002_image_b_dsp_clear_1000f1ac(
                0u,(int16_t *)(uintptr_t)ring_row,ctx[0x1c/4]);
        }
        gx8002_image_b_process_thresholds_verified_chunk(
            (const int16_t *)(uintptr_t)first,
            (const int16_t *)(uintptr_t)second,
            (const float *)(uintptr_t)prep.coefficient_address,
            (int16_t *)(uintptr_t)ring_row,
            (int32_t)band.mode_count,(int32_t)band.band_index);
        first+=spectrum_stride;
        second+=spectrum_stride;
        gx8002_image_b_process_ring_average_verified_chunk(
            ctx,(uint32_t)stage,observed_ring_counter);
    }
    gx8002_image_b_process_post_ring_experimental(
        ctx,caller_output,output_frame_index,energy_first_use_word);
}
