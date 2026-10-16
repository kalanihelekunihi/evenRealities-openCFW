/* Stock Apollo Main ALS manual target update, 0x4ade36..0x4adec4. */
#include <stdint.h>

extern uint32_t audio_als_curve_nominal; /* stock RAM 0x200741e8 */
extern uint32_t audio_als_scale_active; /* stock RAM 0x20000064 */
extern uint32_t audio_als_scale_shadow; /* stock RAM 0x20000068 */
extern uint32_t audio_als_recompute_pending; /* stock RAM 0x20074200 */
uint32_t audio_als_manual_target_count; /* stock RAM 0x200741fc */
extern uint32_t audio_als_first_curve_percent_4ad9e2(void);
extern uint32_t audio_als_manual_target_scale_4addb6(uint32_t, uint32_t);

void audio_als_manual_set_target_4ade36(uint32_t level)
{
    if (audio_als_first_curve_percent_4ad9e2() < audio_als_curve_nominal) {
        uint32_t target = audio_als_manual_target_scale_4addb6(
            audio_als_curve_nominal, level);
        uint32_t mixed = (audio_als_scale_active * 30u + target * 70u) / 100u;
        if (mixed < 615u)
            mixed = 614u;
        if (mixed >= 1434u)
            mixed = 1434u;
        audio_als_scale_active = mixed;
        ++audio_als_manual_target_count;
        audio_als_scale_shadow = target;
        audio_als_recompute_pending = 0u;
    } else {
        audio_als_recompute_pending = 1u;
        audio_als_scale_shadow = 1024u;
    }
}
