/* DRV_ALSFilterValueByPitch, stock driver\sensor\als\als.c.
 * Native 0x4adab8..0x4adb50; literal pool 0x4ae4d0..0x4ae4e0, 0x4ae734.
 *
 * Floating-point unit: needs profile g2-apollo-main-3. The IMU getter
 * 0x4a5d16 returns its float in s0 (VFP calling convention), so it is
 * declared aapcs-vfp. While the head is pitched below -30 degrees the sensor
 * faces the floor or body, so the new reading is dropped and the last
 * accepted reading (0x200741dc) is returned instead. */
#include <stdint.h>
#include "g2_als.h"
#include "als_log.h"

#define PITCH_IGNORE_BELOW (-30.0f)

extern __attribute__((pcs("aapcs-vfp"))) float semantic_get_heading_float(void); /* 0x4a5d16 */

static const char function[] = "DRV_ALSFilterValueByPitch"; /* ROM 0x768994 */
static const char format[] = "ALS read ignored by pitch, pitch:%.2f, raw:%d, fill:%d"; /* ROM 0x71b628 */
static const char short_format[] =
    "[sensor_als]ALS read ignored by pitch, pitch:%.2f, raw:%d, fill:%d"; /* ROM 0x6ff820 */

uint32_t als_function_08(uint32_t lux)
{
    float pitch = semantic_get_heading_float();
    if (!(pitch < PITCH_IGNORE_BELOW))
        return lux;
    ALS_LOG(3u, function, 0xadu, 0x0cc00000u, format, short_format,
            (double)pitch, lux, audio_als_default_previous);
    return audio_als_default_previous;
}
