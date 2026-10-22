/* eAT command AT^IMU_EULER (registry row 0x6c9320, type 0).
 * Native atImuEulerHandler 0x5a5864..0x5a589a, format literal at 0x5a58a4.
 * Separate unit because the float -> double arguments need the VFP profile
 * (g2-apollo-main-3); the first double travels in r2:r3 (softfp variadic). */
#include <stdint.h>

extern void at_core_output(const char *fmt, ...);
/* IMU glue 0x4a5d20: pointer to the latest {roll, pitch, yaw} floats. */
extern const float *semantic_get_magnetic_vector(void);

static const char euler_ok[] = "AT^IMU_EULER+OK:roll=%.2f,pitch=%.2f,yaw=%.2f\r\n"; /* ROM 0x731b44 */

int32_t atImuEulerHandler(const char *param) {
    const float *euler = semantic_get_magnetic_vector();
    (void)param;
    at_core_output(euler_ok, (double)euler[0], (double)euler[1], (double)euler[2]);
    return 1;
}
