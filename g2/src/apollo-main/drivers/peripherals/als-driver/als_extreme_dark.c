/* DRV_ALSUpdateTargetWithExtremeDarkMode, stock driver\sensor\als\als.c.
 * Native 0x4adb9a..0x4adc84; literal pool 0x4ae4d8..0x4ae4f4, 0x4ae6c4..0x4ae6cc.
 *
 * Below a filtered reading of 11 the driver enters extreme dark mode once the
 * 20-sample dark window holds at least 19 samples under 3. While active the
 * target is forced to 15% (index 0, nominal 15). Any filtered reading of 11
 * or more leaves the mode and recomputes the target from the curve. */
#include <stdint.h>
#include "g2_als.h"
#include "als_log.h"

#define EXTREME_DARK_LUX_LIMIT 11u
#define EXTREME_DARK_PERCENT 15u

static const char function[] = "DRV_ALSUpdateTargetWithExtremeDarkMode"; /* ROM 0x746d74 */
static const char exit_format[] = "ALS extreme dark mode exit, peak_value:%d"; /* ROM 0x73b7f8 */
static const char exit_short[] =
    "[sensor_als]ALS extreme dark mode exit, peak_value:%d"; /* ROM 0x71b660 */
static const char enter_format[] = "ALS extreme dark mode enter, target:%d"; /* ROM 0x746d9c */
static const char enter_short[] =
    "[sensor_als]ALS extreme dark mode enter, target:%d"; /* ROM 0x72632c */

void als_function_11(uint32_t lux)
{
    if (lux >= EXTREME_DARK_LUX_LIMIT) {
        if (g2_als_extreme_dark_active == 1u)
            ALS_LOG(3u, function, 0xc9u, 0x0c400000u, exit_format, exit_short, lux);
        g2_als_extreme_dark_active = 0u;
        audio_als_apply_previous(lux);
        return;
    }
    if (g2_als_extreme_dark_active == 0u && als_function_07()) {
        g2_als_extreme_dark_active = 1u;
        ALS_LOG(3u, function, 0xd2u, 0x0c400000u, enter_format, enter_short,
                EXTREME_DARK_PERCENT);
    }
    if (g2_als_extreme_dark_active == 1u) {
        audio_als_curve_index = 0u;
        audio_als_curve_nominal = EXTREME_DARK_PERCENT;
        audio_als_curve_adjusted = EXTREME_DARK_PERCENT;
    } else {
        audio_als_apply_previous(lux);
    }
}
