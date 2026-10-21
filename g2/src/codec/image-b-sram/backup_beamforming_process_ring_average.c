/* Native process 0x1000d656..0x1000d6b4, one pass of the repeated stage
 * body. The caller's d5a0 edge recomputes/clears the current ring row before
 * each pass; this leaf owns only the average, flag and counter transition.
 */
#include <stdint.h>

void gx8002_image_b_process_ring_average_verified_chunk(
    const uint32_t *ctx, uint32_t stage_index,
    volatile uint32_t *observed_ring_counter)
{
    int32_t columns=(int32_t)ctx[0x48/4];
    const int16_t *ring=(const int16_t *)(uintptr_t)ctx[0xac/4];
    int16_t *scratch=(int16_t *)(uintptr_t)ctx[0xb4/4];
    uint32_t stride=ctx[0x1c/4];
    float total=0.0f;
    for (int32_t i=0;i<columns;++i) {
        float value=(float)(uint16_t)ring[(uint32_t)i*stride+1u];
        total=total+value;
    }
    const float *threshold=(const float *)(uintptr_t)ctx[0xa8/4];
    /* Native dd6e supplies zero sum when columns is nonpositive, then
     * rejoins at d680 for the division/comparison and counter update. */
    float mean=total/(float)columns;
    if (mean<threshold[1]) {
        scratch[stage_index]=1;
        uint32_t aggregate=ctx[0x08/4];
        scratch[aggregate]=(int16_t)((uint16_t)scratch[aggregate]+1u);
    }
    *observed_ring_counter=*observed_ring_counter+1u;
}
