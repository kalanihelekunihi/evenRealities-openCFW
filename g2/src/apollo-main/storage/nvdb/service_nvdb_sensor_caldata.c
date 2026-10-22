/* NVDB IMU calibration records, stock
 * D:\01_workspace\s200_ap510b_iar_git\platform\service\flashDB\NV\service_nvdb_sensor_caldata.c.
 * Native 0x509764..0x509ae9; literal pool 0x509aec..0x509b47.
 * Floating point: build with profile g2-apollo-main-3. Stock passes the
 * nvdbSensorCaldataUpdate scalar in s0 (hard-float call).
 *
 * "nvSCald"   (92 bytes, RAM 0x200038f4): version 1, CRC16 over 0x58 bytes.
 * "nvSCaldAG" (68 bytes, RAM 0x20003950): version 1, accel[3], gyro[3],
 *             3x3 matrix, CRC16 over 0x40 bytes. */
#include <stdint.h>
#include "nvdb_internal.h"

extern g2_nvdb_sensor_caldata_t g2_nvdb_sensor_caldata;       /* RAM 0x200038f4 */
extern g2_nvdb_sensor_caldata_ag_t g2_nvdb_sensor_caldata_ag; /* RAM 0x20003950 */
extern uint8_t audio_uart_device_role_get(void);               /* 0x45a568, RAM 0x20075024 */
extern void *audio_uart_display_area_copy_439c04(void *, const void *, uint32_t); /* memcpy */

void nvdbSensorCaldataUpdate(const float *vec0, const float *vec1, const float *quat0,
                             const float *quat1, float scalar, const float *vec6);
int32_t _nvdbCheckSensorCaldata(void);

static const char module_tag[] = "nv.s.cald"; /* ROM 0x78c014 */
static const char source_file[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\platform\\service\\flashDB\\NV\\service_nvdb_sensor_caldata.c"; /* ROM 0x6de7f4 */
static const char key_scald[] = "nvSCald"; /* ROM 0x78e634 */
static const char key_scald_ag[] = "nvSCaldAG"; /* ROM 0x78c020 */
static const char update_fn[] = "_nvdbUpdataSensorCaldata"; /* ROM 0x77140c */
static const char check_fn[] = "_nvdbCheckSensorCaldata"; /* ROM 0x77bb24 */
static const char debug_only[] = "!!This is only for program debugging"; /* ROM 0x74e0ec */
static const char debug_only_short[] = "[nv.s.cald]!!This is only for program debugging"; /* ROM 0x7385f4 */
static const char version_fmt[] = "version %d(%d)"; /* ROM 0x788c20 */
static const char version_short[] = "[nv.s.cald]version %d(%d)"; /* ROM 0x771428 */
static const char crc_fmt[] = "crc 0x%x(0x%x)"; /* ROM 0x788c30 */
static const char crc_short[] = "[nv.s.cald]crc 0x%x(0x%x)"; /* ROM 0x771444 */
static const char first_write[] = "---->not key in the flash, first wirte kv crc = 0x%x"; /* ROM 0x722e08 */
static const char first_write_short[] =
    "[nv.s.cald]---->not key in the flash, first wirte kv crc = 0x%x"; /* ROM 0x70ee64 */
static const char abnormal_matrix[] =
    "Detected abnormal caldata_matrix pattern, resetting to default"; /* ROM 0x70eea4 */
static const char abnormal_matrix_short[] =
    "[nv.s.cald]Detected abnormal caldata_matrix pattern, resetting to default"; /* ROM 0x6f5ea8 */

/* ROM 0x759c60: default mounting matrix restored by _nvdbCheckSensorCaldata. */
static const float default_matrix[9] = {
    -0x1.a35696p-1f, -0x1.77ab32p-2f, 0x1.b225fap-2f,
    0x1.ca9196p-2f, 0x1.1419fep-4f, 0x1.bf0004p-1f,
    -0x1.65a294p-2f, 0x1.ddad1p-1f, 0x1.db3d08p-4f,
};

#define LOG(...) NVDB_LOG(module_tag, source_file, __VA_ARGS__)

int32_t nvdbSensorCaldataDefaultInitialize(void)
{
    g2_nvdb_sensor_caldata.crc = audio_uart_hand_checksum_49acd4(&g2_nvdb_sensor_caldata, 0x58u, NULL);
    return 0;
}

int32_t _nvdbUpdataSensorCaldata(void)
{
    g2_nvdb_sensor_caldata_t stored;
    g2_nvdb_sensor_caldata_t *rec = &g2_nvdb_sensor_caldata;
    LOG(2u, update_fn, 0x3eu, 0x08000000u, debug_only, debug_only_short);
    if (SVC_NvdbRead(key_scald, &stored, 0x5cu) > 0) {
        LOG(4u, update_fn, 0x41u, 0x10800000u, version_fmt, version_short,
            (uint32_t)stored.version, 1u);
        LOG(4u, update_fn, 0x42u, 0x10800000u, crc_fmt, crc_short,
            (uint32_t)stored.crc, (uint32_t)rec->crc);
        if (stored.crc != rec->crc && stored.version == 0u)
            nvdbSensorCaldataUpdate(rec->vec0, rec->vec1, rec->quat0, rec->quat1,
                                    rec->scalar, rec->vec6);
        return 0;
    }
    LOG(4u, update_fn, 0x49u, 0x10400000u, first_write, first_write_short, (uint32_t)rec->crc);
    nvdbSensorCaldataUpdate(rec->vec0, rec->vec1, rec->quat0, rec->quat1, rec->scalar, rec->vec6);
    return 0;
}

void nvdbSensorCaldataUpdate(const float *vec0, const float *vec1, const float *quat0,
                             const float *quat1, float scalar, const float *vec6)
{
    g2_nvdb_sensor_caldata_t *rec = &g2_nvdb_sensor_caldata;
    rec->version = 1u;
    audio_uart_checksum_copy(rec->vec0, vec0, 12u);
    audio_uart_checksum_copy(rec->vec1, vec1, 12u);
    audio_uart_checksum_copy(rec->quat0, quat0, 16u);
    audio_uart_checksum_copy(rec->quat1, quat1, 16u);
    rec->scalar = scalar;
    audio_uart_checksum_copy(rec->vec6, vec6, 24u);
    rec->crc = audio_uart_hand_checksum_49acd4(rec, 0x58u, NULL);
    (void)SVC_NvdbWrite(key_scald, rec, 0x5cu);
}

int32_t nvdbSensorCaldataAgDefaultInitialize(void)
{
    g2_nvdb_sensor_caldata_ag.crc = audio_uart_hand_checksum_49acd4(&g2_nvdb_sensor_caldata_ag, 0x40u, NULL);
    return 0;
}

int32_t nvdbSensorCaldataAgLoadAndMigrate(void)
{
    return 0;
}

void nvdbSensorCaldataAgUpdate(const float *accel, const float *gyro, const float *matrix)
{
    g2_nvdb_sensor_caldata_ag_t *rec = &g2_nvdb_sensor_caldata_ag;
    rec->version = 1u;
    if (accel != NULL)
        audio_uart_checksum_copy(rec->accel, accel, 12u);
    if (gyro != NULL)
        audio_uart_checksum_copy(rec->gyro, gyro, 12u);
    if (matrix != NULL)
        audio_uart_checksum_copy(rec->matrix, matrix, 36u);
    rec->crc = audio_uart_hand_checksum_49acd4(rec, 0x40u, NULL);
    (void)SVC_NvdbWrite(key_scald_ag, rec, 0x44u);
}

/* Loads the AG record into RAM, repairs a known-bad matrix in RAM only, then
 * hands out copies. Returns the blob read length. */
int32_t nvdbSensorCaldataAgRead(float accel[3], float gyro[3], float matrix[9])
{
    g2_nvdb_sensor_caldata_ag_t *rec = &g2_nvdb_sensor_caldata_ag;
    int32_t length = SVC_NvdbRead(key_scald_ag, rec, 0x44u);
    (void)_nvdbCheckSensorCaldata();
    audio_uart_checksum_copy(accel, rec->accel, 12u);
    audio_uart_checksum_copy(gyro, rec->gyro, 12u);
    audio_uart_checksum_copy(matrix, rec->matrix, 36u);
    return length;
}

/* Device role 1 only: a matrix with 0.6 <= m[0] < 0.85 and -0.95 <= m[5] < -0.7
 * (NaN rejects) is replaced by the ROM default. The flash copy is untouched. */
int32_t _nvdbCheckSensorCaldata(void)
{
    float matrix[9];
    g2_nvdb_sensor_caldata_ag_t *rec = &g2_nvdb_sensor_caldata_ag;
    if (audio_uart_device_role_get() != 1u)
        return 0;
    float m0 = rec->matrix[0];
    float m5 = rec->matrix[5];
    if (!(m0 >= 0x1.333336p-1f) || !(m0 < 0x1.b33334p-1f) ||
        !(m5 < -0x1.666666p-1f) || !(m5 >= -0x1.e66664p-1f))
        return 0;
    LOG(2u, check_fn, 0xb0u, 0x08000000u, abnormal_matrix, abnormal_matrix_short);
    (void)audio_uart_display_area_copy_439c04(matrix, default_matrix, 36u);
    audio_uart_checksum_copy(rec->matrix, matrix, 36u);
    return 1;
}
