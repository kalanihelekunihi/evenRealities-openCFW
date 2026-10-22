/* Product FreeRTOS-Plus-CLI "imu" command, stock directory
 * D:\01_workspace\s200_ap510b_iar_git\kernel\FreeRTOS-Plus-CLI\prvCommand\
 * (file name not retained). Native: handler 0x580824..0x580bfb, inline
 * strings 0x580bfc..0x580c03 and 0x580c10..0x580c17, pool
 * 0x580c18..0x580c77. The registrar 0x580c04 is in
 * a-59-cli-commands/prvCommand_registrars.c.
 *
 *   imu open|close <type>          HUB_Open/HUB_Close(type)
 *   imu rawdata <1|0>              raw-data collection (hub message 4)
 *   imu rnv acc|gyr|matrix         print the NV IMU calibration
 *   imu wnv acc|gyr <x y z>        write accel / gyro offsets
 *   imu wnv matrix <m0..m8>        write the 3x3 mounting matrix
 *   imu mode <n>                   hub message 1
 *   imu calib update               hub message 3 (see the note below)
 *   imu acc <1|0> <interval>       accelerometer stream, hub type 5
 *
 * Uses double-precision FPU instructions (vcvt.f64.f32 for the %f
 * arguments): profile g2-apollo-main-20. */
#include <stddef.h>
#include <stdint.h>
#include "../a-59-cli-commands/cli_commands.h"

#define IMU_HUB_TYPE_ACC 5u
#define IMU_MATRIX_WORDS 9u

extern int32_t audio_ble_hci_vendor_compare_44b610(const void *a, const void *b, uint32_t len); /* strncmp */
extern int32_t atoi_48d868(const char *text);
extern int32_t HUB_Open(uint8_t func_type);   /* 0x4a6d58 */
extern int32_t HUB_Close(uint8_t func_type);  /* 0x4a6dca */
extern uint32_t audio_hub_parameter_config_4a6e3c(uint32_t type, const int32_t *param); /* HUB_ParameterConfig */
extern int32_t hub_msg_send_id1(uint8_t mode);   /* 0x4a6a86 */
extern int32_t hub_msg_send_id3(void);           /* 0x4a6aca */
extern int32_t hub_msg_send_id4(uint8_t start);  /* 0x4a6aa8 */
extern int32_t nvdbSensorCaldataAgRead(float accel[3], float gyro[3], float matrix[9]); /* 0x5099f8 */
extern void nvdbSensorCaldataAgUpdate(const float *accel, const float *gyro,
                                      const float *matrix); /* 0x50999e */
/* IAR strtof (float return in s0). */
extern __attribute__((pcs("aapcs-vfp"))) float iar_strtof_595964(const char *text, char **endptr);

static const char s_open[] = "open";                    /* ROM 0x78e25c */
static const char s_close[] = "close";                  /* ROM 0x78e264 */
static const char s_rawdata[] = "rawdata";              /* ROM 0x78e26c */
static const char s_rnv[] = "rnv";                      /* ROM 0x580bfc */
static const char s_acc[] = "acc";                      /* ROM 0x580c00 */
static const char s_gyr[] = "gyr";                      /* ROM 0x580c10 */
static const char s_wnv[] = "wnv";                      /* ROM 0x580c14 */
static const char s_matrix[] = "matrix";                /* ROM 0x78e274 */
static const char s_mode[] = "mode";                    /* ROM 0x78e27c */
static const char s_calib[] = "calib";                  /* ROM 0x78e284 */
static const char s_update[] = "update";                /* ROM 0x78e28c */
static const char s_open_log[] = "IMU open type=%d\r\n";   /* ROM 0x782808 */
static const char s_close_log[] = "IMU close type=%d\r\n"; /* ROM 0x78281c */
static const char s_raw_start[] = "imu rawdata collection start\r\n"; /* ROM 0x763ef0 */
static const char s_raw_stop[] = "imu rawdata collection stop\r\n";   /* ROM 0x763f10 */
static const char s_raw_invalid[] =
    "imu rawdata: invalid parameter, use 1 to start or 0 to stop\r\n"; /* ROM 0x70e024 */
static const char s_raw_missing[] =
    "imu rawdata: missing parameter, use 1 to start or 0 to stop\r\n"; /* ROM 0x70e064 */
static const char s_rnv_acc[] = "imu rnv acc %.4f %.4f %.4f\r\n";          /* ROM 0x763f30 */
static const char s_rnv_gyr[] = "imu rnv gyr %.4f %.4f %.4f\r\n";          /* ROM 0x763f50 */
static const char s_rnv_m0[] = "imu rnv matrix[0] %.4f %.4f %.4f\r\n";     /* ROM 0x7586b8 */
static const char s_rnv_m1[] = "imu rnv matrix[1] %.4f %.4f %.4f\r\n";     /* ROM 0x7586dc */
static const char s_rnv_m2[] = "imu rnv matrix[2] %.4f %.4f %.4f\r\n";     /* ROM 0x758700 */
static const char s_rnv_bad[] =
    "imu rnv: The parameter is incorrect. Please enter the correct command\r\n"; /* ROM 0x6fc194 */
static const char s_wnv_bad[] = "imu wnv: The parameter is incorrect.\r\n"; /* ROM 0x74ce7c */
static const char s_acc_start[] = "imu acc start, interval = %d\r\n";       /* ROM 0x763f70 */
static const char s_acc_stop[] = "imu acc stop\r\n";                        /* ROM 0x7881a0 */
static const char s_acc_invalid[] =
    "imu acc: invalid parameter, use 1 to start or 0 to stop\r\n"; /* ROM 0x717c80 */
static const char s_imu_bad[] =
    "imu test: The parameter is incorrect. Please enter the correct command\r\n"; /* ROM 0x6f56a4 */

int32_t cli_cmd_imu_580824(char *write_buffer, size_t write_buffer_len, const char *command_string);

/* Parse `count` floats from parameters 3.. into out; 0 when one is missing. */
static int32_t imu_parse_floats(const char *command_string, float *out, uint32_t count,
                                int32_t *length)
{
    char *end;
    uint32_t i;

    for (i = 0u; i < count; i++) {
        const char *text = freertos_cli_get_parameter_5848fc(command_string, i + 3u, length);

        if (text == NULL)
            return 0;
        out[i] = iar_strtof_595964(text, &end);
    }
    return 1;
}

int32_t cli_cmd_imu_580824(char *write_buffer, size_t write_buffer_len, const char *command_string)
{
    int32_t length = 0;
    int32_t interval;
    float gyr_new[3];
    float acc_new[3];
    float matrix[IMU_MATRIX_WORDS];
    float gyr[3];
    float acc[3];
    float matrix_new[IMU_MATRIX_WORDS];
    const char *sub;
    const char *arg;
    int32_t value;

    (void)write_buffer;
    (void)write_buffer_len;
    sub = freertos_cli_get_parameter_5848fc(command_string, 1u, &length);

    if (audio_ble_hci_vendor_compare_44b610(sub, s_open, 4u) == 0) {
        value = atoi_48d868(freertos_cli_get_parameter_5848fc(command_string, 2u, &length));
        audio_ble_hci_boot_log_4733ee(s_open_log, value);
        (void)HUB_Open((uint8_t)value);
    } else if (audio_ble_hci_vendor_compare_44b610(sub, s_close, 5u) == 0) {
        value = atoi_48d868(freertos_cli_get_parameter_5848fc(command_string, 2u, &length));
        audio_ble_hci_boot_log_4733ee(s_close_log, value);
        (void)HUB_Close((uint8_t)value);
    } else if (audio_ble_hci_vendor_compare_44b610(sub, s_rawdata, 7u) == 0) {
        arg = freertos_cli_get_parameter_5848fc(command_string, 2u, &length);
        if (arg == NULL) {
            audio_ble_hci_boot_log_4733ee(s_raw_missing);
        } else {
            value = atoi_48d868(arg);
            if (value == 1) {
                audio_ble_hci_boot_log_4733ee(s_raw_start);
                (void)hub_msg_send_id4(1u);
            } else if (value == 0) {
                audio_ble_hci_boot_log_4733ee(s_raw_stop);
                (void)hub_msg_send_id4(0u);
            } else {
                audio_ble_hci_boot_log_4733ee(s_raw_invalid);
            }
        }
    } else if (audio_ble_hci_vendor_compare_44b610(sub, s_rnv, 3u) == 0) {
        arg = freertos_cli_get_parameter_5848fc(command_string, 2u, &length);
        (void)nvdbSensorCaldataAgRead(acc, gyr, matrix);
        if (audio_ble_hci_vendor_compare_44b610(arg, s_acc, 3u) == 0) {
            audio_ble_hci_boot_log_4733ee(s_rnv_acc, (double)acc[0], (double)acc[1], (double)acc[2]);
        } else if (audio_ble_hci_vendor_compare_44b610(arg, s_gyr, 3u) == 0) {
            audio_ble_hci_boot_log_4733ee(s_rnv_gyr, (double)gyr[0], (double)gyr[1], (double)gyr[2]);
        } else if (audio_ble_hci_vendor_compare_44b610(arg, s_matrix, 6u) == 0) {
            audio_ble_hci_boot_log_4733ee(s_rnv_m0, (double)matrix[0], (double)matrix[1],
                                          (double)matrix[2]);
            audio_ble_hci_boot_log_4733ee(s_rnv_m1, (double)matrix[3], (double)matrix[4],
                                          (double)matrix[5]);
            audio_ble_hci_boot_log_4733ee(s_rnv_m2, (double)matrix[6], (double)matrix[7],
                                          (double)matrix[8]);
        } else {
            audio_ble_hci_boot_log_4733ee(s_rnv_bad);
        }
    } else if (audio_ble_hci_vendor_compare_44b610(sub, s_wnv, 3u) == 0) {
        arg = freertos_cli_get_parameter_5848fc(command_string, 2u, &length);
        if (audio_ble_hci_vendor_compare_44b610(arg, s_acc, 3u) == 0) {
            if (imu_parse_floats(command_string, acc_new, 3u, &length) == 0) {
                audio_ble_hci_boot_log_4733ee(s_wnv_bad);
                return 0;
            }
            nvdbSensorCaldataAgUpdate(acc_new, NULL, NULL);
        } else if (audio_ble_hci_vendor_compare_44b610(arg, s_gyr, 3u) == 0) {
            if (imu_parse_floats(command_string, gyr_new, 3u, &length) == 0) {
                audio_ble_hci_boot_log_4733ee(s_wnv_bad);
                return 0;
            }
            nvdbSensorCaldataAgUpdate(NULL, gyr_new, NULL);
        } else if (audio_ble_hci_vendor_compare_44b610(arg, s_matrix, 6u) == 0) {
            if (imu_parse_floats(command_string, matrix_new, IMU_MATRIX_WORDS, &length) == 0) {
                audio_ble_hci_boot_log_4733ee(s_wnv_bad);
                return 0;
            }
            nvdbSensorCaldataAgUpdate(NULL, NULL, matrix_new);
        } else {
            audio_ble_hci_boot_log_4733ee(s_rnv_bad); /* stock reuses the "imu rnv:" text */
        }
    } else if (audio_ble_hci_vendor_compare_44b610(sub, s_mode, 4u) == 0) {
        value = atoi_48d868(freertos_cli_get_parameter_5848fc(command_string, 2u, &length));
        (void)hub_msg_send_id1((uint8_t)value);
    } else if (audio_ble_hci_vendor_compare_44b610(sub, s_calib, 5u) == 0) {
        /* Stock fetches parameter 2 but compares parameter 1 ("calib...")
         * with "update", so the calibration message is never sent. */
        (void)freertos_cli_get_parameter_5848fc(command_string, 2u, &length);
        if (audio_ble_hci_vendor_compare_44b610(sub, s_update, 6u) == 0)
            (void)hub_msg_send_id3();
    } else if (audio_ble_hci_vendor_compare_44b610(sub, s_acc, 3u) == 0) {
        value = atoi_48d868(freertos_cli_get_parameter_5848fc(command_string, 2u, &length));
        interval = atoi_48d868(freertos_cli_get_parameter_5848fc(command_string, 3u, &length));
        if (value == 1) {
            (void)HUB_Open(IMU_HUB_TYPE_ACC);
            (void)audio_hub_parameter_config_4a6e3c(IMU_HUB_TYPE_ACC, &interval);
            audio_ble_hci_boot_log_4733ee(s_acc_start, interval);
        } else if (value == 0) {
            (void)HUB_Close(IMU_HUB_TYPE_ACC);
            audio_ble_hci_boot_log_4733ee(s_acc_stop);
        } else {
            audio_ble_hci_boot_log_4733ee(s_acc_invalid);
        }
    } else {
        audio_ble_hci_boot_log_4733ee(s_imu_bad);
    }
    return 0;
}
