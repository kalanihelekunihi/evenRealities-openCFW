/* eAT production-test command handlers (core, IMU, screen, ALS, brightness).
 * Native 0x5a5720..0x5a595e, literal pools 0x5a57b4..0x5a57ef, 0x5a5824..0x5a582f,
 * 0x5a589c..0x5a58a7 and 0x5a5960..0x5a5983. No source path string survives.
 * atImuEulerHandler 0x5a5864 is in eat_core_imu_euler.c (VFP profile).
 *
 * Registry ROM 0x6c9260..0x6c93af, rows {type, name, handler, 0}; the handler
 * gets the parameter text after the command and returns 1 when handled:
 *   AT^INFO 0, AT^RESET 0, AT^PSN 0, AT^IMU_RAWDATA 2, AT^IMU_EULER 0,
 *   AT^SCRN_X 2, AT^SCRN_Y 2, AT^ALS_READ 0, AT^ALS 0, AT^BRIGHTNESS 2,
 *   AT^ALS_SCALE_READ 0, AT^BRIGHTNESS_READ 0 (row type as stored). */
#include <stdint.h>
#include "g2_als.h"
#include "../sensor_hub.h"

#define PSN_LENGTH 14u
#define SCREEN_Y_LIMIT 193u /* accepted 0..192 although the message says 1 - 192 */
#define ALS_READ_BUFFER 100u

extern void at_core_output(const char *fmt, ...);
extern int32_t atoi_48d868(const char *text); /* strtol(text, NULL, 10) via 0x48d724 */
extern uint32_t g2_log_module_length(const char *text); /* strlen 0x44a43c */
extern int32_t g2_audio_dump_snprintf(char *buf, uint32_t size, const char *fmt, ...); /* 0x44b728 */
extern const char *hardware_version_string_57e6cc(void);
extern const char *codec_version_string_57e702(void);
extern const char *semantic_TouchLogCurrentVersion(void);
extern const char *SVC_NvdbReadSysData(uint32_t item);
extern int32_t SVC_NvdbWriteSysData(uint32_t item, const char *value);
extern const uint8_t *APP_BleAddressGet(void);
extern const char *APP_BleNameGet(void);
extern void audio_ble_radio_ready_44b0ae(void); /* system reset via 0x44ab24 */
extern uint32_t display_driver_set_brightness_46c984(uint32_t value); /* stores the screen Y offset and redraws 576x288 */
extern void settings_set_brightness_level(uint32_t level);
extern uint32_t service_settings_auto_brightness(void);
extern uint32_t als_function_38(void); /* ALS scale, Q10, 0x4ae946 */
extern uint8_t display_driver_ratio_cells_20003994[0xac]; /* RAM 0x20003994 NVDB system data */

static const char product_name[] = "S200"; /* ROM 0x78cc0c */
static const char fmt_product[] = "Product name:     [%s]\r\n"; /* ROM 0x769b4c */
static const char fmt_hardware[] = "Hardware version: [%s]\r\n"; /* ROM 0x769b68 */
static const char software_version[] = "2.2.6.10"; /* ROM 0x78a3a0 */
static const char fmt_software[] = "Software version: [%s]\r\n"; /* ROM 0x769b84 */
static const char fmt_codec[] = "Codec version:    [%s]\r\n"; /* ROM 0x769ba0 */
static const char fmt_touch[] = "Touch version:    [%s]\r\n"; /* ROM 0x769bbc */
static const char build_date[] = "Jul  6 2026"; /* ROM 0x78a3ac, __DATE__ */
static const char build_time[] = "21:37:47"; /* ROM 0x78a3b8, __TIME__ */
static const char fmt_compile[] = "Compile time:     [%s %s]\r\n"; /* ROM 0x769bd8 */
static const char fmt_sn[] = "Product SN:       [%s]\r\n"; /* ROM 0x769bf4 */
static const char fmt_ble_name[] = "BLE NAME:         [%s]\r\n"; /* ROM 0x769c10 */
static const char fmt_ble_addr[] = "BLE ADDR:         [%02X:%02X:%02X:%02X:%02X:%02X]\r\n"; /* ROM 0x727200 */
static const char info_ok[] = "INFO+OK\r\n"; /* ROM 0x78a3c4 */
static const char reset_ok[] = "RESET+OK\r\n"; /* ROM 0x78a3d0 */
static const char fmt_echo[] = "%s"; /* ROM 0x5a5824, inline literal */
static const char psn_bad[] = "AT^PSN: set PSN: The parameter is incorrect. Please enter the correct command (len %d)\r\n"; /* ROM 0x6df828 */
static const char psn_ok[] = "PSN+OK\r\n"; /* ROM 0x78a3e8 */
static const char raw_ok[] = "AT^IMU_RAWDATA+OK:type=%d\r\n"; /* ROM 0x769c2c */
static const char raw_bad[] = "AT^IMU_RAWDATA+ERROR: invalid parameter, use 1 to start or 0 to stop\r\n"; /* ROM 0x6f887c */
static const char scrn_x_ok[] = "AT^SCRN_X+OK\r\n"; /* ROM 0x785190 */
static const char scrn_y_bad[] = "AT^SCRN_Y Error,height value must be 1 - 192.\r\n"; /* ROM 0x731b74 */
static const char scrn_y_ok[] = "AT^SCRN_Y+OK\r\n"; /* ROM 0x7851a0 */
static const char als_read_fmt[] = "AT^ALS_READ+OK:ALS\xe5\x80\xbc=%u, LUX_BASE=%d\r\n"; /* ROM 0x747c74, UTF-8 "ALS值" */
static const char als_ok[] = "AT^ALS+OK:enable=%d\r\n"; /* ROM 0x775614 */
static const char brightness_ok[] = "AT^BRIGHTNESS+OK:brightness=%d\r\n"; /* ROM 0x7523b8 */
static const char scale_ok[] = "AT^ALS_SCALE_READ+OK:scale_q10=%u\r\n"; /* ROM 0x7523dc */
static const char brightness_read_ok[] = "AT^BRIGHTNESS_READ+OK:brightness=%u\r\n"; /* ROM 0x747c9c */

int32_t atInfoHandler(const char *param) {
    const uint8_t *addr;
    (void)param;
    at_core_output(fmt_product, product_name);
    at_core_output(fmt_hardware, hardware_version_string_57e6cc());
    at_core_output(fmt_software, software_version);
    at_core_output(fmt_codec, codec_version_string_57e702());
    at_core_output(fmt_touch, semantic_TouchLogCurrentVersion());
    at_core_output(fmt_compile, build_date, build_time);
    at_core_output(fmt_sn, SVC_NvdbReadSysData(0u));
    addr = APP_BleAddressGet();
    at_core_output(fmt_ble_name, APP_BleNameGet());
    /* Stored little-endian; printed most significant byte first. */
    at_core_output(fmt_ble_addr, addr[5], addr[4], addr[3], addr[2], addr[1], addr[0]);
    at_core_output(info_ok);
    return 1;
}

int32_t atResetHandler(const char *param) {
    (void)param;
    at_core_output(reset_ok);
    audio_ble_radio_ready_44b0ae();
    return 1;
}

/* Product serial number: exactly 14 characters, NVDB system item 0. */
int32_t atPsnHandler(const char *param) {
    if (g2_log_module_length(param) == PSN_LENGTH) {
        at_core_output(fmt_echo, param);
        (void)SVC_NvdbWriteSysData(0u, param);
    } else {
        at_core_output(psn_bad, PSN_LENGTH);
    }
    at_core_output(psn_ok);
    return 1;
}

/* 1 starts, 0 stops IMU raw-data CSV collection (hub message 4). */
int32_t atImuRawDataHandler(const char *param) {
    const int32_t type = atoi_48d868(param);
    if (type == 1)
        (void)hub_msg_send_id4(1u);
    else if (type == 0)
        (void)hub_msg_send_id4(0u);
    else {
        at_core_output(raw_bad);
        return 0;
    }
    at_core_output(raw_ok, type);
    return 1;
}

int32_t atScreenXHandler(const char *param) {
    (void)param;
    at_core_output(scrn_x_ok);
    return 1;
}

int32_t atScreenYHandler(const char *param) {
    const uint32_t height = (uint32_t)atoi_48d868(param);
    if (height < SCREEN_Y_LIMIT) {
        (void)display_driver_set_brightness_46c984(height);
        at_core_output(scrn_y_ok);
    } else {
        at_core_output(scrn_y_bad);
    }
    return 1;
}

/* Newest ALS peak-window sample and the NVDB LUX_BASE word (+0x28). */
int32_t atAlsReadHandler(const char *param) {
    char text[ALS_READ_BUFFER];
    const uint32_t als = als_function_09();
    const int32_t lux_base = *(const int32_t *)(const void *)&display_driver_ratio_cells_20003994[0x28];
    (void)param;
    (void)g2_audio_dump_snprintf(text, ALS_READ_BUFFER, als_read_fmt, als, lux_base);
    at_core_output(text);
    return 1;
}

int32_t atAlsHandler(const char *param) {
    const int32_t enable = atoi_48d868(param);
    if (enable == 1)
        (void)als_function_28(); /* DRV_ALSOpen */
    else if (enable == 0)
        (void)als_function_29(); /* DRV_ALSClose */
    at_core_output(als_ok, enable);
    return 1;
}

int32_t atBrightnessHandler(const char *param) {
    const int32_t level = atoi_48d868(param);
    settings_set_brightness_level((uint32_t)level);
    at_core_output(brightness_ok, level);
    return 1;
}

int32_t atAlsScaleReadHandler(const char *param) {
    (void)param;
    at_core_output(scale_ok, als_function_38());
    return 1;
}

int32_t atBrightnessReadHandler(const char *param) {
    (void)param;
    at_core_output(brightness_read_ok, service_settings_auto_brightness());
    return 1;
}
