/* IMU glue, stock D:\01_workspace\s200_ap510b_iar_git\driver\sensor\imu\imu_icm45608.c.
 * Integer part of native 0x4a35b0..0x4a656e (the float functions are in
 * imu_icm45608_fp.c). Literal pools 0x4a37e0, 0x4a5374, 0x4a6584..0x4a6640.
 *
 * The TDK transport reaches the ICM-45608 through product I2C bus 4,
 * address 0x69. Bring-up (semantic_imu_init) power-cycles the rail on codec
 * GPIO channel 1, initialises the TDK device object, copies one row of the
 * work-mode table into the ODR cells and runs DRV_IMUSetSensorParameters.
 * DRV_IMUReadData is the sensor-hub tick: register data on DRDY, FIFO drain
 * and parse on FIFO threshold, EDMP events (TILT/B2S, AID, tap). */
#include <stdint.h>
#include <stddef.h>
#include "g2_hal_i2c.h"
#include "g2_imu.h"
#include "imu_icm45608_private.h"

/* ---- TDK driver (vendored 1.1.2) ---- */
extern int inv_imu_adv_init_504784(g2_inv_imu_device_t *s);
extern int inv_imu_adv_get_data_from_fifo_505888(g2_inv_imu_device_t *s, uint8_t *fifo,
                                                 uint16_t *frame_count);
extern int inv_imu_adv_parse_fifo_data_5058b2(g2_inv_imu_device_t *s, const uint8_t *fifo,
                                              uint16_t frame_count);
extern int inv_imu_get_who_am_i_505fbe(g2_inv_imu_device_t *s, uint8_t *who_am_i);
extern int inv_imu_get_register_data_5061f8(g2_inv_imu_device_t *s,
                                            g2_inv_imu_sensor_data_t *data);
extern int inv_imu_flush_fifo_5062c8(g2_inv_imu_device_t *s);
extern int inv_imu_set_config_int_50637c(g2_inv_imu_device_t *s, uint8_t num,
                                         const g2_inv_imu_int_state_t *it);
extern int inv_imu_set_pin_config_int_50655c(g2_inv_imu_device_t *s, uint8_t num,
                                             const g2_inv_imu_int_pin_config_t *conf);
extern int inv_imu_get_int_status_5065cc(g2_inv_imu_device_t *s, uint8_t num,
                                         g2_inv_imu_int_state_t *it);
/* Stock variant: Q14 int16 matrix, products accumulated in int32, >> 14. */
extern void inv_imu_remap_data_5066ee(int16_t data[3], const int16_t matrix_q14[9]);
extern int inv_imu_edmp_get_int_apex_status_507b00(g2_inv_imu_device_t *s,
                                                   g2_inv_imu_edmp_int_state_t *it);
extern int inv_imu_edmp_get_tap_data_507ba2(g2_inv_imu_device_t *s,
                                            g2_inv_imu_edmp_tap_data_t *data);
extern int inv_imu_edmp_aid_get_data_human_50880a(g2_inv_imu_device_t *s, uint8_t usecase,
                                                  uint8_t *state);
extern int inv_imu_edmp_aid_get_data_device_508830(g2_inv_imu_device_t *s, uint8_t usecase,
                                                   uint8_t *state);
/* Even addition to invn_mag.c: WHO_AM_I cached by invn_mag_init (0x508954);
 * -1 for NULL, -2 when no magnetometer answered. */
extern int invn_mag_get_whoami_508a4e(uint8_t *who_am_i);

/* ---- product callees ---- */
extern uint32_t g2_codec_gpio_write(uint32_t channel, uint32_t value,
                                    uint32_t unused_r2, uint32_t passthrough_r3); /* 0x509024 */
extern void g2_delay_us_491102(uint32_t us);
extern uint16_t hub_role_get(void);                     /* 0x4a6d50 */
extern uint32_t audio_wear_child_46b0ec(void);          /* SVC_Settings_InputEventCheck */
extern int32_t audio_uart_master_input_event(uint32_t device, uint32_t event,
                                             uint32_t value, uint32_t context); /* 0x465748 */
extern int32_t audio_uart_display_housekeep(void);      /* 0x47243a */
extern void g2_log_datetime_now_44a19a(void *record);   /* calendar record */
extern int32_t g2_audio_dump_snprintf(char *, uint32_t, const char *, ...); /* 0x44b728 */
extern uint32_t g2_log_module_length(const char *);     /* 0x44a43c strlen */
extern void *file_open(const char *path, const char *mode);                   /* 0x474550 */
extern int32_t file_close(void *file);                                         /* 0x4745f4 */
extern uint32_t file_write(const void *buf, uint32_t size, uint32_t count, void *file); /* 0x474682 */

static const char imu_module[] = "sensor_imu"; /* ROM 0x78ab44 */
static const char imu_path[] = "D:\\01_workspace\\s200_ap510b_iar_git\\driver\\sensor\\imu\\imu_icm45608.c"; /* ROM 0x6fade4 */
static const char imu_error_text[] = "IMU Error: At %s (line %d)"; /* ROM 0x76be14 */
static const char imu_error_short[] = "[sensor_imu]IMU Error: At %s (line %d)"; /* ROM 0x74a514 */

static const char fn_aid_print[] = "IMU_AIDStatePrint"; /* ROM 0x77f7ac */
static const char fn_aid_update[] = "IMU_AIDStateUpdate"; /* ROM 0x77f7c0 */
static const char fn_read_data[] = "DRV_IMUReadData"; /* ROM 0x7860e0 */
static const char fn_csv_header[] = "DRV_IMUWriteCSVHeader"; /* ROM 0x777b4c */
static const char fn_csv_start[] = "DRV_IMUStartRawDataCollection"; /* ROM 0x7603b0 */
static const char fn_csv_stop[] = "DRV_IMUStopRawDataCollection"; /* ROM 0x7603d0 */
static const char fn_csv_save[] = "DRV_IMUSaveRawDataToCSV"; /* ROM 0x777b94 */
static const char fn_imu_whoami[] = "DRV_IMUReadWhoAmI"; /* ROM 0x77f7e8 */
static const char fn_mag_whoami[] = "DRV_MAGReadWhoAmI"; /* ROM 0x77f7fc */

static const char aid_device[] = "device"; /* ROM 0x78d734 */
static const char aid_human[] = "human"; /* ROM 0x78d73c */
static const char aid_activity[] = "   %d ms   AID %s activity state detected"; /* ROM 0x73f108 */
static const char aid_activity_short[] = "[sensor_imu]   %d ms   AID %s activity state detected"; /* ROM 0x71f6b0 */
static const char aid_inactivity[] = "   %d ms   AID %s inactivity state detected"; /* ROM 0x73f134 */
static const char aid_inactivity_short[] = "[sensor_imu]   %d ms   AID %s inactivity state detected"; /* ROM 0x71f6e8 */
static const char aid_sedentary[] = "   %d ms   AID %s sedentary alert detected"; /* ROM 0x73f160 */
static const char aid_sedentary_short[] = "[sensor_imu]   %d ms   AID %s sedentary alert detected"; /* ROM 0x71f720 */
static const char ev_tilt[] = "IMU event: TILT"; /* ROM 0x7860f0 */
static const char ev_tilt_short[] = "[sensor_imu]IMU event: TILT"; /* ROM 0x76be30 */
static const char ev_tap_double[] = "IMU event: TAP_DOUBLE"; /* ROM 0x777b04 */
static const char ev_tap_double_short[] = "[sensor_imu]IMU event: TAP_DOUBLE"; /* ROM 0x754bcc */
static const char ev_tap_num[] = "IMU event: TAP num = %d"; /* ROM 0x777b1c */
static const char ev_tap_num_short[] = "[sensor_imu]IMU event: TAP num = %d"; /* ROM 0x754bf0 */

static const char csv_path_format[] = "/log/imu_rawdata_%02d%02d%02d.csv"; /* ROM 0x754c38 */
static const char csv_header[] = "TIMESTAMP,ACC_X,ACC_Y,ACC_Z,GYR_X,GYR_Y,GYR_Z,MAG_X,MAG_Y,MAG_Z,Roll,Pitch,Yaw\n"; /* ROM 0x6ed798 */
static const char csv_mode[] = "w"; /* ROM 0x4a6364 */
static const char csv_header_fail[] = "[IMU] Failed to write CSV header"; /* ROM 0x754c5c */
static const char csv_header_fail_short[] = "[sensor_imu][IMU] Failed to write CSV header"; /* ROM 0x7346f4 */
static const char csv_already_open[] = "[IMU] CSV file already open, closing previous file"; /* ROM 0x72a050 */
static const char csv_already_open_short[] = "[sensor_imu][IMU] CSV file already open, closing previous file"; /* ROM 0x70c224 */
static const char csv_create_fail[] = "[IMU] Failed to create CSV file: %s"; /* ROM 0x754ca4 */
static const char csv_create_fail_short[] = "[sensor_imu][IMU] Failed to create CSV file: %s"; /* ROM 0x734754 */
static const char csv_started[] = "[IMU] Started raw data collection to file: %s"; /* ROM 0x734784 */
static const char csv_started_short[] = "[sensor_imu][IMU] Started raw data collection to file: %s"; /* ROM 0x715a84 */
static const char csv_not_open[] = "[IMU] No CSV file open"; /* ROM 0x777b7c */
static const char csv_not_open_short[] = "[sensor_imu][IMU] No CSV file open"; /* ROM 0x754cc8 */
static const char csv_close_fail[] = "[IMU] Failed to close CSV file"; /* ROM 0x7603f0 */
static const char csv_close_fail_short[] = "[sensor_imu][IMU] Failed to close CSV file"; /* ROM 0x73f1b8 */
static const char csv_stopped[] = "[IMU] Stopped raw data collection, saved %lu data points"; /* ROM 0x715ac0 */
static const char csv_stopped_short[] = "[sensor_imu][IMU] Stopped raw data collection, saved %lu data points"; /* ROM 0x6fae74 */
static const char csv_time_limit[] = "[IMU] Data collection time limit reached (2 minutes), auto-stopping"; /* ROM 0x70346c */
static const char csv_time_limit_short[] = "[sensor_imu][IMU] Data collection time limit reached (2 minutes), auto-stopping"; /* ROM 0x6ed7e8 */
static const char imu_whoami_fail[] = "[IMU] read WHO_AM_I failed, rc=%d"; /* ROM 0x754cec */
static const char imu_whoami_fail_short[] = "[sensor_imu][IMU] read WHO_AM_I failed, rc=%d"; /* ROM 0x7347b4 */
static const char mag_whoami_fail[] = "[MAG] read WHO_AM_I failed, rc=%d"; /* ROM 0x754d10 */
static const char mag_whoami_fail_short[] = "[sensor_imu][MAG] read WHO_AM_I failed, rc=%d"; /* ROM 0x7347e4 */

static const uint32_t imu_csv_time_limit_ms = 120000u; /* ROM 0x78f11c */

/* Stock error macro: level 1 "IMU Error: At <fn> (line <n>)". */
#define IMU_ERROR(fn, line)                                                          \
    do {                                                                             \
        if (IMU_LOG_ON())                                                            \
            audio_log_extended(1u, imu_module, imu_path, fn, line, imu_error_text,   \
                               fn, line);                                            \
        if (IMU_CLOG_ON())                                                           \
            (void)compress_log_output(0x04800000u, imu_error_short, imu_error_short, \
                                      fn, line);                                     \
    } while (0)

/* AID states reported by the EDMP image. */
enum { AID_ACTIVITY = 1u, AID_INACTIVITY = 2u, AID_SEDENTARY = 6u };

/* TDK transport read. Both length paths are the same call in stock (the
 * long-read branch never got its chunked variant). */
int semantic_bus_read(uint8_t reg, uint8_t *buf, uint32_t len)
{
    uint32_t rc;
    if (len < IMU_BUS_MAX_READ + 1u)
        rc = hal_i2c_transfer_full(IMU_I2C_BUS, IMU_I2C_ADDR, &reg, 1u, buf, len);
    else
        rc = hal_i2c_transfer_full(IMU_I2C_BUS, IMU_I2C_ADDR, &reg, 1u, buf, len);
    return rc != 0u ? -1 : 0;
}

/* TDK transport write: register byte and payload joined in one transaction. */
int semantic_bus_write(uint8_t reg, const uint8_t *buf, uint32_t len)
{
    uint32_t rc = hal_i2c_transfer_joined(IMU_I2C_BUS, IMU_I2C_ADDR, &reg, 1u, buf, len);
    return rc != 0u ? -1 : 0;
}

/* Fills the TDK device object, runs inv_imu_adv_init (3 ms wait, WHO_AM_I
 * 0x81 check, soft reset), configures INT1 active-high/pulse/push-pull,
 * installs the FIFO event callback and resets the head-up filter. */
int semantic_device_context_init(void)
{
    g2_inv_imu_device_t *s = &g2_imu_device;
    g2_inv_imu_int_pin_config_t pin;
    int rc;

    s->transport.read_reg = semantic_bus_read;
    s->transport.write_reg = semantic_bus_write;
    s->transport.serif_type = 0u;
    s->transport.sleep_us = g2_delay_us_491102;
    rc = inv_imu_adv_init_504784(s);
    pin.int_polarity = 1u;
    pin.int_mode = 0u;
    pin.int_drive = 0u;
    rc |= inv_imu_set_pin_config_int_50655c(s, 0u, &pin);
    s->sensor_event_cb = DRV_IMUDataParserCallback;
    semantic_filter_init(&g2_imu_headup_filter);
    return rc;
}

/* Maps a mode row's sample period (us) to the accel/gyro ODR codes and the
 * APEX ODR, and copies the gyro flag, GAF PDR and FIFO watermark. */
int32_t semantic_apply_odr_config(const g2_imu_mode_row_t *row)
{
    switch (row->period_us) {
    case 1000u: /* 800 Hz */
        g2_imu_accel_odr = 6u;
        g2_imu_gyro_odr = 6u;
        g2_imu_apex_odr = 5u;
        break;
    case 2500u: /* 400 Hz */
        g2_imu_accel_odr = 7u;
        g2_imu_gyro_odr = 7u;
        g2_imu_apex_odr = 4u;
        break;
    case 5000u: /* 200 Hz */
        g2_imu_accel_odr = 8u;
        g2_imu_gyro_odr = 8u;
        g2_imu_apex_odr = 3u;
        break;
    case 10000u: /* 100 Hz */
        g2_imu_accel_odr = 9u;
        g2_imu_gyro_odr = 9u;
        g2_imu_apex_odr = 2u;
        break;
    case 20000u: /* 50 Hz */
        g2_imu_accel_odr = 10u;
        g2_imu_gyro_odr = 10u;
        g2_imu_apex_odr = 1u;
        break;
    case 40000u: /* 25 Hz */
        g2_imu_accel_odr = 11u;
        g2_imu_gyro_odr = 11u;
        g2_imu_apex_odr = 0u;
        break;
    default:
        return -1;
    }
    g2_imu_gyro_enabled = (uint8_t)((row->flags >> 1) & 1u);
    g2_imu_gaf_pdr_us = row->gaf_pdr_us;
    g2_imu_fifo_watermark = (uint16_t)row->fifo_watermark;
    return 0;
}

/* IMU rail off for 100 ms, then on with 5 ms settle. */
void semantic_sensor_power_cycle(void)
{
    (void)g2_codec_gpio_write(IMU_POWER_CHANNEL, 0u, 0u, 0u);
    (void)osDelay(100u);
    (void)g2_codec_gpio_write(IMU_POWER_CHANNEL, 1u, 0u, 0u);
    (void)osDelay(5u);
}

void semantic_sensor_reset_line(void)
{
    (void)g2_codec_gpio_write(IMU_POWER_CHANNEL, 0u, 0u, 0u);
}

int32_t semantic_imu_init(uint8_t mode)
{
    if (mode >= G2_IMU_MODE_COUNT)
        return -1;
    semantic_sensor_power_cycle();
    (void)semantic_device_context_init();
    (void)semantic_apply_odr_config(&g2_imu_mode_table[mode]);
    (void)DRV_IMUSetSensorParameters(&g2_imu_mode_table[mode]);
    g2_imu_mode_index = mode;
    return 0;
}

void IMU_AIDStatePrint(uint8_t state, uint8_t is_device)
{
    uint32_t tick = osKernelGetTickCount();
    if (state == AID_ACTIVITY) {
        if (IMU_LOG_ON())
            audio_log_extended(3u, imu_module, imu_path, fn_aid_print, 0x378u, aid_activity,
                               tick, is_device != 0u ? aid_device : aid_human);
        if (IMU_CLOG_ON())
            (void)compress_log_output(0x0c800000u, aid_activity_short, aid_activity_short,
                                      tick, is_device != 0u ? aid_device : aid_human);
    } else if (state == AID_INACTIVITY) {
        if (IMU_LOG_ON())
            audio_log_extended(3u, imu_module, imu_path, fn_aid_print, 0x37au, aid_inactivity,
                               tick, is_device != 0u ? aid_device : aid_human);
        if (IMU_CLOG_ON())
            (void)compress_log_output(0x0c800000u, aid_inactivity_short, aid_inactivity_short,
                                      tick, is_device != 0u ? aid_device : aid_human);
    } else if (state == AID_SEDENTARY) {
        if (IMU_LOG_ON())
            audio_log_extended(3u, imu_module, imu_path, fn_aid_print, 0x37cu, aid_sedentary,
                               tick, is_device != 0u ? aid_device : aid_human);
        if (IMU_CLOG_ON())
            (void)compress_log_output(0x0c800000u, aid_sedentary_short, aid_sedentary_short,
                                      tick, is_device != 0u ? aid_device : aid_human);
    }
}

/* When both AID instances report a sedentary alert the FIFO-threshold IRQ is
 * dropped (EDMP events only) and the "static" cell is raised for the display;
 * any other combination restores FIFO streaming. */
int IMU_AIDStateUpdate(uint8_t device_state, uint8_t human_state)
{
    g2_inv_imu_int_state_t it;
    int rc;

    audio_uart_buffer_zero(&it, sizeof it, 0u);
    if (device_state == AID_SEDENTARY && human_state == AID_SEDENTARY) {
        it.edmp_event = 1u;
        it.fifo_ths = 0u;
        it.ui_drdy = 0u;
        if (g2_imu_aid_enabled_cell == 0u) {
            g2_imu_aid_enabled_cell = 1u;
            (void)audio_uart_display_housekeep();
        }
    } else {
        it.edmp_event = 1u;
        it.fifo_ths = 1u;
        it.ui_drdy = 0u;
        if (g2_imu_aid_enabled_cell == 1u) {
            g2_imu_aid_enabled_cell = 0u;
            (void)audio_uart_display_housekeep();
        }
    }
    rc = inv_imu_flush_fifo_5062c8(&g2_imu_device);
    if (rc != 0) {
        IMU_ERROR(fn_aid_update, 0x39cu);
    } else {
        rc = inv_imu_set_config_int_50637c(&g2_imu_device, 0u, &it);
        if (rc != 0)
            IMU_ERROR(fn_aid_update, 0x39eu);
    }
    return rc;
}

uint32_t DRV_IMUReadData(uint32_t tick)
{
    g2_inv_imu_device_t *s = &g2_imu_device;
    g2_inv_imu_int_state_t it;
    uint16_t frame_count;
    uint8_t aid_state;
    int rc;

    audio_uart_buffer_zero(&it, sizeof it, 0u);
    frame_count = 0u;
    aid_state = 0u;
    rc = inv_imu_get_int_status_5065cc(s, 0u, &it);
    if (rc != 0) {
        IMU_ERROR(fn_read_data, 0x3aau);
        return (uint32_t)rc;
    }

    if (it.ui_drdy != 0u) {
        g2_inv_imu_sensor_data_t *d = &g2_imu_register_data;
        uint32_t valid = 0u; /* computed by stock, never consumed */
        int32_t gyro[3];

        rc |= inv_imu_get_register_data_5061f8(s, d);
        if (rc != 0) {
            IMU_ERROR(fn_read_data, 0x3b1u);
            return (uint32_t)rc;
        }
        inv_imu_remap_data_5066ee(d->accel, g2_imu_mount_q14);
        inv_imu_remap_data_5066ee(d->gyro, g2_imu_mount_q14);
        gyro[0] = d->gyro[0];
        gyro[1] = d->gyro[1];
        gyro[2] = d->gyro[2];
        (void)gyro;
        if (g2_imu_accel_enabled != 0u || g2_imu_gyro_enabled != 0u) {
            if (g2_imu_accel_enabled != 0u && d->accel[0] != INT16_MIN &&
                d->accel[1] != INT16_MIN && d->accel[2] != INT16_MIN)
                valid |= 1u;
            if (g2_imu_gyro_enabled != 0u && d->gyro[0] != INT16_MIN &&
                d->gyro[1] != INT16_MIN && d->gyro[2] != INT16_MIN)
                valid |= 2u;
        }
        (void)valid;
    }

    if (it.fifo_ths != 0u) {
        audio_uart_buffer_zero(&g2_imu_samples, sizeof g2_imu_samples, 0u);
        g2_imu_samples.base_tick = tick;
        rc = inv_imu_adv_get_data_from_fifo_505888(s, g2_imu_fifo_mirror, &frame_count);
        if (rc != 0) {
            IMU_ERROR(fn_read_data, 0x3cdu);
            return (uint32_t)rc;
        }
        g2_imu_samples.frame_count = frame_count;
        rc = inv_imu_adv_parse_fifo_data_5058b2(s, g2_imu_fifo_mirror, frame_count);
        if (rc != 0) {
            IMU_ERROR(fn_read_data, 0x3d0u);
            return (uint32_t)rc;
        }
        (void)semantic_postprocess_samples();
    }

    rc = 0;
    if (it.edmp_event != 0u) {
        g2_inv_imu_edmp_int_state_t apex;
        g2_inv_imu_edmp_tap_data_t tap;

        audio_uart_buffer_zero(&apex, sizeof apex, 0u);
        rc = inv_imu_edmp_get_int_apex_status_507b00(s, &apex);
        if (rc != 0) {
            IMU_ERROR(fn_read_data, 0x3d8u);
            return (uint32_t)rc;
        }
        if (g2_imu_tilt_enabled != 0u && apex.b2s != 0u) {
            if (IMU_LOG_ON())
                audio_log_extended(2u, imu_module, imu_path, fn_read_data, 0x3dau, ev_tilt);
            if (IMU_CLOG_ON())
                (void)compress_log_output(0x08000000u, ev_tilt_short, ev_tilt_short);
        }
        if (g2_imu_aid_feature_enabled != 0u && apex.aid_device != 0u) {
            rc |= inv_imu_edmp_aid_get_data_device_508830(s, 0u, &aid_state);
            g2_imu_aid_device_state = aid_state;
            IMU_AIDStatePrint(g2_imu_aid_device_state, 1u);
            (void)IMU_AIDStateUpdate(g2_imu_aid_device_state, g2_imu_aid_human_state);
        }
        if (g2_imu_aid_feature_enabled != 0u && apex.aid_human != 0u) {
            rc |= inv_imu_edmp_aid_get_data_human_50880a(s, 0u, &aid_state);
            g2_imu_aid_human_state = aid_state;
            IMU_AIDStatePrint(g2_imu_aid_human_state, 0u);
            (void)IMU_AIDStateUpdate(g2_imu_aid_device_state, g2_imu_aid_human_state);
        }
        if (g2_imu_tap_enabled != 0u && apex.tap != 0u) {
            rc |= inv_imu_edmp_get_tap_data_507ba2(s, &tap);
            if (rc != 0) {
                IMU_ERROR(fn_read_data, 0x3f1u);
                return (uint32_t)rc;
            }
            if (tap.num == 2u) {
                if (IMU_LOG_ON())
                    audio_log_extended(2u, imu_module, imu_path, fn_read_data, 0x3f3u,
                                       ev_tap_double);
                if (IMU_CLOG_ON())
                    (void)compress_log_output(0x08000000u, ev_tap_double_short,
                                              ev_tap_double_short);
            } else {
                if (IMU_LOG_ON())
                    audio_log_extended(2u, imu_module, imu_path, fn_read_data, 0x3f5u,
                                       ev_tap_num, tap.num);
                if (IMU_CLOG_ON())
                    (void)compress_log_output(0x08400000u, ev_tap_num_short, ev_tap_num_short,
                                              tap.num);
            }
        }
    }
    return (uint32_t)rc;
}

/* Forwards an IMU event to the master-input path when input events are
 * allowed (worn / settings gate). */
uint32_t semantic_emit_imu_event(uint32_t event, uint32_t value)
{
    uint16_t role = hub_role_get();
    if (audio_wear_child_46b0ec() == 0u)
        return 0u;
    (void)audio_uart_master_input_event(role, event, value, 0u);
    return 0u;
}

/* Compass heading from yaw: (yaw + 90) wrapped into 0..359. */
int32_t semantic_normalize_heading(int32_t yaw)
{
    int32_t h = yaw + 90;
    if (h < 0)
        h += 360;
    return h % 360;
}

/* Hook run for the "dis" IMU user; empty in stock. */
void semantic_noop_sample_callback(void)
{
}

/* Stores the latest {roll, pitch, yaw}. */
void semantic_set_magnetic_vector(const float euler[3])
{
    float *dst = g2_imu_euler;
    dst[0] = euler[0];
    dst[1] = euler[1];
    dst[2] = euler[2];
}

const float *semantic_get_magnetic_vector(void)
{
    return g2_imu_euler;
}

/* "/log/imu_rawdata_HHMMSS.csv" from calendar words 6..8 of the local time. */
void semantic_build_raw_csv_path(char *path, uint32_t size)
{
    uint32_t cal[10];
    g2_log_datetime_now_44a19a(cal);
    (void)g2_audio_dump_snprintf(path, size, csv_path_format, cal[6], cal[7], cal[8]);
}

int32_t DRV_IMUWriteCSVHeader(void)
{
    uint32_t written = file_write(csv_header, 1u, g2_log_module_length(csv_header),
                                  g2_imu_csv_file);
    if (written == g2_log_module_length(csv_header))
        return 0;
    if (IMU_LOG_ON())
        audio_log_extended(1u, imu_module, imu_path, fn_csv_header, 0x60fu, csv_header_fail);
    if (IMU_CLOG_ON())
        (void)compress_log_output(0x04000000u, csv_header_fail_short, csv_header_fail_short);
    return -1;
}

void DRV_IMUStartRawDataCollection(void)
{
    char path[32];

    if (g2_imu_csv_active != 0u) {
        if (IMU_LOG_ON())
            audio_log_extended(2u, imu_module, imu_path, fn_csv_start, 0x64au, csv_already_open);
        if (IMU_CLOG_ON())
            (void)compress_log_output(0x08000000u, csv_already_open_short,
                                      csv_already_open_short);
        DRV_IMUStopRawDataCollection();
    }
    audio_uart_buffer_zero(path, sizeof path, 0u);
    semantic_build_raw_csv_path(path, sizeof path);
    g2_imu_csv_file = file_open(path, csv_mode);
    if (g2_imu_csv_file == NULL) {
        if (IMU_LOG_ON())
            audio_log_extended(1u, imu_module, imu_path, fn_csv_start, 0x655u, csv_create_fail,
                               path);
        if (IMU_CLOG_ON())
            (void)compress_log_output(0x04400000u, csv_create_fail_short, csv_create_fail_short,
                                      path);
        return;
    }
    if (DRV_IMUWriteCSVHeader() != 0) {
        if (IMU_LOG_ON())
            audio_log_extended(1u, imu_module, imu_path, fn_csv_start, 0x65bu, csv_header_fail);
        if (IMU_CLOG_ON())
            (void)compress_log_output(0x04000000u, csv_header_fail_short, csv_header_fail_short);
        (void)file_close(g2_imu_csv_file);
        return;
    }
    g2_imu_csv_active = 1u;
    g2_imu_csv_lines = 0u;
    g2_imu_csv_start_tick = osKernelGetTickCount();
    if (IMU_LOG_ON())
        audio_log_extended(3u, imu_module, imu_path, fn_csv_start, 0x664u, csv_started, path);
    if (IMU_CLOG_ON())
        (void)compress_log_output(0x0c400000u, csv_started_short, csv_started_short, path);
}

void DRV_IMUStopRawDataCollection(void)
{
    if (g2_imu_csv_active == 0u) {
        if (IMU_LOG_ON())
            audio_log_extended(2u, imu_module, imu_path, fn_csv_stop, 0x66du, csv_not_open);
        if (IMU_CLOG_ON())
            (void)compress_log_output(0x08000000u, csv_not_open_short, csv_not_open_short);
        return;
    }
    g2_imu_csv_active = 0u;
    if (file_close(g2_imu_csv_file) != 0) {
        if (IMU_LOG_ON())
            audio_log_extended(1u, imu_module, imu_path, fn_csv_stop, 0x674u, csv_close_fail);
        if (IMU_CLOG_ON())
            (void)compress_log_output(0x04000000u, csv_close_fail_short, csv_close_fail_short);
    } else {
        if (IMU_LOG_ON())
            audio_log_extended(3u, imu_module, imu_path, fn_csv_stop, 0x676u, csv_stopped,
                               g2_imu_csv_lines);
        if (IMU_CLOG_ON())
            (void)compress_log_output(0x0c400000u, csv_stopped_short, csv_stopped_short,
                                      g2_imu_csv_lines);
    }
    g2_imu_csv_file = NULL;
    g2_imu_csv_start_tick = 0u;
    g2_imu_csv_lines = 0u;
}

/* Appends every parsed sample of the batch; stops after two minutes. */
void DRV_IMUSaveRawDataToCSV(void)
{
    uint32_t i;

    if (g2_imu_csv_active == 0u)
        return;
    if (osKernelGetTickCount() - g2_imu_csv_start_tick >= imu_csv_time_limit_ms) {
        if (IMU_LOG_ON())
            audio_log_extended(3u, imu_module, imu_path, fn_csv_save, 0x68du, csv_time_limit);
        if (IMU_CLOG_ON())
            (void)compress_log_output(0x0c000000u, csv_time_limit_short, csv_time_limit_short);
        DRV_IMUStopRawDataCollection();
        return;
    }
    for (i = 0u; i < g2_imu_samples.count; i++) {
        const g2_imu_sample_t *r = &g2_imu_samples.sample[i];
        (void)DRV_IMUWriteCSVDataLine(r->tick, r->accel, r->gyro, r->mag, r->euler,
                                      (uint8_t)(r->flags & 1u),
                                      (uint8_t)((r->flags >> 1) & 1u),
                                      (uint8_t)((r->flags >> 3) & 1u));
    }
}

int32_t DRV_IMUReadWhoAmI(uint32_t *id)
{
    uint8_t who;
    int rc;

    if (id == NULL)
        return -1;
    who = 0u;
    rc = inv_imu_get_who_am_i_505fbe(&g2_imu_device, &who);
    if (rc != 0) {
        if (IMU_LOG_ON())
            audio_log_extended(1u, imu_module, imu_path, fn_imu_whoami, 0x6a8u, imu_whoami_fail,
                               rc);
        if (IMU_CLOG_ON())
            (void)compress_log_output(0x04400000u, imu_whoami_fail_short, imu_whoami_fail_short,
                                      rc);
        return rc;
    }
    *id = who;
    return 0;
}

int32_t DRV_MAGReadWhoAmI(uint32_t *id)
{
    uint8_t who;
    int rc;

    if (id == NULL)
        return -1;
    who = 0u;
    rc = invn_mag_get_whoami_508a4e(&who);
    if (rc != 0) {
        if (IMU_LOG_ON())
            audio_log_extended(1u, imu_module, imu_path, fn_mag_whoami, 0x6b7u, mag_whoami_fail,
                               rc);
        if (IMU_CLOG_ON())
            (void)compress_log_output(0x04400000u, mag_whoami_fail_short, mag_whoami_fail_short,
                                      rc);
        return rc;
    }
    *id = who;
    return 0;
}

uint32_t semantic_get_state_20074674(void) { return g2_imu_headup_open; }
uint32_t semantic_get_state_20074678(void) { return g2_imu_compass_open; }
uint32_t semantic_get_state_2007467c(void) { return g2_imu_dis_open; }
uint32_t semantic_get_state_20074680(void) { return g2_imu_type5_open; }
void semantic_set_state_20074674(uint32_t open) { g2_imu_headup_open = open; }
void semantic_set_state_20074678(uint32_t open) { g2_imu_compass_open = open; }
void semantic_set_state_2007467c(uint32_t open) { g2_imu_dis_open = open; }
uint32_t semantic_get_flag_20074fdc(void) { return g2_imu_compass_calibrated; }
void semantic_set_state_20074680(uint32_t open) { g2_imu_type5_open = open; }
