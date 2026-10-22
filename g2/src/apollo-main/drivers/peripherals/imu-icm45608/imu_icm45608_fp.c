/* IMU glue, stock D:\01_workspace\s200_ap510b_iar_git\driver\sensor\imu\imu_icm45608.c.
 * Floating-point part of native 0x4a35b0..0x4a656e (filter, sensor setup,
 * mounting matrix, sample parser, quaternion/euler, head-up and compass
 * detection, CSV data lines). Literal pools 0x4a37e0, 0x4a4278, 0x4a457c,
 * 0x4a4960, 0x4a56a0, 0x4a5b68, 0x4a5d28, 0x4a5e14, 0x4a5ec4, 0x4a60d0,
 * 0x4a625c, 0x4a6368, 0x4a6570.
 *
 * Stock is IAR with a double-precision FPv5 unit: it uses VFP instructions
 * (vmul.f64, vcvt fixed-point) and the hard-float calling convention, never
 * soft-float helpers. Profile g2-apollo-main-3 (fpv5-sp-d16, softfp) is the
 * nearest repository profile; functions with float arguments or results are
 * marked aapcs-vfp to keep the stock register interface. */
#include <stdint.h>
#include <stddef.h>
#include "g2_imu.h"
#include "imu_icm45608_private.h"

/* ---- TDK driver (vendored 1.1.2 unless noted) ---- */
extern int inv_imu_adv_configure_wom_50481a(g2_inv_imu_device_t *s, uint8_t wom_x_th,
                                            uint8_t wom_y_th, uint8_t wom_z_th,
                                            uint8_t wom_int, uint8_t wom_dur);
extern int inv_imu_adv_enable_wom_504888(g2_inv_imu_device_t *s);
extern int inv_imu_adv_disable_wom_5048ba(g2_inv_imu_device_t *s);
extern int inv_imu_adv_get_fifo_config_5059c0(g2_inv_imu_device_t *s,
                                              g2_inv_imu_adv_fifo_config_t *conf);
extern int inv_imu_adv_set_fifo_config_505aa2(g2_inv_imu_device_t *s,
                                              const g2_inv_imu_adv_fifo_config_t *conf);
extern int inv_imu_set_accel_mode_505fcc(g2_inv_imu_device_t *s, uint8_t mode);
extern int inv_imu_set_gyro_mode_506008(g2_inv_imu_device_t *s, uint8_t mode);
extern int inv_imu_set_accel_frequency_506044(g2_inv_imu_device_t *s, uint8_t odr);
extern int inv_imu_set_gyro_frequency_506078(g2_inv_imu_device_t *s, uint8_t odr);
extern int inv_imu_set_accel_fsr_5060ac(g2_inv_imu_device_t *s, uint8_t fsr);
extern int inv_imu_set_gyro_fsr_5060e0(g2_inv_imu_device_t *s, uint8_t fsr);
extern int inv_imu_set_gyro_ln_bw_506118(g2_inv_imu_device_t *s, uint8_t bw);
extern int inv_imu_set_gyro_lp_avg_506150(g2_inv_imu_device_t *s, uint8_t avg);
extern int inv_imu_set_accel_lp_avg_506188(g2_inv_imu_device_t *s, uint8_t avg);
extern int inv_imu_set_accel_ln_bw_5061c0(g2_inv_imu_device_t *s, uint8_t bw);
extern int inv_imu_flush_fifo_5062c8(g2_inv_imu_device_t *s);
extern int inv_imu_set_config_int_50637c(g2_inv_imu_device_t *s, uint8_t num,
                                         const g2_inv_imu_int_state_t *it);
extern int inv_imu_get_int_status_5065cc(g2_inv_imu_device_t *s, uint8_t num,
                                         g2_inv_imu_int_state_t *it);
extern int inv_imu_select_accel_lp_clk_5066b6(g2_inv_imu_device_t *s, uint8_t clk_sel);
extern int inv_imu_edmp_set_frequency_506794(g2_inv_imu_device_t *s, uint8_t apex_odr);
extern int inv_imu_edmp_init_5067c8(g2_inv_imu_device_t *s);
extern int inv_imu_edmp_get_powersave_parameters_50699a(
    g2_inv_imu_device_t *s, g2_inv_imu_edmp_powersave_parameters_t *p);
extern int inv_imu_edmp_get_tap_parameters_5069cc(g2_inv_imu_device_t *s,
                                                  g2_inv_imu_edmp_tap_parameters_t *p);
extern int inv_imu_edmp_set_powersave_parameters_506a6e(
    g2_inv_imu_device_t *s, const g2_inv_imu_edmp_powersave_parameters_t *p);
extern int inv_imu_edmp_set_tap_parameters_506b06(g2_inv_imu_device_t *s,
                                                  const g2_inv_imu_edmp_tap_parameters_t *p);
extern int inv_imu_edmp_get_gaf_parameters_506bd2(g2_inv_imu_device_t *s,
                                                  g2_inv_imu_edmp_gaf_parameters_t *p);
extern int inv_imu_edmp_set_gaf_parameters_506eca(g2_inv_imu_device_t *s,
                                                  const g2_inv_imu_edmp_gaf_parameters_t *p);
extern int inv_imu_edmp_set_gaf_soft_iron_cor_matrix_507576(g2_inv_imu_device_t *s,
                                                            const int32_t matrix[3][3]);
extern int inv_imu_edmp_set_gaf_mag_bias_5075d6(g2_inv_imu_device_t *s,
                                                const int32_t mag_bias_q16[3],
                                                uint8_t accuracy);
extern int inv_imu_edmp_set_gaf_mode_507694(g2_inv_imu_device_t *s, uint8_t gyro_is_on,
                                            uint8_t mag_is_on);
/* Stock variant writes the 18-byte Q14 buffer to SRAM 0x1ac unconverted. */
extern int inv_imu_edmp_set_mounting_matrix_507710(g2_inv_imu_device_t *s,
                                                   const int16_t matrix_q14[9]);
extern int inv_imu_edmp_set_config_int_apex_507726(g2_inv_imu_device_t *s,
                                                   const g2_inv_imu_edmp_int_state_t *it);
extern int inv_imu_edmp_enable_5078a0(g2_inv_imu_device_t *s);
extern int inv_imu_edmp_disable_5078d2(g2_inv_imu_device_t *s);
extern int inv_imu_edmp_enable_tap_5079bc(g2_inv_imu_device_t *s);
extern int inv_imu_edmp_disable_tap_5079fe(g2_inv_imu_device_t *s);
extern int inv_imu_edmp_enable_gaf_507a30(g2_inv_imu_device_t *s);
extern int inv_imu_edmp_disable_gaf_507a9c(g2_inv_imu_device_t *s);
extern int inv_imu_edmp_enable_gaf_soft_iron_cor_507ace(g2_inv_imu_device_t *s);
extern int inv_imu_edmp_get_int_apex_status_507b00(g2_inv_imu_device_t *s,
                                                   g2_inv_imu_edmp_int_state_t *it);
extern int inv_imu_edmp_gaf_decode_fifo_507c94(g2_inv_imu_device_t *s, const uint8_t es0[9],
                                               const uint8_t es1[6],
                                               g2_inv_imu_edmp_gaf_outputs_t *out);
extern int inv_imu_edmp_unmask_int_src_5080fa(g2_inv_imu_device_t *s, uint8_t edmp_int,
                                              uint8_t mask);
/* B2S ("TILT") of the stock TDK drop: enable has no ODR check, the image
 * goes to SRAM 0x1088 and the parameters are {Q30 cos, mode}. */
extern int inv_imu_edmp_b2s_enable_5082d0(g2_inv_imu_device_t *s);
extern int inv_imu_edmp_b2s_disable_50832e(g2_inv_imu_device_t *s);
extern int inv_imu_edmp_b2s_init_over_sif_50839e(g2_inv_imu_device_t *s);
extern int inv_imu_edmp_b2s_get_parameters_508402(g2_inv_imu_device_t *s,
                                                  g2_imu_b2s_parameters_t *p);
extern int inv_imu_edmp_b2s_set_parameters_50842e(g2_inv_imu_device_t *s,
                                                  const g2_imu_b2s_parameters_t *p,
                                                  uint32_t odr_hz);
extern int inv_imu_edmp_aid_init_over_sif_5084d8(g2_inv_imu_device_t *s, uint8_t *usecase);
extern int inv_imu_edmp_aid_get_parameters_508548(g2_inv_imu_device_t *s,
                                                  g2_inv_imu_edmp_aid_parameters_t *p,
                                                  uint8_t usecase);
extern int inv_imu_edmp_aid_set_parameters_50861a(g2_inv_imu_device_t *s,
                                                  const g2_inv_imu_edmp_aid_parameters_t *p,
                                                  uint8_t usecase);
extern int inv_imu_edmp_aid_enable_50872c(g2_inv_imu_device_t *s);
extern int inv_imu_edmp_aid_disable_50879a(g2_inv_imu_device_t *s);
/* invn_mag.c (Arduino-port glue for the ICT1531x behind the I2C master). */
extern int invn_mag_init_508954(g2_inv_imu_device_t *s);
extern int invn_mag_load_ram_image_508a98(g2_inv_imu_device_t *s, uint8_t usecase);
extern int invn_mag_enable_automrm_508ab4(g2_inv_imu_device_t *s);
extern int invn_mag_disable_automrm_508b5a(g2_inv_imu_device_t *s);
extern int inv_imu_read_reg_508e5c(void *t, uint32_t reg, uint32_t len, void *buf);
extern int inv_imu_read_sram_508e8a(void *t, uint32_t addr, uint32_t len, void *buf);

/* ---- IAR libm and product callees ---- */
extern G2_IMU_VFP double iar_cos_508e58(double x);
extern G2_IMU_VFP float audio_uart_float_two_input_angle_50969c(float y, float x); /* atan2f */
extern G2_IMU_VFP float audio_uart_float_inverse_signed_509708(float x);         /* asinf */
extern G2_IMU_VFP float audio_uart_float_sqrt_4397a8(float x);                   /* sqrtf */
extern int32_t iar_abs_509694(int32_t x);
/* Packs {1, x, y, z} and sends command 0xe0 (13 bytes). */
extern G2_IMU_VFP void imu_accel_report_send_4da6d4(float x, float y, float z);
extern uint32_t file_write(const void *buf, uint32_t size, uint32_t count, void *file); /* 0x474682 */
extern int32_t g2_audio_dump_snprintf(char *, uint32_t, const char *, ...); /* 0x44b728 */

G2_IMU_VFP float semantic_filter_update(float x, g2_imu_biquad_t *f);
void semantic_transform_vector(float v[3], const float m[3][3]);
void semantic_fixed_vector_to_float(const int32_t *in, float *out, uint32_t q, uint8_t n);
void semantic_quaternion_to_euler(const float q[4], float euler[3]);
void semantic_forward_periodic_sample(void);
G2_IMU_VFP void semantic_set_heading(float pitch);

static const char imu_module[] = "sensor_imu"; /* ROM 0x78ab44 */
static const char imu_path[] = "D:\\01_workspace\\s200_ap510b_iar_git\\driver\\sensor\\imu\\imu_icm45608.c"; /* ROM 0x6fade4 */
static const char imu_error_text[] = "IMU Error: At %s (line %d)"; /* ROM 0x76be14 */
static const char imu_error_short[] = "[sensor_imu]IMU Error: At %s (line %d)"; /* ROM 0x74a514 */

static const char fn_set_params[] = "DRV_IMUSetSensorParameters"; /* ROM 0x76bdf8 */
static const char fn_headup[] = "DRV_IMUCheckHeadUpEvent"; /* ROM 0x777b34 */
static const char fn_compass[] = "DRV_IMUCheckCompassEvent"; /* ROM 0x76be4c */
static const char fn_parser[] = "DRV_IMUDataParserCallback"; /* ROM 0x76be68 */
static const char fn_csv_line[] = "DRV_IMUWriteCSVDataLine"; /* ROM 0x777b64 */

static const char mag_init_error[] = "invn_mag_init error"; /* ROM 0x77f798 */
static const char mag_init_error_short[] = "[sensor_imu]invn_mag_init error"; /* ROM 0x760370 */
static const char headup_text[] = "[IMU] Check head-up event,euler_data[1]=%.2f,threshold=%d"; /* ROM 0x715994 */
static const char headup_short[] = "[sensor_imu][IMU] Check head-up event,euler_data[1]=%.2f,threshold=%d"; /* ROM 0x6fae2c */
static const char headdown_text[] = "[IMU] Check head-down event,euler_data[1]=%.2f"; /* ROM 0x734634 */
static const char headdown_short[] = "[sensor_imu][IMU] Check head-down event,euler_data[1]=%.2f"; /* ROM 0x7159d0 */
static const char compass_cal1[] = "[IMU] Compass calibration state changed to 1"; /* ROM 0x734664 */
static const char compass_cal1_short[] = "[sensor_imu][IMU] Compass calibration state changed to 1"; /* ROM 0x715a0c */
static const char compass_cal0[] = "[IMU] Compass calibration state changed to 0"; /* ROM 0x734694 */
static const char compass_cal0_short[] = "[sensor_imu][IMU] Compass calibration state changed to 0"; /* ROM 0x715a48 */
static const char compass_event[] = "[IMU] Check compass event,compass_angle=%d,last_compass_angle=%d"; /* ROM 0x7033e4 */
static const char compass_event_short[] = "[sensor_imu][IMU] Check compass event,compass_angle=%d,last_compass_angle=%d"; /* ROM 0x6ed748 */
static const char parser_index[] = "[IMU] DataParser error, index > 20"; /* ROM 0x754c14 */
static const char parser_index_short[] = "[sensor_imu][IMU] DataParser error, index > 20"; /* ROM 0x7346c4 */
static const char csv_line_format[] = "%lu,%.6f,%.6f,%.6f,%.6f,%.6f,%.6f,%.6f,%.6f,%.6f,%.6f,%.6f,%.6f\n"; /* ROM 0x703428 */
static const char csv_overflow[] = "[IMU] CSV line buffer overflow"; /* ROM 0x760390 */
static const char csv_overflow_short[] = "[sensor_imu][IMU] CSV line buffer overflow"; /* ROM 0x73f18c */
static const char csv_line_fail[] = "[IMU] Failed to write CSV data line"; /* ROM 0x754c80 */
static const char csv_line_fail_short[] = "[sensor_imu][IMU] Failed to write CSV data line"; /* ROM 0x734724 */

#define IMU_RAD_TO_DEG_F (180.0f / 3.14159265f) /* 0x42652ee0, ROM 0x4a56a0 */
#define IMU_RAD_TO_DEG_D 57.2957795131         /* ROM 0x4a5ee4 */
#define Q16_MAG_SCALE 0x1333                    /* rmag LSB -> uT Q16 */
#define Q16_GYRO_SCALE 4000                     /* +-2000 dps: 4000/65536 dps per LSB */
#define Q16_ACCEL_SCALE 8                       /* +-4 g: 8/65536 g per LSB */

#define IMU_ERROR(fn, line)                                                          \
    do {                                                                             \
        if (IMU_LOG_ON())                                                            \
            audio_log_extended(1u, imu_module, imu_path, fn, line, imu_error_text,   \
                               fn, line);                                            \
        if (IMU_CLOG_ON())                                                           \
            (void)compress_log_output(0x04800000u, imu_error_short, imu_error_short, \
                                      fn, line);                                     \
    } while (0)

#define IMU_CHECK(line)                          \
    do {                                         \
        if (rc != 0) {                           \
            IMU_ERROR(fn_set_params, line);      \
            return (uint32_t)rc;                 \
        }                                        \
    } while (0)

/* Second-order Butterworth low-pass, cut-off 1/100 of the sample rate. */
void semantic_filter_init(g2_imu_biquad_t *f)
{
    f->b0 = 0.0009446918;
    f->b1 = 0.0018893837;
    f->b2 = 0.0009446918;
    f->a1 = -1.9111970674;
    f->a2 = 0.9149758348;
    f->x1 = 0.0f;
    f->x2 = 0.0f;
    f->y1 = 0.0f;
    f->y2 = 0.0f;
}

G2_IMU_VFP float semantic_filter_update(float x, g2_imu_biquad_t *f)
{
    float y = (float)((double)x * f->b0 + (double)f->x1 * f->b1 + (double)f->x2 * f->b2 -
                      (double)f->y1 * f->a1 - (double)f->y2 * f->a2);
    f->x2 = f->x1;
    f->x1 = x;
    f->y2 = f->y1;
    f->y1 = y;
    return y;
}

/* Full sensor bring-up after semantic_device_context_init. The row argument
 * is passed by semantic_imu_init but not read; the ODR cells were already
 * filled by semantic_apply_odr_config. Accel +-4 g, gyro +-2000 dps,
 * INT1 on EDMP events (+ FIFO threshold when GAF streams). */
uint32_t DRV_IMUSetSensorParameters(const g2_imu_mode_row_t *row)
{
    g2_inv_imu_device_t *s = &g2_imu_device;
    g2_imu_b2s_parameters_t b2s;
    g2_inv_imu_edmp_int_state_t apex;
    g2_inv_imu_int_state_t it;
    g2_inv_imu_edmp_tap_parameters_t tap;
    g2_inv_imu_edmp_powersave_parameters_t ps;
    g2_inv_imu_edmp_aid_parameters_t aid;
    g2_inv_imu_edmp_gaf_parameters_t gaf;
    g2_inv_imu_adv_fifo_config_t fifo;
    uint32_t gyr_dt_us;
    uint8_t aid_usecase;
    uint8_t mag_ok;
    int rc = 0;

    (void)row;
    audio_uart_buffer_zero(&b2s, sizeof b2s, 0u);
    audio_uart_buffer_zero(&apex, sizeof apex, 0u);
    audio_uart_buffer_zero(&it, sizeof it, 0u);
    audio_uart_buffer_zero(&tap, sizeof tap, 0u);

    rc |= inv_imu_edmp_disable_gaf_507a9c(s);
    rc |= inv_imu_edmp_b2s_disable_50832e(s);
    rc |= inv_imu_edmp_aid_disable_50879a(s);
    rc |= inv_imu_edmp_disable_tap_5079fe(s);
    rc |= inv_imu_edmp_disable_5078d2(s);
    IMU_CHECK(0x1d8u);

    rc |= inv_imu_set_accel_mode_505fcc(s, 0u);
    rc |= inv_imu_set_gyro_mode_506008(s, 0u);
    rc |= inv_imu_flush_fifo_5062c8(s);
    IMU_CHECK(0x1e1u);

    /* Read (and so clear) pending interrupt and APEX status. */
    rc |= inv_imu_get_int_status_5065cc(s, 0u, &it);
    rc |= inv_imu_edmp_get_int_apex_status_507b00(s, &apex);
    IMU_CHECK(0x1e6u);

    if (invn_mag_init_508954(s) == 0) {
        mag_ok = 1u;
    } else {
        if (IMU_LOG_ON())
            audio_log_extended(2u, imu_module, imu_path, fn_set_params, 0x1e9u, mag_init_error);
        if (IMU_CLOG_ON())
            (void)compress_log_output(0x08000000u, mag_init_error_short, mag_init_error_short);
        mag_ok = 0u;
    }

    rc |= inv_imu_edmp_set_frequency_506794(s, g2_imu_apex_odr);
    IMU_CHECK(0x1f1u);

    rc |= inv_imu_set_accel_frequency_506044(s, g2_imu_accel_odr);
    if (g2_imu_gyro_enabled != 0u)
        rc |= inv_imu_set_gyro_frequency_506078(s, g2_imu_gyro_odr);
    IMU_CHECK(0x1f8u);

    /* Accel LP clock: RCOSC (1) when the gyro is off, WUOSC (0) otherwise. */
    if (g2_imu_gyro_enabled == 0u)
        rc |= inv_imu_select_accel_lp_clk_5066b6(s, 1u);
    else
        rc |= inv_imu_select_accel_lp_clk_5066b6(s, 0u);
    IMU_CHECK(0x200u);

    rc |= inv_imu_set_accel_lp_avg_506188(s, 0u);
    rc |= inv_imu_set_accel_ln_bw_5061c0(s, 0u);
    IMU_CHECK(0x205u);

    if (g2_imu_gyro_enabled != 0u) {
        rc |= inv_imu_set_gyro_lp_avg_506150(s, 0u);
        rc |= inv_imu_set_gyro_ln_bw_506118(s, 0u);
        IMU_CHECK(0x20bu);
    }

    rc |= inv_imu_set_accel_fsr_5060ac(s, 3u); /* +-4 g */
    if (g2_imu_gyro_enabled != 0u)
        rc |= inv_imu_set_gyro_fsr_5060e0(s, 1u); /* +-2000 dps */
    IMU_CHECK(0x213u);

    rc |= inv_imu_edmp_init_5067c8(s);
    IMU_CHECK(0x217u);

    if (g2_imu_tilt_enabled != 0u) {
        int prior;
        rc |= inv_imu_edmp_b2s_init_over_sif_50839e(s);
        rc |= inv_imu_edmp_b2s_get_parameters_508402(s, &b2s);
        b2s.thr_cos_q30 = (uint32_t)(int32_t)(iar_cos_508e58((double)g2_imu_tilt_angle) *
                                              1073741824.0);
        b2s.mode = 2u;
        prior = rc;
        rc = inv_imu_edmp_b2s_set_parameters_50842e(s, &b2s, 50u);
        rc |= prior;
        IMU_CHECK(0x222u);
    }

    if (g2_imu_aid_feature_enabled != 0u) {
        rc |= inv_imu_edmp_aid_init_over_sif_5084d8(s, &aid_usecase);
        if (aid_usecase != 0u)
            rc = -1;
        rc |= inv_imu_edmp_aid_get_parameters_508548(s, &aid, 0u);
        aid.aid_device.aid_update_win = 50u;
        aid.aid_device.aid_alert_timer = 600u;
        aid.aid_device.aid_output_enable = 7u;
        aid.aid_device.aid_disable_multiple_interrupt = 1u;
        aid.aid_human.aid_update_win = 350u;
        aid.aid_human.aid_alert_timer = 3750u;
        aid.aid_human.aid_output_enable = 7u;
        aid.aid_human.aid_disable_multiple_interrupt = 1u;
        rc |= inv_imu_edmp_aid_set_parameters_50861a(s, &aid, 0u);
        rc |= inv_imu_adv_configure_wom_50481a(s, 3u, 3u, 3u, 0u, 0u);
        rc |= inv_imu_adv_enable_wom_504888(s);
        IMU_CHECK(0x23du);
    }

    if (g2_imu_tap_enabled != 0u) {
        rc |= inv_imu_edmp_get_tap_parameters_5069cc(s, &tap);
        tap.tap_tmin = 55u;
        tap.tap_tmax = 400u;
        tap.tap_min_jerk = 1400u;
        tap.tap_smudge_reject_th = 20u;
        tap.tap_min = 2u;
        rc |= inv_imu_edmp_set_tap_parameters_506b06(s, &tap);
        IMU_CHECK(0x248u);
    }

    rc |= inv_imu_edmp_get_powersave_parameters_50699a(s, &ps);
    if (g2_imu_powersave_enabled != 0u) {
        ps.power_save_en = 1u;
        rc |= inv_imu_adv_configure_wom_50481a(s, 13u, 13u, 13u, 1u, 0u);
        rc |= inv_imu_adv_enable_wom_504888(s);
    } else {
        ps.power_save_en = 0u;
    }
    rc |= inv_imu_edmp_set_powersave_parameters_506a6e(s, &ps);
    if ((uint8_t)(g2_imu_aid_feature_enabled | g2_imu_powersave_enabled) == 0u)
        rc |= inv_imu_adv_disable_wom_5048ba(s);

    if (g2_imu_gaf_enabled != 0u) {
        rc |= inv_imu_edmp_get_gaf_parameters_506bd2(s, &gaf);
        gaf.pdr_us = g2_imu_gaf_pdr_us;
        gaf.run_spherical = 1u;
        gaf.mag_dt_us = mag_ok != 0u ? 40000u : 0u;
        g2_imu_mag_accuracy = 0u;
        rc |= inv_imu_edmp_set_gaf_mag_bias_5075d6(s, g2_imu_mag_bias_q16, g2_imu_mag_accuracy);
        rc |= inv_imu_read_reg_508e5c(s, ICM_SW_PLL1_TRIM, 1u, &gaf.clock_variation);
        rc |= inv_imu_edmp_set_gaf_parameters_506eca(s, &gaf);
        rc |= inv_imu_edmp_set_gaf_mode_507694(s, g2_imu_gyro_enabled, mag_ok);
        IMU_CHECK(0x26cu);
        rc |= inv_imu_read_sram_508e8a(s, ICM_SRAM_GAF_CONFIG_GYR_DT_US, 4u, &gyr_dt_us);
    }

    rc |= inv_imu_set_accel_mode_505fcc(s, 2u); /* low power */
    IMU_CHECK(0x276u);
    (void)osDelay(10u);

    if (g2_imu_gyro_enabled != 0u) {
        if (g2_imu_gyro_low_power != 0u)
            rc |= inv_imu_set_gyro_mode_506008(s, 2u);
        else
            rc |= inv_imu_set_gyro_mode_506008(s, 3u);
        IMU_CHECK(0x281u);
        (void)osDelay(10u);
    }

    rc |= inv_imu_edmp_set_mounting_matrix_507710(s, g2_imu_mount_q14);
    if (mag_ok != 0u) {
        rc |= inv_imu_edmp_set_gaf_soft_iron_cor_matrix_507576(s, g2_imu_mount_q30);
        rc |= inv_imu_edmp_enable_gaf_soft_iron_cor_507ace(s);
    }
    IMU_CHECK(0x28du);

    rc |= invn_mag_load_ram_image_508a98(s, 0u);
    if (g2_imu_auto_mrm_enabled != 0u)
        rc |= invn_mag_enable_automrm_508ab4(s);
    else
        rc |= invn_mag_disable_automrm_508b5a(s);

    audio_uart_buffer_zero(&apex, sizeof apex, 0u);
    if (g2_imu_tilt_enabled != 0u) {
        rc |= inv_imu_edmp_b2s_enable_5082d0(s);
        apex.b2s = 1u;
    }
    if (g2_imu_aid_feature_enabled != 0u) {
        rc |= inv_imu_edmp_aid_enable_50872c(s);
        apex.aid_human = 1u;
        apex.aid_device = 1u;
    }
    if (g2_imu_gaf_enabled != 0u) {
        rc |= inv_imu_edmp_enable_gaf_507a30(s);
        IMU_CHECK(0x2aau);
    }
    if (g2_imu_tap_enabled != 0u) {
        rc |= inv_imu_edmp_enable_tap_5079bc(s);
        apex.tap = 1u;
    }

    audio_uart_buffer_zero(&it, sizeof it, 0u);
    it.edmp_event = 1u;
    if (g2_imu_gaf_enabled != 0u)
        it.fifo_ths = 1u;
    it.ui_drdy = 0u;
    rc |= inv_imu_set_config_int_50637c(s, 0u, &it);
    IMU_CHECK(0x2bdu);

    if (g2_imu_auto_mrm_enabled != 0u) {
        apex.gaf_mrm_chg = 1u;
        apex.gaf_mrm_run = 1u;
        apex.gaf_mrm_thr = 1u;
    }
    rc |= inv_imu_edmp_set_config_int_apex_507726(s, &apex);
    IMU_CHECK(0x2c8u);

    if (g2_imu_gaf_enabled != 0u) {
        int prior;
        rc |= inv_imu_adv_get_fifo_config_5059c0(s, &fifo);
        fifo.fifo_mode = 2u;  /* snapshot */
        fifo.fifo_depth = 7u; /* APEX depth */
        fifo.fifo_wm_th = g2_imu_fifo_watermark;
        fifo.hires_en = 0u;
        fifo.gyro_en = 1u;
        fifo.accel_en = 1u;
        fifo.fifo_wr_wm_gt_th = 1u;
        fifo.es1_en = 1u;
        fifo.es0_en = 1u;
        fifo.comp_en = 0u;
        fifo.tmst_fsync_en = 0u;
        fifo.es0_6b_9b = 1u;
        prior = rc;
        rc = inv_imu_adv_set_fifo_config_505aa2(s, &fifo);
        rc |= prior;
        IMU_CHECK(0x2deu);
    }

    if ((uint8_t)(g2_imu_gaf_enabled | g2_imu_tilt_enabled | g2_imu_aid_feature_enabled) != 0u ||
        g2_imu_tap_enabled != 0u) {
        int prior;
        rc |= inv_imu_edmp_unmask_int_src_5080fa(s, 0u, 3u); /* accel + gyro DRDY */
        prior = rc;
        rc = inv_imu_edmp_enable_5078a0(s);
        rc |= prior;
    }
    IMU_CHECK(0x2e9u);
    return (uint32_t)rc;
}

/* Caches the calibration mounting matrix: raw floats, Q14 for the EDMP
 * mounting matrix and Q30 (columns 0 and 1 negated) for the soft-iron
 * matrix. accel and gyro are unused. */
int32_t semantic_set_orientation_matrix(const float accel[3], const float gyro[3],
                                        const float matrix[9])
{
    int32_t i;

    (void)accel;
    (void)gyro;
    for (i = 0; i < 9; i++) {
        g2_imu_mount_matrix[i / 3][i % 3] = matrix[i];
        g2_imu_mount_q14[i] = (int16_t)(int32_t)(matrix[i] * 16384.0f);
        if (i == 2 || i == 5 || i == 8)
            g2_imu_mount_q30[i / 3][i % 3] = (int32_t)(matrix[i] * 1073741824.0f);
        else
            g2_imu_mount_q30[i / 3][i % 3] = (int32_t)(matrix[i] * -1.0f * 1073741824.0f);
    }
    return 0;
}

/* Head-up: pitch above the threshold while the low-passed accel Z is below
 * its sine threshold. Head-down: pitch 20 degrees under the threshold. */
uint32_t DRV_IMUCheckHeadUpEvent(void)
{
    uint32_t i;

    for (i = 0u; i < g2_imu_samples.count; i++) {
        g2_imu_sample_t *r = &g2_imu_samples.sample[i];
        float az = semantic_filter_update(r->accel[2], &g2_imu_headup_filter);
        int32_t threshold = (int32_t)audio_hub_motion_threshold_cell;

        if ((r->flags & IMU_SAMPLE_QUAT) != 0u && (float)threshold < r->euler[1] &&
            az < audio_hub_motion_threshold_sine_cell && g2_imu_head_down_state == 1u) {
            g2_imu_head_down_state = 0u;
            g2_imu_head_up_state = 1u;
            (void)semantic_emit_imu_event(G2_IMU_EVENT_HEAD_UP, 0u);
            if (IMU_LOG_ON())
                audio_log_extended(2u, imu_module, imu_path, fn_headup, 0x438u, headup_text,
                                   (double)r->euler[1], (int32_t)audio_hub_motion_threshold_cell);
            if (IMU_CLOG_ON())
                (void)compress_log_output(0x08800000u, headup_short, headup_short,
                                          (double)r->euler[1],
                                          (int32_t)audio_hub_motion_threshold_cell);
            continue;
        }
        if ((r->flags & IMU_SAMPLE_QUAT) != 0u &&
            r->euler[1] < (float)((int32_t)audio_hub_motion_threshold_cell - 20) &&
            g2_imu_head_up_state == 1u) {
            g2_imu_head_up_state = 0u;
            g2_imu_head_down_state = 1u;
            (void)semantic_emit_imu_event(G2_IMU_EVENT_HEAD_DOWN, 0u);
            if (IMU_LOG_ON())
                audio_log_extended(2u, imu_module, imu_path, fn_headup, 0x43du, headdown_text,
                                   (double)r->euler[1]);
            if (IMU_CLOG_ON())
                (void)compress_log_output(0x08400000u, headdown_short, headdown_short,
                                          (double)r->euler[1]);
        }
    }
    return 0u;
}

/* Reports compass calibration once, then at most every period ms the
 * heading of the newest fused sample when it moved by more than the delta. */
void DRV_IMUCheckCompassEvent(void)
{
    uint32_t now = osKernelGetTickCount();
    int32_t angle = 0;

    if (g2_imu_compass_cal_reported == 0u && g2_imu_compass_calibrated == 1u) {
        g2_imu_compass_cal_reported = 1u;
        (void)semantic_emit_imu_event(G2_IMU_EVENT_COMPASS_CAL, 1u);
        if (IMU_LOG_ON())
            audio_log_extended(2u, imu_module, imu_path, fn_compass, 0x466u, compass_cal1);
        if (IMU_CLOG_ON())
            (void)compress_log_output(0x08000000u, compass_cal1_short, compass_cal1_short);
    } else if (g2_imu_compass_cal_reported == 1u && g2_imu_compass_calibrated == 0u) {
        g2_imu_compass_cal_reported = 0u;
        if (IMU_LOG_ON())
            audio_log_extended(2u, imu_module, imu_path, fn_compass, 0x46au, compass_cal0);
        if (IMU_CLOG_ON())
            (void)compress_log_output(0x08000000u, compass_cal0_short, compass_cal0_short);
    }

    if (now - g2_imu_compass_last_tick >= audio_hub_motion_period_cell) {
        int32_t i;

        g2_imu_compass_last_tick = now;
        for (i = (int32_t)g2_imu_samples.count - 1; i >= 0; i--) {
            if ((g2_imu_samples.sample[i].flags & IMU_SAMPLE_QUAT) != 0u) {
                angle = (int32_t)g2_imu_samples.sample[i].heading;
                break;
            }
        }
        if ((int32_t)audio_hub_motion_duration_cell <
            iar_abs_509694(angle - g2_imu_compass_last_angle)) {
            (void)semantic_emit_imu_event(G2_IMU_EVENT_COMPASS_ANGLE, (uint32_t)angle);
            if (IMU_LOG_ON())
                audio_log_extended(2u, imu_module, imu_path, fn_compass, 0x478u, compass_event,
                                   angle, g2_imu_compass_last_angle);
            if (IMU_CLOG_ON())
                (void)compress_log_output(0x08800000u, compass_event_short, compass_event_short,
                                          angle, g2_imu_compass_last_angle);
            g2_imu_compass_last_angle = angle;
        }
    }
}

/* Fifth IMU user: every report_interval ms (counted in FIFO batches of
 * watermark * period) sends the newest accel vector. */
void semantic_forward_periodic_sample(void)
{
    const g2_imu_mode_row_t *row = &g2_imu_mode_table[g2_imu_mode_index];
    uint32_t batch_ms = row->fifo_watermark * row->period_us / 1000u;

    if (g2_imu_report_counter >= audio_hub_imu_report_interval_cell / batch_ms) {
        const g2_imu_sample_t *r;
        g2_imu_report_counter = 0u;
        r = &g2_imu_samples.sample[g2_imu_samples.count - 1u];
        imu_accel_report_send_4da6d4(r->accel[0], r->accel[1], r->accel[2]);
    }
    g2_imu_report_counter++;
}

/* After a FIFO batch: heading, mounting-matrix rotation, CSV capture and the
 * open IMU users. Mode 4 does none of it. */
uint32_t semantic_postprocess_samples(void)
{
    uint32_t i;

    if (g2_imu_mode_index == 4u)
        return 0u;
    for (i = 0u; i < g2_imu_samples.count; i++) {
        g2_imu_sample_t *r = &g2_imu_samples.sample[i];
        if ((r->flags & IMU_SAMPLE_QUAT) != 0u) {
            r->heading = (float)semantic_normalize_heading((int32_t)r->euler[2]);
            semantic_set_heading(r->euler[1]);
            semantic_set_magnetic_vector(r->euler);
        }
        if ((r->flags & IMU_SAMPLE_MAG) != 0u)
            semantic_transform_vector(r->mag, g2_imu_mount_matrix);
        semantic_transform_vector(r->accel, g2_imu_mount_matrix);
        semantic_transform_vector(r->gyro, g2_imu_mount_matrix);
    }
    DRV_IMUSaveRawDataToCSV();
    if (g2_imu_headup_open == 1u)
        (void)DRV_IMUCheckHeadUpEvent();
    if (g2_imu_compass_open == 1u)
        DRV_IMUCheckCompassEvent();
    if (g2_imu_dis_open == 1u)
        semantic_noop_sample_callback();
    if (g2_imu_type5_open == 1u)
        semantic_forward_periodic_sample();
    return 0u;
}

/* v = M v (row-major 3x3). */
void semantic_transform_vector(float v[3], const float m[3][3])
{
    float t[3] = {0.0f, 0.0f, 0.0f};
    uint32_t i;

    for (i = 0u; i < 3u; i++) {
        t[i] = v[0] * m[i][0];
        t[i] = t[i] + v[1] * m[i][1];
        t[i] = t[i] + v[2] * m[i][2];
    }
    v[0] = t[0];
    v[1] = t[1];
    v[2] = t[2];
}

/* out[i] = in[i] / 2^q. */
void semantic_fixed_vector_to_float(const int32_t *in, float *out, uint32_t q, uint8_t n)
{
    float scale = 1.0f / (float)(int32_t)(1u << q);
    int32_t i;

    for (i = 0; i < (int32_t)n; i++)
        out[i] = (float)in[i] * scale;
}

/* {w, x, y, z} -> rotation matrix -> {atan2(-R10, R00), atan2(-R21, R22),
 * asin(-R20)} in degrees. */
void semantic_quaternion_to_euler(const float q[4], float euler[3])
{
    float r[9];
    float x2 = q[1] * 2.0f;
    float y2 = q[2] * 2.0f;
    float z2 = q[3] * 2.0f;
    float wx = x2 * q[0], wy = y2 * q[0], wz = z2 * q[0];
    float xx = x2 * q[1], xy = y2 * q[1], xz = z2 * q[1];
    float yy = y2 * q[2], yz = z2 * q[2], zz = z2 * q[3];

    r[0] = 1.0f - (yy + zz);
    r[1] = xy - wz;
    r[2] = xz + wy;
    r[3] = xy + wz;
    r[4] = 1.0f - (xx + zz);
    r[5] = yz - wx;
    r[6] = xz - wy;
    r[7] = yz + wx;
    r[8] = 1.0f - (xx + yy);
    euler[0] = audio_uart_float_two_input_angle_50969c(-r[3], r[0]) * IMU_RAD_TO_DEG_F;
    euler[1] = audio_uart_float_two_input_angle_50969c(-r[7], r[8]) * IMU_RAD_TO_DEG_F;
    euler[2] = audio_uart_float_inverse_signed_509708(-r[6]) * IMU_RAD_TO_DEG_F;
}

/* adv_var.sensor_event_cb: one FIFO frame -> one sample record. ES0/ES1
 * carry the GAF (game/geomag rotation vector) frames decoded by the EDMP. */
void DRV_IMUDataParserCallback(const g2_inv_imu_sensor_event_t *event)
{
    g2_imu_samples_t *b = &g2_imu_samples;
    g2_inv_imu_edmp_gaf_outputs_t *gaf = &g2_imu_gaf_outputs;
    uint32_t idx = b->count;
    uint32_t period_ms = g2_imu_mode_table[g2_imu_mode_index].period_us / 1000u;
    g2_imu_sample_t *r;
    int32_t v[3];
    uint32_t k;

    if (idx >= IMU_SAMPLE_SLOTS) {
        if (IMU_LOG_ON())
            audio_log_extended(1u, imu_module, imu_path, fn_parser, 0x51cu, parser_index);
        if (IMU_CLOG_ON())
            (void)compress_log_output(0x04000000u, parser_index_short, parser_index_short);
        return;
    }
    r = &b->sample[idx];
    r->tick = period_ms * (idx - b->frame_count) + b->base_tick;

    if ((event->sensor_mask & 1) != 0) {
        audio_uart_buffer_zero(v, sizeof v, 0u);
        r->flags |= IMU_SAMPLE_ACCEL;
        for (k = 0u; k < 3u; k++)
            r->accel_raw[k] = event->accel[k];
        for (k = 0u; k < 3u; k++)
            v[k] = (int32_t)event->accel[k] * Q16_ACCEL_SCALE - g2_imu_accel_bias_q16[k];
        semantic_fixed_vector_to_float(v, r->accel, 16u, 3u);
    }

    if ((event->sensor_mask & 0x30) == 0x30 &&
        inv_imu_edmp_gaf_decode_fifo_507c94(&g2_imu_device, event->es0, event->es1, gaf) != -1 &&
        gaf->frame_complete != 0u) {
        if (gaf->mag_bias_valid != 0u) {
            g2_imu_mag_bias_valid = 1u;
            g2_imu_mag_accuracy = (uint8_t)gaf->mag_accuracy_flag;
            g2_imu_mag_anomalies = (uint8_t)gaf->mag_anomalies;
            g2_imu_mag_bias_q16[0] = gaf->mag_bias_q16[0];
            g2_imu_mag_bias_q16[1] = gaf->mag_bias_q16[1];
            g2_imu_mag_bias_q16[2] = gaf->mag_bias_q16[2];
            r->mag_accuracy = (uint8_t)gaf->mag_accuracy_flag;
            r->mag_anomalies = (uint8_t)gaf->mag_anomalies;
            if (g2_imu_mag_accuracy != 0u)
                g2_imu_compass_calibrated = 1u;
            if (g2_imu_mag_anomalies != 0u)
                g2_imu_compass_calibrated = 0u;
        }
        if (gaf->rmag_valid != 0u) {
            audio_uart_buffer_zero(v, sizeof v, 0u);
            r->flags |= IMU_SAMPLE_MAG;
            for (k = 0u; k < 3u; k++)
                r->mag_raw[k] = gaf->rmag[k];
            for (k = 0u; k < 3u; k++)
                v[k] = (int32_t)gaf->rmag[k] * Q16_MAG_SCALE - g2_imu_mag_bias_q16[k];
            semantic_fixed_vector_to_float(v, r->mag, 16u, 3u);
        }
        if (gaf->grv_quat_valid != 0u) {
            r->flags |= IMU_SAMPLE_QUAT;
            for (k = 0u; k < 4u; k++)
                r->quat_q30[k] = (int32_t)gaf->grv_quat_q14[k] * 65536;
        }
        if (gaf->gmrv_quat_valid != 0u && gaf->gmrv_heading_valid != 0u) {
            r->flags |= IMU_SAMPLE_QUAT;
            for (k = 0u; k < 4u; k++)
                r->quat_q30[k] = (int32_t)gaf->gmrv_quat_q14[k] * 65536;
        }
        if (gaf->rv_quat_valid != 0u && gaf->rv_heading_valid != 0u) {
            r->flags |= IMU_SAMPLE_QUAT;
            for (k = 0u; k < 4u; k++)
                r->quat_q30[k] = (int32_t)gaf->rv_quat_q14[k] * 65536;
        }
        if ((r->flags & IMU_SAMPLE_QUAT) != 0u) {
            float e0;
            semantic_fixed_vector_to_float(r->quat_q30, r->quat, 30u, 4u);
            semantic_quaternion_to_euler(r->quat, r->euler);
            /* Device axes: roll <- pitch', pitch <- -yaw', yaw <- roll'. */
            e0 = r->euler[0];
            r->euler[0] = r->euler[1];
            r->euler[1] = r->euler[2] * -1.0f;
            r->euler[2] = e0;
        }
        if (gaf->gyr_bias_valid != 0u) {
            g2_imu_gyro_bias_q16[0] = (int32_t)gaf->gyr_bias_q12[0] * 16;
            g2_imu_gyro_bias_q16[1] = (int32_t)gaf->gyr_bias_q12[1] * 16;
            g2_imu_gyro_bias_q16[2] = (int32_t)gaf->gyr_bias_q12[2] * 16;
        }
        audio_uart_buffer_zero(gaf, sizeof *gaf, 0u);
    }

    if ((event->sensor_mask & 2) != 0) {
        audio_uart_buffer_zero(v, sizeof v, 0u);
        r->flags |= IMU_SAMPLE_GYRO;
        for (k = 0u; k < 3u; k++)
            r->gyro_raw[k] = event->gyro[k];
        for (k = 0u; k < 3u; k++)
            v[k] = (int32_t)event->gyro[k] * Q16_GYRO_SCALE - g2_imu_gyro_bias_q16[k];
        semantic_fixed_vector_to_float(v, r->gyro, 16u, 3u);
    }

    b->count++;
    if (b->count > IMU_SAMPLE_SLOTS - 1u)
        b->count = 0u;
}

/* Newest slot whose gyro, accel and mag vectors are all non-zero (slot 0
 * when none); copies gyro, accel, mag (36 bytes) to the export buffer. */
const uint8_t *semantic_get_latest_complete_sample(void)
{
    const float *vec[3];
    const g2_imu_sample_t *r;
    uint32_t start = (g2_imu_samples.count + 19u) % IMU_SAMPLE_SLOTS;
    uint32_t sel = 0u;
    uint32_t n = 0u;
    uint32_t i, j, b;

    for (i = 0u; i < IMU_SAMPLE_SLOTS; i++) {
        uint32_t idx = (start + IMU_SAMPLE_SLOTS - i) % IMU_SAMPLE_SLOTS;
        const g2_imu_sample_t *c = &g2_imu_samples.sample[idx];
        uint8_t gyro_ok = !(c->gyro[0] == 0.0f && c->gyro[1] == 0.0f && c->gyro[2] == 0.0f);
        uint8_t accel_ok = !(c->accel[0] == 0.0f && c->accel[1] == 0.0f && c->accel[2] == 0.0f);
        uint8_t mag_ok = !(c->mag[0] == 0.0f && c->mag[1] == 0.0f && c->mag[2] == 0.0f);
        if (gyro_ok != 0u && accel_ok != 0u && mag_ok != 0u) {
            sel = idx;
            break;
        }
    }
    r = &g2_imu_samples.sample[sel];
    vec[0] = r->gyro;
    vec[1] = r->accel;
    vec[2] = r->mag;
    for (i = 0u; i < 3u; i++)
        for (j = 0u; j < 3u; j++)
            for (b = 0u; b < 4u; b++)
                g2_imu_latest_sample[n++] = ((const uint8_t *)&vec[i][j])[b];
    return g2_imu_latest_sample;
}

/* Stores the newest pitch (euler[1]); read back by the ALS pitch filter. */
G2_IMU_VFP void semantic_set_heading(float pitch)
{
    g2_imu_pitch = pitch;
}

int32_t semantic_get_heading_degrees(void)
{
    return (int32_t)g2_imu_pitch;
}

G2_IMU_VFP float semantic_get_heading_float(void)
{
    return g2_imu_pitch;
}

/* Accelerometer-only tilt of the newest sample: {0, pitch, roll} degrees.
 * Rotates the stored accel vector in place again before use. */
const float *semantic_get_orientation_vector(void)
{
    if (g2_imu_samples.count != 0u) {
        uint32_t idx = (g2_imu_samples.count - 1u) % IMU_SAMPLE_SLOTS;
        g2_imu_sample_t *r = &g2_imu_samples.sample[idx];
        if ((r->flags & IMU_SAMPLE_ACCEL) != 0u) {
            float norm, pitch, roll;
            semantic_transform_vector(r->accel, g2_imu_mount_matrix);
            norm = audio_uart_float_sqrt_4397a8(r->accel[1] * r->accel[1] +
                                                r->accel[2] * r->accel[2]);
            pitch = audio_uart_float_two_input_angle_50969c(r->accel[0] * -1.0f, norm);
            roll = audio_uart_float_two_input_angle_50969c(r->accel[1], r->accel[2]);
            g2_imu_orientation[0] = 0.0f;
            g2_imu_orientation[1] = (float)((double)pitch * IMU_RAD_TO_DEG_D);
            g2_imu_orientation[2] = (float)((double)roll * IMU_RAD_TO_DEG_D);
        }
    }
    return g2_imu_orientation;
}

int32_t DRV_IMUWriteCSVDataLine(uint32_t tick, const float accel[3], const float gyro[3],
                                const float mag[3], const float euler[3],
                                uint8_t accel_valid, uint8_t gyro_valid, uint8_t mag_valid)
{
    char line[256];
    float mx = 0.0f, my = 0.0f, mz = 0.0f;
    float gx = 0.0f, gy = 0.0f, gz = 0.0f;
    float ax = 0.0f, ay = 0.0f, az = 0.0f;
    int32_t len;

    if (mag_valid != 0u) {
        mx = mag[0];
        my = mag[1];
        mz = mag[2];
    }
    if (gyro_valid != 0u) {
        gx = gyro[0];
        gy = gyro[1];
        gz = gyro[2];
    }
    if (accel_valid != 0u) {
        ax = accel[0];
        ay = accel[1];
        az = accel[2];
    }
    len = g2_audio_dump_snprintf(line, sizeof line, csv_line_format, tick, (double)ax,
                                 (double)ay, (double)az, (double)gx, (double)gy, (double)gz,
                                 (double)mx, (double)my, (double)mz, (double)euler[0],
                                 (double)euler[1], (double)euler[2]);
    if (len >= (int32_t)sizeof line) {
        if (IMU_LOG_ON())
            audio_log_extended(1u, imu_module, imu_path, fn_csv_line, 0x635u, csv_overflow);
        if (IMU_CLOG_ON())
            (void)compress_log_output(0x04000000u, csv_overflow_short, csv_overflow_short);
        return -1;
    }
    if (file_write(line, 1u, (uint32_t)len, g2_imu_csv_file) != (uint32_t)len) {
        if (IMU_LOG_ON())
            audio_log_extended(1u, imu_module, imu_path, fn_csv_line, 0x63cu, csv_line_fail);
        if (IMU_CLOG_ON())
            (void)compress_log_output(0x04000000u, csv_line_fail_short, csv_line_fail_short);
        return -1;
    }
    g2_imu_csv_lines++;
    return 0;
}
