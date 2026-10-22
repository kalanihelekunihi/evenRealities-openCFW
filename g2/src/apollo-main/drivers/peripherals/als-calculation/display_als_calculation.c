/* Native ALS curve update 0x4add8c..0x4addb5. The curve helpers 0x4add02/30/6a
 * and ROM table 0x730e24 are owned by drivers/peripherals/als-driver. */
#include <stdint.h>
#include "g2_als.h"
extern uint32_t audio_als_curve_index; /* RAM 0x200741e4 */
extern uint32_t audio_als_curve_nominal; /* RAM 0x200741e8 */
extern uint32_t audio_als_curve_adjusted; /* RAM 0x200741ec */
void audio_als_apply_previous(uint32_t prior) {
    audio_als_curve_index=als_function_14(prior);
    audio_als_curve_nominal=als_function_16(prior);
    audio_als_curve_adjusted=als_function_18(audio_als_curve_index);
}
