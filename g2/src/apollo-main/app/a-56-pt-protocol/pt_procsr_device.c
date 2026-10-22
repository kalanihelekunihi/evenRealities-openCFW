/* Product-test command handlers (battery, canvas, version, IMU, touch, mic flag,
 * panel, lux rail, wear, board SN, MAC, case lid, restart), stock
 * D:\01_workspace\s200_ap510b_iar_git\platform\product_test\pt_protocol_procsr.c.
 * Native 0x56fdb4..0x570d16 and 0x571cd4..0x571fd4, 0x57222c..0x572c40
 * (the mic recording handlers 0x570d40..0x571cb6 are in pt_procsr_mic.c and
 * get_lux_info 0x57200c in pt_procsr_lux.c).
 *
 * Every handler is reached through pt_protocol_dispatch (0x56f4a0) as
 * handler(payload, length, rsp, rsp_len): payload[0] is the command byte and
 * arguments start at payload[4]. The handler writes a bare response
 * [rsp_cmd][0x01][0x03][data_len][data...] and its length; the dispatcher then
 * prepends 5a a5 ff <len> and appends the byte-sum checksum. Data byte 0 is the
 * status: 0 ok, 3 invalid argument, 5 not in product-test mode
 * (productModeGet() != 1). A NULL buffer or short frame returns -1 with no
 * response. The stock __func__ names (log strings) are given per handler.
 *
 * The TSV pt_cmd_NN labels do not match the dispatched command (the
 * command-map.tsv pairing is shifted); comments give the real command from
 * the dispatcher compare chain, which the reply byte rsp[0] always echoes. */
#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>
#include "g2_nvdb.h"

#define PT_PRODUCT_TEST_MODE 1u
#define PT_STATUS_OK 0u
#define PT_STATUS_NOT_TEST_MODE 5u
#define PT_DISPLAY_APP 0x10bu

/* View of the charger telemetry record at RAM 0x20073b18 (see g2_bq27427.h). */
typedef struct {
    uint32_t charge_status;  /* +0x00 nonzero while charging */
    int32_t soc;             /* +0x04 % */
    int32_t voltage_mv;      /* +0x08 */
    int32_t avg_current_ma;  /* +0x0c signed */
    int32_t temperature;     /* +0x10 */
    uint8_t soc_band_flag;   /* +0x14 */
} pt_charger_telemetry_view_t;

extern const pt_charger_telemetry_view_t g2_charger_telemetry;   /* RAM 0x20073b18 */
extern uint8_t display_driver_ratio_cells_20003994[0xac];         /* RAM 0x20003994 nvSysDt */
extern uint8_t audio_ble_adv_config_state[32u];                   /* RAM 0x20003838 NVDB record pointer table */
extern volatile uint8_t g2_production_lc3_enable;                 /* RAM 0x20004551 */
#define SYS_DT ((g2_nvdb_sys_dt_t *)(void *)display_driver_ratio_cells_20003994)

extern uint32_t audio_log_flags(void); /* 0x43d0ce */
extern void audio_log_extended(uint8_t, const char *, const char *, const char *, uint32_t, const char *, ...); /* 0x43d574 */
extern uint32_t compress_log_output(uint32_t, const char *, const char *, ...); /* 0x43ce9e */
extern void *aeabi_memset_43c0e4(void *dst, uint32_t len, int32_t value);
extern void *audio_queue_copy_bytes(void *dst, const void *src, uint32_t len); /* memcpy 0x439be4 */
extern uint32_t g2_log_module_length(const char *text);                       /* strlen 0x44a43c */
extern int32_t g2_lfs_memcmp(const void *a, const void *b, uint32_t length);  /* memcmp 0x4751c8 */
extern char *g2_strcpy_48d540(char *dst, const char *src);
extern int32_t audio_ble_format_to_buffer(char *dst, const char *format, ...); /* sprintf 0x4b4728 */
extern int32_t audio_ble_parse_version(const char *s, const char *format, ...); /* sscanf 0x475fc0 */
extern int32_t iar_abs_509694(int32_t v);
extern uint8_t productModeGet(void);                                           /* 0x4abe60 */
extern uint8_t *display_driver_brightness_ratio_cell_4af73a(uint32_t index);  /* SVC_NvdbGetSysData */
extern const uint8_t *audio_ble_hci_radio_mode_state_50938e(uint32_t index);  /* 1 = hardware version byte */
extern void box_detect_set_soc_4ac718(uint8_t soc);
extern void box_detect_set_charging_4ac72e(uint8_t charging);
extern void box_detect_set_lid_open_4ac744(uint8_t lid_open);
extern uint8_t *display_startup_state_get_44347a(void);
extern int32_t audio_uart_slave_display_start(uint32_t, const void *, uint32_t); /* 0x4441ec */
extern int32_t audio_uart_slave_display_stop(uint32_t, const void *, uint32_t);  /* 0x4443cc */
extern uint32_t display_driver_case4_apply(uint32_t, uint32_t, uint32_t);        /* 0x4ca1ee uled_mspi_setBrightness */
extern uint32_t display_driver_set_brightness_46c984(uint32_t value);
extern uint32_t display_driver_set_offsets_46c9dc(uint32_t horizontal, uint32_t vertical);
extern uint32_t display_driver_set_profile_46c9aa(uint32_t value);
extern uint32_t uled_set_display_offset(uint8_t x, uint8_t y);                   /* 0x4ca24a */
extern const uint8_t *semantic_get_latest_complete_sample(void);                 /* 0x4a5b90 */
extern int32_t DRV_TouchReadSensorDiff_55b6a8(void *out);
extern void pt_sensor_rail_power_off_58f950(void);
extern uint8_t wear_detect_sensor_state_get_502dae(void);

static const char module_tag[] = "pt_protocol_procsr"; /* ROM 0x7829fc */
static const char source_file[] = "D:\\01_workspace\\s200_ap510b_iar_git\\platform\\product_test\\pt_protocol_procsr.c"; /* ROM 0x6ef458 */
static const char para_null[] = "%s para is NULL\n"; /* ROM 0x782a74 */
static const char para_null_c[] = "[pt_protocol_procsr]%s para is NULL\n"; /* ROM 0x74d304 */
static const char denied[] = "permission denied current mode is not product test mode"; /* ROM 0x721c18 */
static const char denied_c[] = "[pt_protocol_procsr]permission denied current mode is not product test mode"; /* ROM 0x6f586c */

static int log_extended_on(void) { return (audio_log_flags() & 2u) != 0u; }
static int log_compressed_on(void) { return (audio_log_flags() & 1u) || (audio_log_flags() & 4u); }

/* Compressed-log word: level in bits 26+, argument count in bits 22+. */
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

/* Stock writes the response header inline with a running uint8_t index. */
#define PT_HEADER(rsp, idx, rsp_cmd, data_len) do { \
        (rsp)[(idx)++] = (rsp_cmd); \
        (rsp)[(idx)++] = 1u; \
        (rsp)[(idx)++] = 3u; \
        (rsp)[(idx)++] = (data_len); \
    } while (0)

/* Panel power-on sequence repeated inline by commands 0x38 and 0x25. */
#define PT_PANEL_POWER_ON() do { \
        (void)display_driver_case4_apply(100u, 0x1bbcu, 0x3fu); \
        (void)display_driver_set_brightness_46c984(0x60u); \
        (void)display_driver_set_offsets_46c9dc(0u, 0u); \
        (void)display_driver_set_profile_46c9aa(0x20u); \
    } while (0)

/* Command 0x13 (TSV label pt_cmd_11_handler) get_battery_status: payload[4] = case SoC (bit 7 = case charging),
 * payload[5] == 2 = case lid open. Reply 0x13 with own battery state. */
uint32_t pt_cmd_11_handler(const uint8_t *payload, uint8_t length, uint8_t *rsp, uint8_t *rsp_len)
{
    static const char fn[] = "get_battery_status"; /* ROM 0x782a88 */
    static const char pos[] = "Charging detected, current is positive (%d), setting current to -1"; /* ROM 0x704c10 */
    static const char pos_c[] = "[pt_protocol_procsr]Charging detected, current is positive (%d), setting current to -1"; /* ROM 0x6e49b0 */
    static const char neg[] = "Not charging, current is negative (%d), setting current to -1"; /* ROM 0x70e1e4 */
    static const char neg_c[] = "[pt_protocol_procsr]Not charging, current is negative (%d), setting current to -1"; /* ROM 0x6e96ac */
    const pt_charger_telemetry_view_t *bat = &g2_charger_telemetry;

    if (PT_BAD_ARGS(payload, length, rsp, rsp_len, 4u)) {
        PT_PARA_NULL(fn, 0x3f3u);
        return 0xffffffffu; /* -1 */
    }
    if (length >= 6u) {
        uint8_t box = payload[4];
        box_detect_set_soc_4ac718(box & 0x7fu);
        box_detect_set_charging_4ac72e((uint8_t)(box >> 7));
        if (length >= 7u)
            box_detect_set_lid_open_4ac744(payload[5] == 2u ? 1u : 0u);
    }
    uint8_t idx = 0;
    PT_HEADER(rsp, idx, 0x13u, 6u);
    rsp[idx++] = bat->soc_band_flag != 0u ? 1u : 0u;
    rsp[idx++] = (uint8_t)((uint32_t)bat->voltage_mv >> 8);
    rsp[idx++] = (uint8_t)bat->voltage_mv;
    rsp[idx++] = (uint8_t)bat->soc;
    int32_t current = bat->avg_current_ma;
    if (bat->charge_status == 0u) {
        if (current < 0) {
            PT_LOGN(4, 1, fn, 0x41fu, neg, neg_c, bat->avg_current_ma);
            current = -1;
        }
    } else if (current > 0) {
        PT_LOGN(4, 1, fn, 0x418u, pos, pos_c, bat->avg_current_ma);
        current = -1;
    }
    rsp[idx++] = current < 1 ? 1u : 0u; /* 1 = discharging */
    rsp[idx++] = (uint8_t)iar_abs_509694(current);
    *rsp_len = idx;
    return 0;
}

/* Command 0x11 (TSV label pt_cmd_0B_handler) get_battery_info: reply 0x11 with SoC, voltage/10 + 56, current sign
 * and magnitude, temperature sign and big-endian magnitude. */
uint32_t pt_cmd_0B_handler(const uint8_t *payload, uint8_t length, uint8_t *rsp, uint8_t *rsp_len)
{
    static const char fn[] = "get_battery_info"; /* ROM 0x782a9c */
    static const char join[] = "join in get_battery_info"; /* ROM 0x770484 */
    static const char join_c[] = "[pt_protocol_procsr]join in get_battery_info"; /* ROM 0x7371e4 */
    const pt_charger_telemetry_view_t *bat = &g2_charger_telemetry;

    PT_LOG0(3, fn, 0x42cu, join, join_c);
    if (PT_BAD_ARGS(payload, length, rsp, rsp_len, 4u)) {
        PT_PARA_NULL(fn, 0x42fu);
        return 0xffffffffu; /* -1 */
    }
    uint8_t idx = 0;
    PT_HEADER(rsp, idx, 0x11u, 7u);
    rsp[idx++] = (uint8_t)bat->soc;
    rsp[idx++] = (uint8_t)(bat->voltage_mv / 10 + 0x38);
    rsp[idx++] = bat->avg_current_ma < 1 ? 1u : 0u;
    rsp[idx++] = (uint8_t)iar_abs_509694(bat->avg_current_ma);
    rsp[idx++] = bat->temperature > 0 ? 1u : 0u;
    uint16_t temp = (uint16_t)iar_abs_509694(bat->temperature);
    rsp[idx++] = (uint8_t)(temp >> 8);
    rsp[idx++] = (uint8_t)temp;
    *rsp_len = idx;
    return 0;
}

/* Command 0x38 (TSV label pt_cmd_2D_handler) set_canvas_pos_info: payload[6] = x, payload[8] = y, payload[4] != 0
 * also persists them to nvSysDt. Reply 0x38. */
uint32_t pt_cmd_2D_handler(const uint8_t *payload, uint8_t length, uint8_t *rsp, uint8_t *rsp_len)
{
    static const char fn[] = "set_canvas_pos_info"; /* ROM 0x782ab0 */
    static const char join[] = "join in set_canvas_pos_info"; /* ROM 0x7704a0 */
    static const char join_c[] = "[pt_protocol_procsr]join in set_canvas_pos_info"; /* ROM 0x737214 */
    static const char ok[] = "set canvas pos info success, x = %d, y = %d"; /* ROM 0x741fc8 */
    static const char ok_c[] = "[pt_protocol_procsr]set canvas pos info success, x = %d, y = %d"; /* ROM 0x70e224 */
    static const char fail[] = "set canvas pos info failed, product mode is not test mode"; /* ROM 0x717e60 */
    static const char fail_c[] = "[pt_protocol_procsr]set canvas pos info failed, product mode is not test mode"; /* ROM 0x6ef4a8 */

    PT_LOG0(3, fn, 0x44au, join, join_c);
    if (PT_BAD_ARGS(payload, length, rsp, rsp_len, 4u)) {
        PT_PARA_NULL(fn, 0x44du);
        return 0xffffffffu; /* -1 */
    }
    uint8_t idx = 0;
    PT_HEADER(rsp, idx, 0x38u, 1u);
    if (productModeGet() == PT_PRODUCT_TEST_MODE) {
        uint8_t x = payload[6];
        uint8_t y = payload[8];
        PT_LOGN(3, 2, fn, 0x45cu, ok, ok_c, x, y);
        SYS_DT->canvas_x = x;
        SYS_DT->canvas_y = y;
        rsp[idx++] = PT_STATUS_OK;
        if (payload[4] != 0u) {
            (void)SVC_NvdbWriteSysData(G2_NVDB_SYSDT_CANVAS_X, &x);
            (void)SVC_NvdbWriteSysData(G2_NVDB_SYSDT_CANVAS_Y, &y);
        }
        const uint8_t *started = display_startup_state_get_44347a();
        if (started == NULL || *started != 1u) {
            (void)audio_uart_slave_display_start(PT_DISPLAY_APP, NULL, 0u);
            PT_PANEL_POWER_ON();
        }
        (void)uled_set_display_offset(x, y);
    } else {
        PT_LOG0(1, fn, 0x47bu, fail, fail_c);
        rsp[idx++] = PT_STATUS_NOT_TEST_MODE;
    }
    *rsp_len = idx;
    return 0;
}

/* Command 0x39 (TSV label pt_cmd_45_handler) get_canvas_pos_info: reply 0x39 with x and y as 16-bit big-endian. */
uint32_t pt_cmd_45_handler(const uint8_t *payload, uint8_t length, uint8_t *rsp, uint8_t *rsp_len)
{
    static const char fn[] = "get_canvas_pos_info"; /* ROM 0x782ac4 */
    static const char join[] = "join in get_canvas_pos_info"; /* ROM 0x7704bc */
    static const char join_c[] = "[pt_protocol_procsr]join in get_canvas_pos_info"; /* ROM 0x737244 */

    PT_LOG0(3, fn, 0x485u, join, join_c);
    if (PT_BAD_ARGS(payload, length, rsp, rsp_len, 4u)) {
        PT_PARA_NULL(fn, 0x488u);
        return 0xffffffffu; /* -1 */
    }
    uint8_t idx = 0;
    PT_HEADER(rsp, idx, 0x39u, 4u);
    rsp[idx++] = 0u;
    rsp[idx++] = SYS_DT->canvas_x;
    rsp[idx++] = 0u;
    rsp[idx++] = SYS_DT->canvas_y;
    *rsp_len = idx;
    return 0;
}

/* Command 0x24 (TSV label pt_cmd_1C_handler) get_version: reply 0x24 with the four software version numbers
 * (prefixed with '9' in product-test mode, i.e. 92.2.6.10) and the hardware
 * version byte. */
uint32_t pt_cmd_1C_handler(const uint8_t *payload, uint8_t length, uint8_t *rsp, uint8_t *rsp_len)
{
    static const char fn[] = "get_version"; /* ROM 0x78bd08 */
    static const char join[] = "join in get_version"; /* ROM 0x782ad8 */
    static const char join_c[] = "[pt_protocol_procsr]join in get_version"; /* ROM 0x74d32c */
    static const char soft[] = "soft version is:%s"; /* ROM 0x782aec */
    static const char soft_c[] = "[pt_protocol_procsr]soft version is:%s"; /* ROM 0x74d354 */
    static const char hw[] = "hw_version version is:%d"; /* ROM 0x7704d8 */
    static const char hw_c[] = "[pt_protocol_procsr]hw_version version is:%d"; /* ROM 0x737274 */
    static const char test_fmt[] = "9%s"; /* ROM 0x570768 (literal pool) */
    static const char ver_fmt[] = "%d.%d.%d.%d"; /* ROM 0x78bd14 */
    static const char version_init[12] = "2.2.6.10"; /* ROM 0x78bd44 */
    int32_t v0, v1, v2, v3;
    char text[20];
    char version[12];

    PT_LOG0(3, fn, 0x49du, join, join_c);
    if (PT_BAD_ARGS(payload, length, rsp, rsp_len, 4u)) {
        PT_PARA_NULL(fn, 0x4a0u);
        return 0xffffffffu; /* -1 */
    }
    uint8_t idx = 0;
    PT_HEADER(rsp, idx, 0x24u, 5u);
    (void)audio_queue_copy_bytes(version, version_init, sizeof version);
    if (productModeGet() == PT_PRODUCT_TEST_MODE)
        (void)audio_ble_format_to_buffer(text, test_fmt, version);
    else
        (void)g2_strcpy_48d540(text, version);
    PT_LOGN(3, 1, fn, 0x4c4u, soft, soft_c, text);
    (void)audio_ble_parse_version(text, ver_fmt, &v0, &v1, &v2, &v3);
    rsp[idx++] = (uint8_t)v0;
    rsp[idx++] = (uint8_t)v1;
    rsp[idx++] = (uint8_t)v2;
    rsp[idx++] = (uint8_t)v3;
    uint8_t hw_version = *audio_ble_hci_radio_mode_state_50938e(1u);
    rsp[idx++] = hw_version;
    PT_LOGN(3, 1, fn, 0x4cfu, hw, hw_c, hw_version);
    *rsp_len = idx;
    return 0;
}

/* Command 0x17 (TSV label pt_cmd_13_handler) get_imu_info: reply 0x17 with the latest 36-byte IMU sample. */
uint32_t pt_cmd_13_handler(const uint8_t *payload, uint8_t length, uint8_t *rsp, uint8_t *rsp_len)
{
    static const char fn[] = "get_imu_info"; /* ROM 0x788440 */
    static const char join[] = "join in get_imu_info"; /* ROM 0x77ace4 */
    static const char join_c[] = "[pt_protocol_procsr]join in get_imu_info"; /* ROM 0x741ff4 */
    static const char no_data[] = "getImuData() returned NULL pointer!"; /* ROM 0x758a84 */
    static const char no_data_c[] = "[pt_protocol_procsr]getImuData() returned NULL pointer!"; /* ROM 0x721b38 */
    static const char before[] = "Before IMU data copy: cmdIdx = %d"; /* ROM 0x758aa8 */
    static const char before_c[] = "[pt_protocol_procsr]Before IMU data copy: cmdIdx = %d"; /* ROM 0x721b70 */
    static const char after[] = "After IMU data copy: cmdIdx = %d"; /* ROM 0x758acc */
    static const char after_c[] = "[pt_protocol_procsr]After IMU data copy: cmdIdx = %d"; /* ROM 0x721ba8 */
    static const char final[] = "Final send_len = %d (should be 40)"; /* ROM 0x758af0 */
    static const char final_c[] = "[pt_protocol_procsr]Final send_len = %d (should be 40)"; /* ROM 0x721be0 */

    PT_LOG0(3, fn, 0x4d7u, join, join_c);
    if (PT_BAD_ARGS(payload, length, rsp, rsp_len, 4u)) {
        PT_PARA_NULL(fn, 0x4dau);
        return 0xffffffffu; /* -1 */
    }
    uint8_t idx = 0;
    PT_HEADER(rsp, idx, 0x17u, 0x24u);
    const uint8_t *sample = semantic_get_latest_complete_sample();
    if (sample == NULL) {
        PT_LOG0(1, fn, 0x4eau, no_data, no_data_c);
        *rsp_len = 4u;
        return 0xffffffffu; /* -1 */
    }
    PT_LOGN(4, 1, fn, 0x4efu, before, before_c, idx);
    for (int i = 0; i < 0x24; i++)
        rsp[idx++] = sample[i];
    PT_LOGN(4, 1, fn, 0x4f6u, after, after_c, idx);
    *rsp_len = idx;
    PT_LOGN(4, 1, fn, 0x4f9u, final, final_c, *rsp_len);
    return 0;
}

/* Command 0x18 (TSV label pt_cmd_17_handler) get_press_key_val: reply 0x18 with four touch-channel diff counts
 * (16-bit little-endian); a fifth is read and only logged. */
uint32_t pt_cmd_17_handler(const uint8_t *payload, uint8_t length, uint8_t *rsp, uint8_t *rsp_len)
{
    static const char fn[] = "get_press_key_val"; /* ROM 0x782b00 */
    static const char join[] = "join in get_press_key_val"; /* ROM 0x7704f4 */
    static const char join_c[] = "[pt_protocol_procsr]join in get_press_key_val"; /* ROM 0x7372a4 */
    static const char diff[] = "diff val is:%u,%u,%u,%u,%u"; /* ROM 0x770510 */
    static const char diff_c[] = "[pt_protocol_procsr]diff val is:%u,%u,%u,%u,%u"; /* ROM 0x7372d4 */
    uint16_t val[5];

    PT_LOG0(3, fn, 0x501u, join, join_c);
    if (PT_BAD_ARGS(payload, length, rsp, rsp_len, 4u)) {
        PT_PARA_NULL(fn, 0x504u);
        return 0xffffffffu; /* -1 */
    }
    uint8_t idx = 0;
    PT_HEADER(rsp, idx, 0x18u, 8u);
    (void)aeabi_memset_43c0e4(val, sizeof val, 0);
    (void)DRV_TouchReadSensorDiff_55b6a8(val);
    for (int i = 0; i < 4; i++) {
        rsp[idx] = (uint8_t)val[i];
        rsp[(uint8_t)(idx + 1u)] = (uint8_t)(val[i] >> 8);
        idx = (uint8_t)(idx + 2u);
    }
    PT_LOGN(3, 5, fn, 0x517u, diff, diff_c, val[0], val[1], val[2], val[3], val[4]);
    *rsp_len = idx;
    return 0;
}

/* Command 0x3A (TSV label pt_cmd_2E_handler) set_mic_nocompress: payload[5] != 0 sets the production LC3 flag. */
uint32_t pt_cmd_2E_handler(const uint8_t *payload, uint8_t length, uint8_t *rsp, uint8_t *rsp_len)
{
    static const char fn[] = "set_mic_nocompress"; /* ROM 0x782b14 */
    static const char join[] = "join in set_mic_nocompress"; /* ROM 0x77052c */
    static const char join_c[] = "[pt_protocol_procsr]join in set_mic_nocompress"; /* ROM 0x737304 */
    static const char flag[] = "set mic nocompress flag = %d"; /* ROM 0x764350 */
    static const char flag_c[] = "[pt_protocol_procsr]set mic nocompress flag = %d"; /* ROM 0x72c478 */

    PT_LOG0(3, fn, 0x520u, join, join_c);
    if (PT_BAD_ARGS(payload, length, rsp, rsp_len, 6u)) {
        PT_PARA_NULL(fn, 0x523u);
        return 0xffffffffu; /* -1 */
    }
    uint8_t idx = 0;
    PT_HEADER(rsp, idx, 0x3au, 1u);
    if (productModeGet() == PT_PRODUCT_TEST_MODE) {
        if (payload[5] == 0u)
            g2_production_lc3_enable = 0u;
        else
            g2_production_lc3_enable = 1u;
        PT_LOGN(3, 1, fn, 0x532u, flag, flag_c, g2_production_lc3_enable);
        rsp[idx++] = PT_STATUS_OK;
    } else {
        PT_DENIED(fn, 0x537u);
        rsp[idx++] = PT_STATUS_NOT_TEST_MODE;
    }
    rsp[idx++] = payload[4];
    *rsp_len = idx;
    return 0;
}

/* Command 0x25 (TSV label pt_cmd_20_handler) panel_resume: start the display app and power the panel. */
uint32_t pt_cmd_20_handler(const uint8_t *payload, uint8_t length, uint8_t *rsp, uint8_t *rsp_len)
{
    static const char fn[] = "panel_resume"; /* ROM 0x788460 */
    static const char join[] = "join in panel_resume"; /* ROM 0x77ad44 */
    static const char join_c[] = "[pt_protocol_procsr]join in panel_resume"; /* ROM 0x7420fc */

    PT_LOG0(3, fn, 0x6c7u, join, join_c);
    if (PT_BAD_ARGS(payload, length, rsp, rsp_len, 4u)) {
        PT_PARA_NULL(fn, 0x6cau);
        return 0xffffffffu; /* -1 */
    }
    uint8_t idx = 0;
    PT_HEADER(rsp, idx, 0x25u, 1u);
    if (productModeGet() == PT_PRODUCT_TEST_MODE) {
        (void)audio_uart_slave_display_start(PT_DISPLAY_APP, NULL, 0u);
        rsp[idx++] = PT_STATUS_OK;
        PT_PANEL_POWER_ON();
    } else {
        PT_DENIED(fn, 0x6e3u);
        rsp[idx++] = PT_STATUS_NOT_TEST_MODE;
    }
    *rsp_len = idx;
    return 0;
}

/* Command 0x26 (TSV label pt_cmd_22_handler) panel_suspend: stop the display app if the display is running. */
uint32_t pt_cmd_22_handler(const uint8_t *payload, uint8_t length, uint8_t *rsp, uint8_t *rsp_len)
{
    static const char fn[] = "panel_suspend"; /* ROM 0x788470 */
    static const char join[] = "join in panel_suspend"; /* ROM 0x77ad5c */
    static const char join_c[] = "[pt_protocol_procsr]join in panel_suspend"; /* ROM 0x742128 */
    static const char active[] = "Display is active, clearing screen before restart"; /* ROM 0x72c5e4 */
    static const char active_c[] = "[pt_protocol_procsr]Display is active, clearing screen before restart"; /* ROM 0x6fc4ac */

    PT_LOG0(3, fn, 0x6eeu, join, join_c);
    if (PT_BAD_ARGS(payload, length, rsp, rsp_len, 4u)) {
        PT_PARA_NULL(fn, 0x6f1u);
        return 0xffffffffu; /* -1 */
    }
    uint8_t idx = 0;
    PT_HEADER(rsp, idx, 0x26u, 1u);
    if (productModeGet() == PT_PRODUCT_TEST_MODE) {
        const uint8_t *started = display_startup_state_get_44347a();
        if (started != NULL && *started == 1u) {
            PT_LOG0(3, fn, 0x701u, active, active_c);
            (void)audio_uart_slave_display_stop(PT_DISPLAY_APP, NULL, 0u);
        }
        rsp[idx++] = PT_STATUS_OK;
    } else {
        PT_DENIED(fn, 0x708u);
        rsp[idx++] = PT_STATUS_NOT_TEST_MODE;
    }
    *rsp_len = idx;
    return 0;
}

/* Command 0x30 (TSV label pt_cmd_26_handler) power_on_lux: acknowledge only (the rail is powered on demand). */
uint32_t pt_cmd_26_handler(const uint8_t *payload, uint8_t length, uint8_t *rsp, uint8_t *rsp_len)
{
    static const char fn[] = "power_on_lux"; /* ROM 0x7884a0 */
    static const char join[] = "join in power_on_lux"; /* ROM 0x77ad8c */
    static const char join_c[] = "[pt_protocol_procsr]join in power_on_lux"; /* ROM 0x742180 */

    PT_LOG0(3, fn, 0x73eu, join, join_c);
    if (PT_BAD_ARGS(payload, length, rsp, rsp_len, 4u)) {
        PT_PARA_NULL(fn, 0x741u);
        return 0xffffffffu; /* -1 */
    }
    uint8_t idx = 0;
    PT_HEADER(rsp, idx, 0x30u, 1u);
    if (productModeGet() == PT_PRODUCT_TEST_MODE) {
        rsp[idx++] = PT_STATUS_OK;
    } else {
        PT_DENIED(fn, 0x754u);
        rsp[idx++] = PT_STATUS_NOT_TEST_MODE;
    }
    *rsp_len = idx;
    return 0;
}

/* Command 0x31 (TSV label pt_cmd_29_handler) power_off_lux: switch the product-test sensor rail off. */
uint32_t pt_cmd_29_handler(const uint8_t *payload, uint8_t length, uint8_t *rsp, uint8_t *rsp_len)
{
    static const char fn[] = "power_off_lux"; /* ROM 0x7884b0 */
    static const char join[] = "join in power_off_lux"; /* ROM 0x77ada4 */
    static const char join_c[] = "[pt_protocol_procsr]join in power_off_lux"; /* ROM 0x7421ac */

    PT_LOG0(3, fn, 0x75eu, join, join_c);
    if (PT_BAD_ARGS(payload, length, rsp, rsp_len, 4u)) {
        PT_PARA_NULL(fn, 0x761u);
        return 0xffffffffu; /* -1 */
    }
    uint8_t idx = 0;
    PT_HEADER(rsp, idx, 0x31u, 1u);
    if (productModeGet() == PT_PRODUCT_TEST_MODE) {
        rsp[idx++] = PT_STATUS_OK;
        pt_sensor_rail_power_off_58f950();
    } else {
        PT_DENIED(fn, 0x773u);
        rsp[idx++] = PT_STATUS_NOT_TEST_MODE;
    }
    *rsp_len = idx;
    return 0;
}

/* Command 0x42 (TSV label pt_cmd_30_handler) get_wear_status: reply 0x42 with the wear-detect state and the
 * fifth touch diff channel (16-bit little-endian). */
uint32_t pt_cmd_30_handler(const uint8_t *payload, uint8_t length, uint8_t *rsp, uint8_t *rsp_len)
{
    static const char fn[] = "get_wear_status"; /* ROM 0x7884c0 */
    static const char join[] = "join in get_wear_status"; /* ROM 0x77adbc */
    static const char join_c[] = "[pt_protocol_procsr]join in get_wear_status"; /* ROM 0x7421d8 */
    static const char wear[] = "wear status: %d"; /* ROM 0x7884d0 */
    static const char wear_c[] = "[pt_protocol_procsr]wear status: %d"; /* ROM 0x758b80 */
    static const char key[] = "key data: %u, %u, %u, %u, %u"; /* ROM 0x7643b0 */
    static const char key_c[] = "[pt_protocol_procsr]key data: %u, %u, %u, %u, %u"; /* ROM 0x72c618 */
    uint16_t val[5];

    PT_LOG0(3, fn, 0x77du, join, join_c);
    if (PT_BAD_ARGS(payload, length, rsp, rsp_len, 4u)) {
        PT_PARA_NULL(fn, 0x780u);
        return 0xffffffffu; /* -1 */
    }
    uint8_t idx = 0;
    PT_HEADER(rsp, idx, 0x42u, 3u);
    rsp[idx++] = wear_detect_sensor_state_get_502dae();
    PT_LOGN(3, 1, fn, 0x78cu, wear, wear_c, wear_detect_sensor_state_get_502dae());
    (void)aeabi_memset_43c0e4(val, sizeof val, 0);
    (void)DRV_TouchReadSensorDiff_55b6a8(val);
    PT_LOGN(3, 5, fn, 0x790u, key, key_c, val[0], val[1], val[2], val[3], val[4]);
    rsp[idx++] = (uint8_t)val[4];
    rsp[idx++] = (uint8_t)(val[4] >> 8);
    *rsp_len = idx;
    return 0;
}

/* Command 0x29 (TSV label pt_cmd_24_handler) set_board_sn_info: payload[4..] is the board SN string; it is written
 * to nvSysDt and read back; data byte 1 means the 21-byte compare failed. */
uint32_t pt_cmd_24_handler(const uint8_t *payload, uint8_t length, uint8_t *rsp, uint8_t *rsp_len)
{
    static const char fn[] = "set_board_sn_info"; /* ROM 0x782b8c */
    static const char text[] = "The string is: %s\n"; /* ROM 0x782ba0 */
    static const char text_c[] = "[pt_protocol_procsr]The string is: %s\n"; /* ROM 0x74d46c */

    if (PT_BAD_ARGS(payload, length, rsp, rsp_len, 5u)) {
        PT_PARA_NULL(fn, 0x79eu);
        return 0xffffffffu; /* -1 */
    }
    const char *bsn = (const char *)(payload + 4);
    uint8_t idx = 0;
    PT_HEADER(rsp, idx, 0x29u, 1u);
    if (productModeGet() == PT_PRODUCT_TEST_MODE) {
        PT_LOGN(3, 1, fn, 0x7adu, text, text_c, bsn);
        (void)SVC_NvdbWriteSysData(G2_NVDB_SYSDT_BSN, bsn);
        const uint8_t *stored = SVC_NvdbReadSysData(G2_NVDB_SYSDT_BSN);
        if (g2_lfs_memcmp(bsn, stored, 0x15u) == 0)
            rsp[idx++] = PT_STATUS_OK;
        else
            rsp[idx++] = 1u;
    } else {
        PT_DENIED(fn, 0x7bbu);
        rsp[idx++] = PT_STATUS_NOT_TEST_MODE;
    }
    *rsp_len = idx;
    return 0;
}

/* Command 0x2A (TSV label pt_cmd_25_handler) get_board_sn_info: reply 0x2a with up to 21 board SN characters. */
uint32_t pt_cmd_25_handler(const uint8_t *payload, uint8_t length, uint8_t *rsp, uint8_t *rsp_len)
{
    static const char fn[] = "get_board_sn_info"; /* ROM 0x782bb4 */

    if (PT_BAD_ARGS(payload, length, rsp, rsp_len, 4u)) {
        PT_PARA_NULL(fn, 0x7c8u);
        return 0xffffffffu; /* -1 */
    }
    const char *bsn = (const char *)display_driver_brightness_ratio_cell_4af73a(G2_NVDB_SYSDT_BSN);
    uint8_t idx = 0;
    rsp[idx++] = 0x2au;
    rsp[idx++] = 1u;
    rsp[idx++] = 3u;
    uint8_t n = g2_log_module_length(bsn) < 0x16u ? (uint8_t)g2_log_module_length(bsn) : 0x15u;
    rsp[idx] = n;
    (void)audio_queue_copy_bytes(rsp + 4, bsn, n);
    *rsp_len = (uint8_t)(n + 4u);
    return 0;
}

/* Command 0x05 (TSV label pt_cmd_05_handler) get_mac_info: reply 0x05 with the six nvMAC bytes. Entry 3 of the
 * NVDB record table (RAM 0x20003838) points at nvMAC; byte 0 is its version. */
uint32_t pt_cmd_05_handler(const uint8_t *payload, uint8_t length, uint8_t *rsp, uint8_t *rsp_len)
{
    static const char fn[] = "get_mac_info"; /* ROM 0x7884e0 */
    static const char join[] = "join in get_mac_info"; /* ROM 0x77add4 */
    static const char join_c[] = "[pt_protocol_procsr]join in get_mac_info"; /* ROM 0x742204 */

    PT_LOG0(3, fn, 0x7deu, join, join_c);
    if (PT_BAD_ARGS(payload, length, rsp, rsp_len, 4u)) {
        PT_PARA_NULL(fn, 0x7e1u);
        return 0xffffffffu; /* -1 */
    }
    uint8_t idx = 0;
    PT_HEADER(rsp, idx, 0x05u, 6u);
    const uint8_t *mac_record = *(const uint8_t *const *)(const void *)&audio_ble_adv_config_state[0xc];
    (void)audio_queue_copy_bytes(rsp + idx, mac_record + 1, 6u);
    *rsp_len = (uint8_t)(idx + 6u);
    return 0;
}

/* Command 0x07 (TSV label pt_cmd_06_handler) case_lid_open: reply 0x07 and clear the case lid flag. */
uint32_t pt_cmd_06_handler(const uint8_t *payload, uint8_t length, uint8_t *rsp, uint8_t *rsp_len)
{
    static const char fn[] = "case_lid_open"; /* ROM 0x7884f0 */

    if (PT_BAD_ARGS(payload, length, rsp, rsp_len, 4u)) {
        PT_PARA_NULL(fn, 0x7f6u);
        return 0xffffffffu; /* -1 */
    }
    uint8_t idx = 0;
    PT_HEADER(rsp, idx, 0x07u, 1u);
    rsp[idx++] = PT_STATUS_OK;
    box_detect_set_lid_open_4ac744(0u);
    *rsp_len = idx;
    return 0;
}

/* Command 0x08 (TSV label pt_cmd_07_handler) case_lid_close: reply 0x08 and set the case lid flag. */
uint32_t pt_cmd_07_handler(const uint8_t *payload, uint8_t length, uint8_t *rsp, uint8_t *rsp_len)
{
    static const char fn[] = "case_lid_close"; /* ROM 0x788500 */

    if (PT_BAD_ARGS(payload, length, rsp, rsp_len, 4u)) {
        PT_PARA_NULL(fn, 0x80cu);
        return 0xffffffffu; /* -1 */
    }
    uint8_t idx = 0;
    PT_HEADER(rsp, idx, 0x08u, 1u);
    rsp[idx++] = PT_STATUS_OK;
    box_detect_set_lid_open_4ac744(1u);
    *rsp_len = idx;
    return 0;
}

/* Command 0x0B (TSV label pt_cmd_08_handler) set_restart_mode: acknowledge only (reply 0x0b). */
uint32_t pt_cmd_08_handler(const uint8_t *payload, uint8_t length, uint8_t *rsp, uint8_t *rsp_len)
{
    static const char fn[] = "set_restart_mode"; /* ROM 0x782bc8 */

    if (PT_BAD_ARGS(payload, length, rsp, rsp_len, 4u)) {
        PT_PARA_NULL(fn, 0x822u);
        return 0xffffffffu; /* -1 */
    }
    uint8_t idx = 0;
    PT_HEADER(rsp, idx, 0x0bu, 1u);
    rsp[idx++] = PT_STATUS_OK;
    *rsp_len = idx;
    return 0;
}
