/* HUB_IMUCalibParaInit, stock D:\01_workspace\s200_ap510b_iar_git\platform\sensor_hub\sensor_hub.c.
 * Native 0x4a6bce..0x4a6d26 (literals in pool 0x4a73a4..0x4a73af).
 * Split from sensor_hub.c because the float -> double log arguments need the
 * VFP profile (g2-apollo-main-3).
 *
 * Reads the 0x44-byte NVDB sensor calibration record (two 3-word vectors at
 * +4/+0x10, then the 3x3 mounting matrix at +0x1c) and installs the matrix in
 * the IMU driver as Q14/Q30 caches. Message 3 re-runs it. */
#include <stdint.h>
#include "sensor_hub.h"

extern void audio_uart_lv_memzero_48949c(void *dst, uint32_t len);
extern int32_t nvdbSensorCaldataAgRead(float accel[3], float gyro[3], float matrix[9]);
extern int32_t semantic_set_orientation_matrix(const float accel[3], const float gyro[3],
                                               const float matrix[9]);

static const char hub_module[] = "sensor_hub"; /* ROM 0x78bde0 */
static const char hub_path[] = "D:\\01_workspace\\s200_ap510b_iar_git\\platform\\sensor_hub\\sensor_hub.c"; /* ROM 0x6fc974 */
static const char fn_calib[] = "HUB_IMUCalibParaInit"; /* ROM 0x77b224 */
static const char calib_text[] = "IMU Calib Para Init: calibMatrix = %f, %f, %f, %f, %f, %f, %f, %f, %f"; /* ROM 0x6fc9bc */
static const char calib_short[] = "[sensor_hub]IMU Calib Para Init: calibMatrix = %f, %f, %f, %f, %f, %f, %f, %f, %f"; /* ROM 0x6e9a48 */

void HUB_IMUCalibParaInit(void) {
    float accel[3] = {0.0f, 0.0f, 0.0f}; /* sp+0x5c */
    float gyro[3] = {0.0f, 0.0f, 0.0f};  /* sp+0x50 */
    float m[9];                          /* sp+0x68 */
    audio_uart_lv_memzero_48949c(m, sizeof m);
    (void)nvdbSensorCaldataAgRead(accel, gyro, m);
    (void)semantic_set_orientation_matrix(accel, gyro, m);
    if ((audio_log_flags() & 2u) != 0u)
        audio_log_extended(3u, hub_module, hub_path, fn_calib, 315u, calib_text,
                           (double)m[0], (double)m[1], (double)m[2], (double)m[3],
                           (double)m[4], (double)m[5], (double)m[6], (double)m[7],
                           (double)m[8]);
    if ((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)
        (void)compress_log_output(0x0e400000u, calib_short, calib_short,
                                  (double)m[0], (double)m[1], (double)m[2], (double)m[3],
                                  (double)m[4], (double)m[5], (double)m[6], (double)m[7],
                                  (double)m[8]);
}
