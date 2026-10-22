/* Product-test IMU / ambient-light calibration handlers, stock
 * D:\01_workspace\s200_ap510b_iar_git\platform\product_test\pt_protocol_procsr.c.
 * Native 0x573604..0x573896 (set_imu_base), 0x5738d0..0x573c04 (set_lux_base),
 * 0x5741e0..0x574456 (get_imu_base_info); literal pools 0x573c3c..0x573c4f
 * (22156.0, 4210.7, 1e6f) and 0x574570..0x57457f (1e-5f as double, "No", "Yes").
 *
 * Same calling and response conventions as pt_procsr_cmds.c. The handlers use
 * double-precision VFP (float log arguments are promoted with vcvt.f64.f32 and
 * the lux maths divides in double), so the unit needs profile g2-apollo-main-20.
 *
 * Lux calibration (cmd 0x2E): the fixture shows two reference levels; gear 4
 * stores the rounded raw reading as luminance_curve_a1, gear 1 as the second
 * point and then computes
 *   lux_base = (int)(((float)(22156.0 / a1) + (float)(4210.7 / a2)) / 2 * 1e6f)
 * into nvSysDt.lux_base (dataIdx 2), the factor get_lux_info applies as
 * raw * lux_base / 1e6. */
#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>
#include "g2_nvdb.h"

#define IAR_VFP __attribute__((pcs("aapcs-vfp")))
#define PT_PRODUCT_TEST_MODE 1u
#define PT_LUX_A1_REFERENCE 22156.0     /* ROM 0x573c3c */
#define PT_LUX_A2_REFERENCE 4210.7      /* ROM 0x573c44 */
#define PT_LUX_BASE_SCALE 1000000.0f    /* ROM 0x573c4c */
#define PT_LUX_LIMIT 80001u             /* ROM 0x574788, readings >= this fail */
#define PT_IMU_MATRIX_EPSILON 1e-5f     /* ROM 0x574570, compared in double */

extern uint8_t display_driver_ratio_cells_20003994[0xac]; /* RAM 0x20003994 nvSysDt */
#define SYS_DT ((g2_nvdb_sys_dt_t *)(void *)display_driver_ratio_cells_20003994)
extern uint32_t g2_pt_lux_gear1_200748c4;                 /* RAM 0x200748c4, gear 1 reading */
extern uint32_t g2_pt_lux_curve_a1_200748c8;              /* RAM 0x200748c8, gear 4 reading */

extern uint32_t audio_log_flags(void); /* 0x43d0ce */
extern void audio_log_extended(uint8_t, const char *, const char *, const char *, uint32_t, const char *, ...); /* 0x43d574 */
extern uint32_t compress_log_output(uint32_t, const char *, const char *, ...); /* 0x43ce9e */
extern void *aeabi_memcpy4_439c04(void *dst, const void *src, uint32_t len);
extern void audio_uart_lv_memzero_48949c(void *dst, uint32_t len);
extern uint8_t productModeGet(void);                       /* 0x4abe60 */
extern void HUB_IMUCalibParaInit(void);                    /* 0x4a6bce */
extern const float *semantic_get_orientation_vector(void); /* 0x4a5d38 */
extern IAR_VFP double pt_als_raw_lux_get_58f8e4(void);
extern IAR_VFP double iar_round_58f970(double x);

static const char module_tag[] = "pt_protocol_procsr"; /* ROM 0x7829fc */
static const char source_file[] = "D:\\01_workspace\\s200_ap510b_iar_git\\platform\\product_test\\pt_protocol_procsr.c"; /* ROM 0x6ef458 */
static const char para_null[] = "%s para is NULL\n"; /* ROM 0x782a74 */
static const char para_null_c[] = "[pt_protocol_procsr]%s para is NULL\n"; /* ROM 0x74d304 */
static const char denied[] = "permission denied current mode is not product test mode"; /* ROM 0x721c18 */
static const char denied_c[] = "[pt_protocol_procsr]permission denied current mode is not product test mode"; /* ROM 0x6f586c */

/* set_imu_base / set_lux_base (set_lux_base logs the set_imu_base join text) */
static const char fn_imu_base[] = "set_imu_base"; /* ROM 0x788530 */
static const char imu_base_join[] = "join in set_imu_base"; /* ROM 0x77ae1c */
static const char imu_base_join_c[] = "[pt_protocol_procsr]join in set_imu_base"; /* ROM 0x742288 */
static const char imu_calib[] = "IMU Calib Para Init: calibMatrix = %f, %f, %f, %f, %f, %f, %f, %f, %f"; /* ROM 0x6fc53c */
static const char imu_calib_c[] = "[pt_protocol_procsr]IMU Calib Para Init: calibMatrix = %f, %f, %f, %f, %f, %f, %f, %f, %f"; /* ROM 0x6e14e8 */
static const char fn_lux_base[] = "set_lux_base"; /* ROM 0x788540 */
static const char lux_val[] = "gear = %d,lux val is:%f"; /* ROM 0x77ae34 */
static const char lux_val_c[] = "[pt_protocol_procsr]gear = %d,lux val is:%f"; /* ROM 0x7422b4 */
static const char lux_a1_unset[] = "luminance_curve_a1 is not set"; /* ROM 0x7643d0 */
static const char lux_a1_unset_c[] = "[pt_protocol_procsr]luminance_curve_a1 is not set"; /* ROM 0x72c680 */
static const char lux_ok[] = "production lux base set success"; /* ROM 0x7643f0 */
static const char lux_ok_c[] = "[pt_protocol_procsr]production lux base set success"; /* ROM 0x72c6b4 */
static const char lux_gear_err[] = "gear data error"; /* ROM 0x788550 */
static const char lux_gear_err_c[] = "[pt_protocol_procsr]gear data error"; /* ROM 0x758ba4 */

/* get_imu_base_info */
static const char fn_imu_info[] = "get_imu_base_info"; /* ROM 0x782ca4 */
static const char imu_info_join[] = "join in get_imu_base_info"; /* ROM 0x770698 */
static const char imu_info_join_c[] = "[pt_protocol_procsr]join in get_imu_base_info"; /* ROM 0x737574 */
static const char imu_info[] = "IMU Base Info: calibrated=%s, euler=[%.2f, %.2f, %.2f]"; /* ROM 0x721cc0 */
static const char imu_info_c[] = "[pt_protocol_procsr]IMU Base Info: calibrated=%s, euler=[%.2f, %.2f, %.2f]"; /* ROM 0x6f58b8 */

/* Uncalibrated mounting matrix (identity), copied from ROM 0x758e08. */
static const float imu_default_matrix[9] = {1.0f, 0.0f, 0.0f, 0.0f, 1.0f, 0.0f, 0.0f, 0.0f, 1.0f};

static const char text_no[] = "No";   /* ROM 0x574578, inline literal */
static const char text_yes[] = "Yes"; /* ROM 0x57457c, inline literal */

static int log_extended_on(void) { return (audio_log_flags() & 2u) != 0u; }
static int log_compressed_on(void) { return (audio_log_flags() & 1u) || (audio_log_flags() & 4u); }

#define PT_CLOG(level, nargs) (((uint32_t)(level) << 26) | ((uint32_t)(nargs) << 22))
#define PT_LOG0(level, fn, line, fmt, cfmt) do { \
        if (log_extended_on()) audio_log_extended((level), module_tag, source_file, (fn), (line), (fmt)); \
        if (log_compressed_on()) (void)compress_log_output(PT_CLOG((level), 0), (cfmt), (cfmt)); \
    } while (0)
#define PT_LOGN(level, nargs, fn, line, fmt, cfmt, ...) do { \
        if (log_extended_on()) audio_log_extended((level), module_tag, source_file, (fn), (line), (fmt), __VA_ARGS__); \
        if (log_compressed_on()) (void)compress_log_output(PT_CLOG((level), (nargs)), (cfmt), (cfmt), __VA_ARGS__); \
    } while (0)
#define PT_PARA_NULL(fn, line) PT_LOGN(1, 1, (fn), (line), para_null, para_null_c, (fn))
#define PT_DENIED(fn, line) PT_LOG0(1, (fn), (line), denied, denied_c)
#define PT_BAD_ARGS(payload, length, rsp, rsp_len, min) \
    ((rsp) == NULL || (rsp_len) == NULL || (payload) == NULL || (uint8_t)(length) < (min))
#define PT_HEADER(rsp, idx, rsp_cmd, data_len) do { \
        (rsp)[(idx)++] = (rsp_cmd); \
        (rsp)[(idx)++] = 1u; \
        (rsp)[(idx)++] = 3u; \
        (rsp)[(idx)++] = (data_len); \
    } while (0)

/* cmd 0x2D set_imu_base: payload[4..39] is the 3x3 IMU mounting matrix (9
 * floats); stored with zero accel/gyro bias pointers (matrix only). */
uint32_t pt_cmd_3A_handler(const uint8_t *payload, uint8_t length, uint8_t *rsp, uint8_t *rsp_len)
{
    PT_LOG0(3, fn_imu_base, 0x938u, imu_base_join, imu_base_join_c);
    if (PT_BAD_ARGS(payload, length, rsp, rsp_len, 0x28u)) {
        PT_PARA_NULL(fn_imu_base, 0x93bu);
        return UINT32_MAX;
    }
    uint8_t idx = 0;
    PT_HEADER(rsp, idx, 0x2du, 1u);
    if (productModeGet() == PT_PRODUCT_TEST_MODE) {
        float m[9];
        const float *src = (const float *)(const void *)&payload[4];
        audio_uart_lv_memzero_48949c(m, sizeof(m));
        for (int i = 0; i < 9; i++)
            m[i] = src[i];
        PT_LOGN(3, 9, fn_imu_base, 0x950u, imu_calib, imu_calib_c, (double)m[0], (double)m[1], (double)m[2],
                (double)m[3], (double)m[4], (double)m[5], (double)m[6], (double)m[7], (double)m[8]);
        nvdbSensorCaldataAgUpdate(NULL, NULL, m);
        rsp[idx++] = 0u;
    } else {
        PT_DENIED(fn_imu_base, 0x956u);
        rsp[idx++] = 5u;
    }
    *rsp_len = idx;
    return 0;
}

/* cmd 0x2E set_lux_base: payload[4] = gear (4 = a1 point, 1 = second point,
 * which also computes lux_base when a1 is set). Data: status, gear, rounded
 * lux (LE32). Status 1 when lux >= 80001, 2 when lux is 0, overriding the
 * product-mode result. Stock logs the set_imu_base join text here. */
uint32_t pt_cmd_3D_handler(const uint8_t *payload, uint8_t length, uint8_t *rsp, uint8_t *rsp_len)
{
    PT_LOG0(3, fn_lux_base, 0x960u, imu_base_join, imu_base_join_c);
    if (PT_BAD_ARGS(payload, length, rsp, rsp_len, 5u)) {
        PT_PARA_NULL(fn_lux_base, 0x963u);
        return UINT32_MAX;
    }
    uint8_t idx = 0;
    PT_HEADER(rsp, idx, 0x2eu, 6u);
    uint8_t gear = payload[4];
    double raw = pt_als_raw_lux_get_58f8e4();
    uint32_t lux = (uint32_t)iar_round_58f970(raw);
    PT_LOGN(3, 2, fn_lux_base, 0x971u, lux_val, lux_val_c, gear, raw);
    if (productModeGet() == PT_PRODUCT_TEST_MODE) {
        rsp[idx++] = 0u;
        if (gear == 4u) {
            g2_pt_lux_curve_a1_200748c8 = lux;
        } else if (gear == 1u) {
            g2_pt_lux_gear1_200748c4 = lux;
            if (g2_pt_lux_curve_a1_200748c8 == 0u) {
                PT_LOG0(1, fn_lux_base, 0x980u, lux_a1_unset, lux_a1_unset_c);
            } else {
                float a1 = (float)(PT_LUX_A1_REFERENCE / (double)g2_pt_lux_curve_a1_200748c8);
                float a2 = (float)(PT_LUX_A2_REFERENCE / (double)g2_pt_lux_gear1_200748c4);
                SYS_DT->lux_base = (uint32_t)(int32_t)(((a1 + a2) / 2.0f) * PT_LUX_BASE_SCALE);
                (void)SVC_NvdbWriteSysData(G2_NVDB_SYSDT_LUX, &SYS_DT->lux_base);
                PT_LOG0(4, fn_lux_base, 0x988u, lux_ok, lux_ok_c);
            }
        } else {
            PT_LOG0(1, fn_lux_base, 0x98du, lux_gear_err, lux_gear_err_c);
        }
    } else {
        PT_DENIED(fn_lux_base, 0x992u);
        rsp[idx++] = 5u;
    }
    rsp[idx++] = gear;
    const uint8_t *lux_bytes = (const uint8_t *)&lux;
    for (uint32_t i = 0; i < 4u; i++)
        rsp[idx++] = lux_bytes[i];
    if (lux >= PT_LUX_LIMIT)
        rsp[4] = 1u;
    else if (lux == 0u)
        rsp[4] = 2u;
    *rsp_len = idx;
    return 0;
}

/* cmd 0x45 get_imu_base_info: data byte 0 is 1 when the stored mounting matrix
 * still equals the identity default (not calibrated, every element within
 * 1e-5), else 0; then the current orientation vector as 3 raw floats. */
uint32_t pt_cmd_43_handler(const uint8_t *payload, uint8_t length, uint8_t *rsp, uint8_t *rsp_len)
{
    PT_LOG0(3, fn_imu_info, 0xa2du, imu_info_join, imu_info_join_c);
    if (PT_BAD_ARGS(payload, length, rsp, rsp_len, 4u)) {
        PT_PARA_NULL(fn_imu_info, 0xa30u);
        return UINT32_MAX;
    }
    uint8_t idx = 0;
    PT_HEADER(rsp, idx, 0x45u, 13u);
    HUB_IMUCalibParaInit();
    float accel[3] = {0.0f, 0.0f, 0.0f};
    float gyro[3] = {0.0f, 0.0f, 0.0f};
    float matrix[9];
    float reference[9];
    audio_uart_lv_memzero_48949c(matrix, sizeof(matrix));
    (void)nvdbSensorCaldataAgRead(accel, gyro, matrix);
    (void)aeabi_memcpy4_439c04(reference, imu_default_matrix, sizeof(reference));
    bool is_default = true;
    for (int i = 0; i < 9; i++) {
        if (__builtin_fabs((double)(matrix[i] - reference[i])) >= (double)PT_IMU_MATRIX_EPSILON) {
            is_default = false;
            break;
        }
    }
    rsp[idx++] = is_default ? 1u : 0u;
    const float *euler = semantic_get_orientation_vector();
    const uint8_t *bytes = (const uint8_t *)euler;
    for (uint32_t i = 0; i < 4u; i++)
        rsp[idx++] = bytes[i];
    for (uint32_t i = 0; i < 4u; i++)
        rsp[idx++] = bytes[4u + i];
    for (uint32_t i = 0; i < 4u; i++)
        rsp[idx++] = bytes[8u + i];
    PT_LOGN(3, 4, fn_imu_info, 0xa75u, imu_info, imu_info_c, is_default ? text_no : text_yes,
            (double)euler[0], (double)euler[1], (double)euler[2]);
    *rsp_len = idx;
    return 0;
}
