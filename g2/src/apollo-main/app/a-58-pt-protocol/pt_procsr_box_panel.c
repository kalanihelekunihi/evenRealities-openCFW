/* Product-test command handlers (charging-box OTA, box stress test, panel
 * current, buzzer, onboarding, factory reset, IMU calibration, charger enable,
 * font version/CRC, gray / distortion test screens, touch baseline), stock
 * D:\01_workspace\s200_ap510b_iar_git\platform\product_test\pt_protocol_procsr.c.
 * Native 0x575af8..0x577b79; literal pools 0x575e74..0x575eb3,
 * 0x5760ec..0x57612b, 0x5764e0..0x576517, 0x5766f8..0x576713,
 * 0x5767f0..0x5767ff, 0x5768a8..0x5768c7, 0x5771b4..0x5771d3,
 * 0x577344..0x577363, 0x57746c..0x57747b, 0x57756c..0x57757b,
 * 0x577784..0x577793, 0x5778c8..0x5778d3, 0x577b7c..0x577c33.
 *
 * Same handler contract as a-56/pt_procsr_device.c: reached from
 * pt_protocol_dispatch (0x56f4a0) as handler(payload, length, rsp, rsp_len),
 * payload[0] = command, arguments from payload[4]; the bare response is
 * [rsp_cmd][0x01][type][data_len][data...]. The TSV pt_cmd_XX names are off by
 * one from the command byte (pt_cmd_61_handler serves command 0x60, ...);
 * each handler comment gives the real command and the stock __func__ name.
 *
 * Charging-box OTA (commands 0x58..0x5b) streams /firmware/box.bin to the
 * box over the box UART: 0x58 returns the file's 32-byte header, 0x59 opens
 * the file and sets g_is_box_ota_mode, 0x5a returns file chunks at
 * header + offset with an 8-bit sum, 0x5b closes it and reports the box CRC
 * verdict. Multi-byte arguments are little-endian and read byte by byte. */
#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>
#include "g2_bq27427.h"

#define PT_PRODUCT_TEST_MODE 1u
#define PT_STATUS_OK 0u
#define PT_STATUS_FAIL 1u
#define PT_STATUS_INVALID 3u
#define PT_STATUS_NOT_TEST_MODE 5u
#define PT_TYPE_BOX 2u            /* response byte 2 for box-UART commands */
#define PT_BOX_HEADER_LEN 0x20u   /* /firmware/box.bin header */
#define PT_BOX_CHUNK_MAX 240u     /* 0x5a read_len limit */
#define PT_BOX_OTA_MIN_SOC 50     /* % */
#define PT_STRESS_FRAME_MIN 250u
#define PT_STRESS_PATTERN_LEN 246u
#define PT_NV_PANEL_CURRENT 0x2eu /* nvSysDt byte, NVDB sys-data index 5 */
#define PT_NV_PANEL_CURRENT_ID 5u
#define PT_GRAY_SCREEN_APP 0x10fu
#define PT_DISTORTION_SCREEN_APP 0x110u
#define PT_IMU_CAL_LEN 0x24u      /* 3x3 float matrix */

/* /firmware/box.bin header (first 32 bytes of the file). */
typedef struct {
    uint8_t magic[4];    /* +0x00 printed with %c */
    uint8_t version[4];  /* +0x04 a.b.c.d */
    uint32_t length;     /* +0x08 */
    uint32_t crc;        /* +0x0c cached for the box OTA */
    uint8_t reserved[16]; /* +0x10 */
} pt_box_header_t;
_Static_assert(sizeof(pt_box_header_t) == PT_BOX_HEADER_LEN, "box.bin header is 32 bytes");

extern g2_charger_telemetry_t g2_charger_telemetry;          /* RAM 0x20073b18, soc at +4 */
extern uint8_t display_driver_ratio_cells_20003994[0xac];    /* RAM 0x20003994 nvSysDt */
extern uint8_t g2_imu_calibration_matrix_2000396c[PT_IMU_CAL_LEN]; /* RAM 0x2000396c */
extern volatile uint8_t g2_pt_font_crc_failed;               /* RAM 0x20004552 */
extern void *g2_pt_box_ota_file;                             /* RAM 0x200748e4 g_box_ota_file */
extern volatile uint32_t g2_pt_box_ota_crc;                  /* RAM 0x200748e8 */
extern volatile uint32_t g2_dev_box_ota_start_s;             /* RAM 0x200748ec, seconds */
extern volatile uint8_t g2_dev_box_ota_mode;                 /* RAM 0x20075009 g_is_box_ota_mode */

extern uint32_t audio_log_flags(void); /* 0x43d0ce */
extern void audio_log_extended(uint8_t, const char *, const char *, const char *, uint32_t, const char *, ...); /* 0x43d574 */
extern uint32_t compress_log_output(uint32_t, const char *, const char *, ...); /* 0x43ce9e */
extern void *audio_queue_copy_bytes(void *dst, const void *src, uint32_t len); /* memcpy 0x439be4 */
extern void *file_open(const char *path, const char *mode);                   /* 0x474550 */
extern int32_t file_close(void *file);                                        /* 0x4745f4 */
extern uint32_t file_read(void *buffer, uint32_t size, uint32_t count, void *file); /* 0x474634 */
extern int32_t file_seek(void *file, int32_t offset, int32_t origin);         /* 0x474814 */
extern int32_t file_tell(void *file);                                         /* 0x474870 */
extern uint32_t xTaskGetTickCount(void);                                      /* 0x454efe */
extern uint8_t productModeGet(void);                                          /* 0x4abe60 */
extern int32_t SVC_NvdbWriteSysData(uint8_t data_index, const void *value);   /* 0x4af11c */
extern void DRV_BuzzerStart(uint32_t frequency, uint8_t duty);                /* 0x502c88 */
extern uint32_t nvdbBuzzerFrequencyGet(void);                                 /* 0x58fa60 */
extern uint8_t nvdbBuzzerDutyGet(void);                                       /* 0x58fa66 */
extern void nvdbBuzzerUpdate(uint32_t frequency, uint8_t duty);               /* 0x58fa6c */
/* g2_kvdb.h declares this void; stock returns the persist status in r0 and
 * this caller tests it. */
extern int32_t kvdbOnboardingConfigUpdateAndPersist(uint8_t index, const uint8_t *value); /* 0x4a7820 */
extern void npmx_charger_disable_5128f8(void);
extern void npmx_charger_enable_51299c(void);
extern uint8_t *font_manager_xip_font_name_46d584(void);
extern uint8_t *display_startup_state_get_44347a(void);
extern int32_t audio_uart_slave_display_start(uint32_t, const void *, uint32_t); /* 0x4441ec */
extern int32_t audio_uart_slave_display_stop(uint32_t, const void *, uint32_t);  /* 0x4443cc */
extern uint32_t display_driver_case4_apply(uint32_t, uint32_t, uint32_t);        /* 0x4ca1ee uled_mspi_setBrightness */
extern uint32_t display_driver_set_brightness_46c984(uint32_t value);
extern uint32_t display_driver_set_offsets_46c9dc(uint32_t horizontal, uint32_t vertical);
extern uint32_t display_driver_set_profile_46c9aa(uint32_t value);
extern void audio_uart_case_in_case_side_effect_5130a6(void);                   /* 0x5130a6 input_msg_send_id3 */
extern int32_t pt_handler_result(uint8_t rsp_cmd, uint8_t status, uint8_t type,
                                 uint8_t *rsp, uint8_t *rsp_len);               /* 0x575428 */

static const char module_tag[] = "pt_protocol_procsr"; /* ROM 0x7829fc */
static const char source_file[] = "D:\\01_workspace\\s200_ap510b_iar_git\\platform\\product_test\\pt_protocol_procsr.c"; /* ROM 0x6ef458 */
static const char para_null[] = "%s para is NULL\n"; /* ROM 0x782a74 */
static const char para_null_c[] = "[pt_protocol_procsr]%s para is NULL\n"; /* ROM 0x74d304 */
static const char denied[] = "permission denied current mode is not product test mode"; /* ROM 0x721c18 */
static const char denied_c[] = "[pt_protocol_procsr]permission denied current mode is not product test mode"; /* ROM 0x6f586c */
static const char box_path[] = "/firmware/box.bin"; /* ROM 0x782bf0 */
static const char read_mode[] = "r"; /* inline literal-pool words 0x575e78, 0x5760f8 */
static const char not_exist[] = "pt_box_ota_begin: firmware/box.bin file not exist"; /* ROM 0x72c958 */
static const char not_exist_c[] = "[pt_protocol_procsr]pt_box_ota_begin: firmware/box.bin file not exist"; /* ROM 0x6fc614 */
static const char display_active[] = "Display is active, clearing screen before restart"; /* ROM 0x72c5e4 */
static const char display_active_c[] = "[pt_protocol_procsr]Display is active, clearing screen before restart"; /* ROM 0x6fc4ac */

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
#define PT_HEADER(rsp, idx, rsp_cmd, type, data_len) do { \
        (rsp)[(idx)++] = (rsp_cmd); \
        (rsp)[(idx)++] = 1u; \
        (rsp)[(idx)++] = (type); \
        (rsp)[(idx)++] = (data_len); \
    } while (0)

static uint32_t pt_le32(const uint8_t *p)
{
    return (uint32_t)p[0] | ((uint32_t)p[1] << 8) | ((uint32_t)p[2] << 16) | ((uint32_t)p[3] << 24);
}

/* cmd 0x58 pt_box_ota_firmware_check: payload[4..7] = box firmware version.
 * Reply 0x58 type 2 with the 32-byte box.bin header; caches its CRC. */
int32_t pt_cmd_58_handler(const uint8_t *payload, uint8_t length, uint8_t *rsp, uint8_t *rsp_len)
{
    static const char fn[] = "pt_box_ota_firmware_check"; /* ROM 0x770708 */
    static const char join[] = "join in pt_box_ota_firmware_check"; /* ROM 0x758c34 */
    static const char join_c[] = "[pt_protocol_procsr]join in pt_box_ota_firmware_check"; /* ROM 0x721da0 */
    static const char bad[] = "pt_box_ota_firmware_check: recv_value == NULL || send_value == NULL || send_len == NULL || recv_len < 8"; /* ROM 0x6d97d4 */
    static const char bad_c[] = "[pt_protocol_procsr]pt_box_ota_firmware_check: recv_value == NULL || send_value == NULL || send_len == NULL || recv_len < 8"; /* ROM 0x69be14 */
    static const char cur[] = "box current firmware version: %d.%d.%d.%d"; /* ROM 0x7423bc */
    static const char cur_c[] = "[pt_protocol_procsr]box current firmware version: %d.%d.%d.%d"; /* ROM 0x70e424 */
    static const char magic[] = "box file firmware magic: %c%c%c%c"; /* ROM 0x758c58 */
    static const char magic_c[] = "[pt_protocol_procsr]box file firmware magic: %c%c%c%c"; /* ROM 0x721dd8 */
    static const char ver[] = "box file firmware version: %d.%d.%d.%d"; /* ROM 0x74d50c */
    static const char ver_c[] = "[pt_protocol_procsr]box file firmware version: %d.%d.%d.%d"; /* ROM 0x717f14 */
    static const char len[] = "box file firmware length: %d"; /* ROM 0x7645b0 */
    static const char len_c[] = "[pt_protocol_procsr]box file firmware length: %d"; /* ROM 0x72c98c */
    static const char crc[] = "box file firmware crc: %x"; /* ROM 0x770724 */
    static const char crc_c[] = "[pt_protocol_procsr]box file firmware crc: %x"; /* ROM 0x737724 */
    pt_box_header_t header;

    PT_LOG0(3, fn, 0xc79u, join, join_c);
    if (payload == NULL || rsp == NULL || rsp_len == NULL || length < 8u) {
        PT_LOG0(1, fn, 0xc7bu, bad, bad_c);
        return -1;
    }
    PT_LOGN(2, 4, fn, 0xc7eu, cur, cur_c, payload[4], payload[5], payload[6], payload[7]);
    void *fp = file_open(box_path, read_mode);
    if (fp == NULL) {
        PT_LOG0(1, fn, 0xc84u, not_exist, not_exist_c);
        return pt_handler_result(0x58u, PT_STATUS_FAIL, PT_TYPE_BOX, rsp, rsp_len);
    }
    (void)file_read(&header, 1u, sizeof(header), fp);
    (void)file_close(fp);
    PT_LOGN(2, 4, fn, 0xc8du, magic, magic_c, header.magic[0], header.magic[1], header.magic[2], header.magic[3]);
    PT_LOGN(2, 4, fn, 0xc8eu, ver, ver_c, header.version[0], header.version[1], header.version[2], header.version[3]);
    PT_LOGN(2, 1, fn, 0xc8fu, len, len_c, header.length);
    PT_LOGN(2, 1, fn, 0xc90u, crc, crc_c, header.crc);
    g2_pt_box_ota_crc = header.crc;
    uint8_t idx = 0;
    PT_HEADER(rsp, idx, 0x58u, PT_TYPE_BOX, PT_BOX_HEADER_LEN);
    (void)audio_queue_copy_bytes(&rsp[idx], &header, sizeof(header));
    idx = (uint8_t)(idx + sizeof(header));
    *rsp_len = idx;
    return 0;
}

/* cmd 0x59 pt_box_ota_begin: needs SoC >= 50 %; (re)opens box.bin, enters
 * box OTA mode and records the start time in seconds. */
int32_t pt_cmd_59_handler(const uint8_t *payload, uint8_t length, uint8_t *rsp, uint8_t *rsp_len)
{
    static const char fn[] = "pt_box_ota_begin"; /* ROM 0x782ce0 */
    static const char join[] = "join in pt_box_ota_begin"; /* ROM 0x770740 */
    static const char join_c[] = "[pt_protocol_procsr]join in pt_box_ota_begin"; /* ROM 0x737754 */
    static const char bad[] = "pt_box_ota_begin: recv_value == NULL || send_value == NULL || send_len == NULL || recv_len < 4"; /* ROM 0x6de494 */
    static const char bad_c[] = "[pt_protocol_procsr]pt_box_ota_begin: recv_value == NULL || send_value == NULL || send_len == NULL || recv_len < 4"; /* ROM 0x6a1d94 */
    static const char low[] = "pt_box_ota_begin: battery level is less than 50%"; /* ROM 0x72c9c0 */
    static const char low_c[] = "[pt_protocol_procsr]pt_box_ota_begin: battery level is less than 50%"; /* ROM 0x6fc65c */
    static const char reopen[] = "pt_box_ota_begin: previous file was not closed, closed it now"; /* ROM 0x70e464 */
    static const char reopen_c[] = "[pt_protocol_procsr]pt_box_ota_begin: previous file was not closed, closed it now"; /* ROM 0x6e97a8 */
    static const char start[] = "pt_box_ota_begin: set g_is_box_ota_mode = true, start_time = %d"; /* ROM 0x70e4a4 */
    static const char start_c[] = "[pt_protocol_procsr]pt_box_ota_begin: set g_is_box_ota_mode = true, start_time = %d"; /* ROM 0x6e97fc */

    PT_LOG0(3, fn, 0xca4u, join, join_c);
    if (payload == NULL || rsp == NULL || rsp_len == NULL || length < 4u) {
        PT_LOG0(1, fn, 0xca6u, bad, bad_c);
        return -1;
    }
    if (g2_charger_telemetry.soc < PT_BOX_OTA_MIN_SOC) {
        PT_LOG0(1, fn, 0xcacu, low, low_c);
        return pt_handler_result(0x59u, PT_STATUS_FAIL, PT_TYPE_BOX, rsp, rsp_len);
    }
    if (g2_pt_box_ota_file != NULL) {
        (void)file_close(g2_pt_box_ota_file);
        g2_pt_box_ota_file = NULL;
        PT_LOG0(2, fn, 0xcb4u, reopen, reopen_c);
    }
    void *fp = file_open(box_path, read_mode);
    if (fp == NULL) {
        PT_LOG0(1, fn, 0xcbbu, not_exist, not_exist_c);
        return pt_handler_result(0x59u, PT_STATUS_FAIL, PT_TYPE_BOX, rsp, rsp_len);
    }
    g2_pt_box_ota_file = fp;
    g2_dev_box_ota_mode = 1u;
    g2_dev_box_ota_start_s = xTaskGetTickCount() / 1000u;
    PT_LOGN(3, 1, fn, 0xcc5u, start, start_c, g2_dev_box_ota_start_s);
    return pt_handler_result(0x59u, PT_STATUS_OK, PT_TYPE_BOX, rsp, rsp_len);
}

/* cmd 0x5a pt_box_ota_file_get: payload[4..7] = payload offset (file offset
 * minus the 32-byte header), payload[8] = read_len <= 240. Reply 0x5a type 2,
 * data_len = actual + 1, data, then the 8-bit sum of the data. */
int32_t pt_cmd_5A_handler(const uint8_t *payload, uint8_t length, uint8_t *rsp, uint8_t *rsp_len)
{
    static const char fn[] = "pt_box_ota_file_get"; /* ROM 0x782cf4 */
    static const char join[] = "join in pt_box_ota_file_get"; /* ROM 0x77075c */
    static const char join_c[] = "[pt_protocol_procsr]join in pt_box_ota_file_get"; /* ROM 0x737784 */
    static const char bad[] = "pt_box_ota_file_get: recv_value == NULL || send_value == NULL || send_len == NULL || recv_len < 9"; /* ROM 0x6db808 */
    static const char bad_c[] = "[pt_protocol_procsr]pt_box_ota_file_get: recv_value == NULL || send_value == NULL || send_len == NULL || recv_len < 9"; /* ROM 0x6d68a8 */
    static const char no_file[] = "pt_box_ota_file_get: g_box_ota_file is NULL"; /* ROM 0x7423e8 */
    static const char no_file_c[] = "[pt_protocol_procsr]pt_box_ota_file_get: g_box_ota_file is NULL"; /* ROM 0x70e4e4 */
    static const char req[] = "pt_box_ota_file_get: offset=%d, read_len=%d"; /* ROM 0x742414 */
    static const char req_c[] = "[pt_protocol_procsr]pt_box_ota_file_get: offset=%d, read_len=%d"; /* ROM 0x70e524 */
    static const char too_long[] = "pt_box_ota_file_get: read_len > 240"; /* ROM 0x758c7c */
    static const char too_long_c[] = "[pt_protocol_procsr]pt_box_ota_file_get: read_len > 240"; /* ROM 0x721e10 */
    static const char seek_fail[] = "pt_box_ota_file_get: fseek failed"; /* ROM 0x758ca0 */
    static const char seek_fail_c[] = "[pt_protocol_procsr]pt_box_ota_file_get: fseek failed"; /* ROM 0x721e48 */
    static const char mismatch[] = "pt_box_ota_file_get: file position mismatch, expected=%d, actual=%ld"; /* ROM 0x6fc6a4 */
    static const char mismatch_c[] = "[pt_protocol_procsr]pt_box_ota_file_get: file position mismatch, expected=%d, actual=%ld"; /* ROM 0x6e15a0 */
    static const char positioned[] = "pt_box_ota_file_get: file positioned correctly at offset=%d"; /* ROM 0x717f50 */
    static const char positioned_c[] = "[pt_protocol_procsr]pt_box_ota_file_get: file positioned correctly at offset=%d"; /* ROM 0x6ef548 */
    static const char got[] = "pt_box_ota_file_get: actual_read=%d"; /* ROM 0x758cc4 */
    static const char got_c[] = "[pt_protocol_procsr]pt_box_ota_file_get: actual_read=%d"; /* ROM 0x721e80 */
    uint8_t chunk[PT_BOX_CHUNK_MAX];

    PT_LOG0(3, fn, 0xcccu, join, join_c);
    if (payload == NULL || rsp == NULL || rsp_len == NULL || length < 9u) {
        PT_LOG0(1, fn, 0xcceu, bad, bad_c);
        return -1;
    }
    if (g2_pt_box_ota_file == NULL) {
        PT_LOG0(1, fn, 0xcd4u, no_file, no_file_c);
        return pt_handler_result(0x5au, PT_STATUS_FAIL, PT_TYPE_BOX, rsp, rsp_len);
    }
    uint32_t offset = pt_le32(&payload[4]) + PT_BOX_HEADER_LEN;
    uint8_t read_len = payload[8];
    PT_LOGN(3, 2, fn, 0xcdcu, req, req_c, offset, read_len);
    if (read_len > PT_BOX_CHUNK_MAX) {
        PT_LOG0(1, fn, 0xcdfu, too_long, too_long_c);
        return pt_handler_result(0x5au, PT_STATUS_FAIL, PT_TYPE_BOX, rsp, rsp_len);
    }
    if (file_seek(g2_pt_box_ota_file, (int32_t)offset, 0) != 0) {
        PT_LOG0(1, fn, 0xce5u, seek_fail, seek_fail_c);
        return pt_handler_result(0x5au, PT_STATUS_FAIL, PT_TYPE_BOX, rsp, rsp_len);
    }
    int32_t position = file_tell(g2_pt_box_ota_file);
    if ((uint32_t)position != offset)
        PT_LOGN(2, 2, fn, 0xcecu, mismatch, mismatch_c, offset, position);
    else
        PT_LOGN(4, 1, fn, 0xceeu, positioned, positioned_c, offset);
    uint32_t actual = file_read(chunk, 1u, read_len, g2_pt_box_ota_file);
    PT_LOGN(3, 1, fn, 0xcf5u, got, got_c, actual);

    uint8_t sum = 0;
    uint32_t idx = 0;
    PT_HEADER(rsp, idx, 0x5au, PT_TYPE_BOX, (uint8_t)(actual + 1u));
    if (actual != 0u) {
        (void)audio_queue_copy_bytes(&rsp[(uint8_t)idx], chunk, actual);
        idx += actual;
    }
    for (uint32_t i = 0; i < actual; i++)
        sum = (uint8_t)(sum + chunk[i]);
    rsp[(uint8_t)idx] = sum;
    idx++;
    *rsp_len = (uint8_t)idx;
    return 0;
}

/* cmd 0x5b pt_box_ota_result_check: payload[4] = box CRC verdict (0 = ok),
 * payload[5..8] = new box version. Closes box.bin and leaves box OTA mode. */
int32_t pt_cmd_5B_handler(const uint8_t *payload, uint8_t length, uint8_t *rsp, uint8_t *rsp_len)
{
    static const char fn[] = "pt_box_ota_result_check"; /* ROM 0x77af0c */
    static const char join[] = "join in pt_box_ota_result_check"; /* ROM 0x7645d0 */
    static const char join_c[] = "[pt_protocol_procsr]join in pt_box_ota_result_check"; /* ROM 0x72c9f4 */
    static const char bad[] = "pt_box_ota_result_check: recv_value == NULL || send_value == NULL || send_len == NULL || recv_len < 9"; /* ROM 0x6d983c */
    static const char bad_c[] = "[pt_protocol_procsr]pt_box_ota_result_check: recv_value == NULL || send_value == NULL || send_len == NULL || recv_len < 9"; /* ROM 0x69c214 */
    static const char closed[] = "pt_box_ota_result_check: closed box ota file"; /* ROM 0x7377b4 */
    static const char closed_c[] = "[pt_protocol_procsr]pt_box_ota_result_check: closed box ota file"; /* ROM 0x704efc */
    static const char cleared[] = "pt_box_ota_result_check: set g_is_box_ota_mode = false, clear start_time"; /* ROM 0x6f599c */
    static const char cleared_c[] = "[pt_protocol_procsr]pt_box_ota_result_check: set g_is_box_ota_mode = false, clear start_time"; /* ROM 0x6de4f4 */
    static const char result[] = "pt_box_ota_result_check: crc_result=%d, box_version=%d.%d.%d.%d"; /* ROM 0x70e564 */
    static const char result_c[] = "[pt_protocol_procsr]pt_box_ota_result_check: crc_result=%d, box_version=%d.%d.%d.%d"; /* ROM 0x6e9850 */

    PT_LOG0(3, fn, 0xd13u, join, join_c);
    if (payload == NULL || rsp == NULL || rsp_len == NULL || length < 9u) {
        PT_LOG0(1, fn, 0xd15u, bad, bad_c);
        return -1;
    }
    if (g2_pt_box_ota_file != NULL) {
        (void)file_close(g2_pt_box_ota_file);
        g2_pt_box_ota_file = NULL;
        PT_LOG0(3, fn, 0xd1du, closed, closed_c);
    }
    g2_dev_box_ota_mode = 0u;
    g2_dev_box_ota_start_s = 0u;
    PT_LOG0(3, fn, 0xd23u, cleared, cleared_c);
    uint8_t crc_result = payload[4];
    PT_LOGN(2, 5, fn, 0xd28u, result, result_c, crc_result, payload[5], payload[6], payload[7], payload[8]);
    if (crc_result == 0u)
        return pt_handler_result(0x5bu, PT_STATUS_OK, PT_TYPE_BOX, rsp, rsp_len);
    return pt_handler_result(0x5bu, PT_STATUS_FAIL, PT_TYPE_BOX, rsp, rsp_len);
}

/* cmd 0xf3 pt_box_stree_test (box UART stress frame): payload[4 + i] must be
 * i for i < 246. Reply 0xf3 type 2. */
int32_t pt_cmd_60_handler(const uint8_t *payload, uint8_t length, uint8_t *rsp, uint8_t *rsp_len)
{
    static const char fn[] = "pt_box_stree_test"; /* ROM 0x782d08 */
    static const char short_frame[] = "pt_box_stree_test: recv_len < 250"; /* ROM 0x758ce8 */
    static const char short_frame_c[] = "[pt_protocol_procsr]pt_box_stree_test: recv_len < 250"; /* ROM 0x721eb8 */
    static const char join[] = "join in pt_box_stree_test"; /* ROM 0x770778 */
    static const char join_c[] = "[pt_protocol_procsr]join in pt_box_stree_test"; /* ROM 0x7377e4 */

    if (length < PT_STRESS_FRAME_MIN) {
        PT_LOG0(1, fn, 0xd38u, short_frame, short_frame_c);
        return pt_handler_result(0xf3u, PT_STATUS_FAIL, PT_TYPE_BOX, rsp, rsp_len);
    }
    PT_LOG0(3, fn, 0xd3cu, join, join_c);
    bool match = true;
    for (int32_t i = 0; i < (int32_t)PT_STRESS_PATTERN_LEN; i++) {
        if (payload[4 + i] != (uint32_t)i) {
            match = false;
            break;
        }
    }
    if (match)
        return pt_handler_result(0xf3u, PT_STATUS_OK, PT_TYPE_BOX, rsp, rsp_len);
    return pt_handler_result(0xf3u, PT_STATUS_FAIL, PT_TYPE_BOX, rsp, rsp_len);
}

/* cmd 0x60 set_panel_current: payload[4] -> nvSysDt+0x2e, persisted as NVDB
 * sys-data 5. No argument check and no response is written (stock). */
int32_t pt_cmd_61_handler(const uint8_t *payload, uint8_t length, uint8_t *rsp, uint8_t *rsp_len)
{
    static const char fn[] = "set_panel_current"; /* ROM 0x782d1c */
    static const char join[] = "join in set_panel_current"; /* ROM 0x770794 */
    static const char join_c[] = "[pt_protocol_procsr]join in set_panel_current"; /* ROM 0x737814 */
    static const char value[] = "set_panel_current: panel_current = %d"; /* ROM 0x74d534 */
    static const char value_c[] = "[pt_protocol_procsr]set_panel_current: panel_current = %d"; /* ROM 0x717f8c */
    (void)length;
    (void)rsp;
    (void)rsp_len;

    PT_LOG0(3, fn, 0xd56u, join, join_c);
    uint8_t current = payload[4];
    PT_LOGN(3, 1, fn, 0xd58u, value, value_c, current);
    display_driver_ratio_cells_20003994[PT_NV_PANEL_CURRENT] = current;
    (void)SVC_NvdbWriteSysData(PT_NV_PANEL_CURRENT_ID, &display_driver_ratio_cells_20003994[PT_NV_PANEL_CURRENT]);
    return 0;
}

/* cmd 0x61 set_special_buzzer_status: payload[4..7] = frequency,
 * payload[8] = duty; starts the buzzer in product-test mode only. */
int32_t pt_cmd_62_handler(const uint8_t *payload, uint8_t length, uint8_t *rsp, uint8_t *rsp_len)
{
    static const char fn[] = "set_special_buzzer_status"; /* ROM 0x7707b0 */
    static const char join[] = "join in set_special_buzzer_status"; /* ROM 0x758d0c */
    static const char join_c[] = "[pt_protocol_procsr]join in set_special_buzzer_status"; /* ROM 0x721ef0 */

    PT_LOG0(3, fn, 0xd60u, join, join_c);
    if (PT_BAD_ARGS(payload, length, rsp, rsp_len, 9u)) {
        PT_PARA_NULL(fn, 0xd63u);
        return -1;
    }
    uint8_t idx = 0;
    PT_HEADER(rsp, idx, 0x61u, 3u, 1u);
    if (productModeGet() == PT_PRODUCT_TEST_MODE) {
        DRV_BuzzerStart(pt_le32(&payload[4]), payload[8]);
        rsp[idx++] = PT_STATUS_OK;
    } else {
        PT_DENIED(fn, 0xd77u);
        rsp[idx++] = PT_STATUS_NOT_TEST_MODE;
    }
    *rsp_len = idx;
    return 0;
}

/* cmd 0x62 get_buzzer_base: reply 0x62 with frequency (LE32) and duty. */
int32_t pt_cmd_63_handler(const uint8_t *payload, uint8_t length, uint8_t *rsp, uint8_t *rsp_len)
{
    static const char fn[] = "get_buzzer_base"; /* ROM 0x788580 */
    static const char join[] = "join in get_buzzer_base"; /* ROM 0x77af24 */
    static const char join_c[] = "[pt_protocol_procsr]join in get_buzzer_base"; /* ROM 0x742440 */
    static const char got[] = "get_buzzer_base: buzzer_freq = %d, buzzer_duty = %d"; /* ROM 0x72ca28 */
    static const char got_c[] = "[pt_protocol_procsr]get_buzzer_base: buzzer_freq = %d, buzzer_duty = %d"; /* ROM 0x6fc6ec */

    PT_LOG0(3, fn, 0xd82u, join, join_c);
    if (PT_BAD_ARGS(payload, length, rsp, rsp_len, 4u)) {
        PT_PARA_NULL(fn, 0xd85u);
        return -1;
    }
    uint8_t idx = 0;
    PT_HEADER(rsp, idx, 0x62u, 3u, 5u);
    uint32_t frequency = nvdbBuzzerFrequencyGet();
    const uint8_t *bytes = (const uint8_t *)&frequency;
    for (uint32_t i = 0; i < 4u; i++)
        rsp[idx++] = bytes[i];
    uint8_t duty = nvdbBuzzerDutyGet();
    rsp[idx++] = duty;
    *rsp_len = idx;
    PT_LOGN(3, 2, fn, 0xd96u, got, got_c, frequency, duty);
    return 0;
}

/* cmd 0x63 set_buzzer_base: payload[4..7] = frequency, payload[8] = duty,
 * stored in NVDB. */
int32_t pt_cmd_64_handler(const uint8_t *payload, uint8_t length, uint8_t *rsp, uint8_t *rsp_len)
{
    static const char fn[] = "set_buzzer_base"; /* ROM 0x788590 */
    static const char join[] = "join in set_buzzer_base"; /* ROM 0x77af3c */
    static const char join_c[] = "[pt_protocol_procsr]join in set_buzzer_base"; /* ROM 0x74246c */
    static const char set[] = "set_buzzer_base: buzzer_freq = %d, buzzer_duty = %d"; /* ROM 0x72ca5c */
    static const char set_c[] = "[pt_protocol_procsr]set_buzzer_base: buzzer_freq = %d, buzzer_duty = %d"; /* ROM 0x6fc734 */

    PT_LOG0(3, fn, 0xd9cu, join, join_c);
    if (PT_BAD_ARGS(payload, length, rsp, rsp_len, 9u)) {
        PT_PARA_NULL(fn, 0xd9fu);
        return -1;
    }
    uint8_t idx = 0;
    PT_HEADER(rsp, idx, 0x63u, 3u, 1u);
    uint32_t frequency = pt_le32(&payload[4]);
    uint8_t duty = payload[8];
    nvdbBuzzerUpdate(frequency, duty);
    PT_LOGN(3, 2, fn, 0xdacu, set, set_c, frequency, duty);
    rsp[idx++] = PT_STATUS_OK;
    *rsp_len = idx;
    return 0;
}

/* cmd 0x64 get_panel_current: reply 0x64 with nvSysDt+0x2e (no argument check). */
int32_t pt_cmd_65_handler(const uint8_t *payload, uint8_t length, uint8_t *rsp, uint8_t *rsp_len)
{
    static const char fn[] = "get_panel_current"; /* ROM 0x782d30 */
    static const char join[] = "join in get_panel_current"; /* ROM 0x7707cc */
    static const char join_c[] = "[pt_protocol_procsr]join in get_panel_current"; /* ROM 0x737844 */
    (void)payload;
    (void)length;

    PT_LOG0(3, fn, 0xdb6u, join, join_c);
    uint8_t idx = 0;
    PT_HEADER(rsp, idx, 0x64u, 3u, 1u);
    rsp[idx++] = display_driver_ratio_cells_20003994[PT_NV_PANEL_CURRENT];
    *rsp_len = idx;
    return 0;
}

/* cmd 0x65 set_onboarding_status: payload[4] in {0, 1} -> onboarding KVDB
 * entry 0. Status 0 ok, 1 persist failed, 3 invalid value. */
int32_t pt_cmd_66_handler(const uint8_t *payload, uint8_t length, uint8_t *rsp, uint8_t *rsp_len)
{
    static const char fn[] = "set_onboarding_status"; /* ROM 0x77af54 */
    static const char join[] = "join in set_onboarding_status"; /* ROM 0x7645f0 */
    static const char join_c[] = "[pt_protocol_procsr]join in set_onboarding_status"; /* ROM 0x72ca90 */
    static const char set[] = "set onboarding status: %d"; /* ROM 0x7707e8 */
    static const char set_c[] = "[pt_protocol_procsr]set onboarding status: %d"; /* ROM 0x737874 */
    static const char bad[] = "onboarding status error, value: %d"; /* ROM 0x758d30 */
    static const char bad_c[] = "[pt_protocol_procsr]onboarding status error, value: %d"; /* ROM 0x721f28 */

    PT_LOG0(3, fn, 0xdc4u, join, join_c);
    if (PT_BAD_ARGS(payload, length, rsp, rsp_len, 5u)) {
        PT_PARA_NULL(fn, 0xdc7u);
        return -1;
    }
    uint8_t idx = 0;
    PT_HEADER(rsp, idx, 0x65u, 3u, 1u);
    uint8_t status = payload[4];
    if (status == 0u || status == 1u) {
        PT_LOGN(3, 1, fn, 0xdd6u, set, set_c, status);
        if (kvdbOnboardingConfigUpdateAndPersist(0u, &status) == 0)
            rsp[idx++] = PT_STATUS_OK;
        else
            rsp[idx++] = PT_STATUS_FAIL;
    } else {
        PT_LOGN(1, 1, fn, 0xde0u, bad, bad_c, status);
        rsp[idx++] = PT_STATUS_INVALID;
    }
    *rsp_len = idx;
    return 0;
}

/* cmd 0x66 restore_factory_settings: acknowledged only; the reset itself runs
 * later in pt_production_mode_orchestrate. */
int32_t pt_cmd_67_handler(const uint8_t *payload, uint8_t length, uint8_t *rsp, uint8_t *rsp_len)
{
    static const char fn[] = "restore_factory_settings"; /* ROM 0x770804 */
    static const char join[] = "join in restore_factory_settings"; /* ROM 0x758d54 */
    static const char join_c[] = "[pt_protocol_procsr]join in restore_factory_settings"; /* ROM 0x721f60 */

    PT_LOG0(3, fn, 0xdeau, join, join_c);
    if (PT_BAD_ARGS(payload, length, rsp, rsp_len, 4u)) {
        PT_PARA_NULL(fn, 0xdedu);
        return -1;
    }
    uint8_t idx = 0;
    PT_HEADER(rsp, idx, 0x66u, 3u, 1u);
    rsp[idx++] = PT_STATUS_OK;
    *rsp_len = idx;
    return 0;
}

/* cmd 0x67 get_imu_calibration_matrix: reply 0x67 with the 36-byte matrix. */
int32_t pt_cmd_69_handler(const uint8_t *payload, uint8_t length, uint8_t *rsp, uint8_t *rsp_len)
{
    static const char fn[] = "get_imu_calibration_matrix"; /* ROM 0x770820 */
    static const char join[] = "join in get_imu_calibration_matrix"; /* ROM 0x758d78 */
    static const char join_c[] = "[pt_protocol_procsr]join in get_imu_calibration_matrix"; /* ROM 0x721f98 */

    PT_LOG0(3, fn, 0xdfdu, join, join_c);
    if (PT_BAD_ARGS(payload, length, rsp, rsp_len, 4u)) {
        PT_PARA_NULL(fn, 0xe00u);
        return -1;
    }
    uint8_t idx = 0;
    PT_HEADER(rsp, idx, 0x67u, 3u, PT_IMU_CAL_LEN);
    (void)audio_queue_copy_bytes(&rsp[idx], g2_imu_calibration_matrix_2000396c, PT_IMU_CAL_LEN);
    idx = (uint8_t)(idx + PT_IMU_CAL_LEN);
    *rsp_len = idx;
    return 0;
}

/* cmd 0x69 set_battery_charger_status: payload[4] == 0 disables the nPM1300
 * charger, otherwise enables it. */
int32_t pt_cmd_6A_handler(const uint8_t *payload, uint8_t length, uint8_t *rsp, uint8_t *rsp_len)
{
    static const char fn[] = "set_battery_charger_status"; /* ROM 0x77083c */
    static const char join[] = "join in set_battery_charger_status"; /* ROM 0x758d9c */
    static const char join_c[] = "[pt_protocol_procsr]join in set_battery_charger_status"; /* ROM 0x721fd0 */
    static const char off[] = "disable battery charger"; /* ROM 0x77af6c */
    static const char off_c[] = "[pt_protocol_procsr]disable battery charger"; /* ROM 0x742498 */
    static const char on[] = "enable battery charger"; /* ROM 0x77af84 */
    static const char on_c[] = "[pt_protocol_procsr]enable battery charger"; /* ROM 0x7424c4 */

    PT_LOG0(3, fn, 0xe14u, join, join_c);
    if (PT_BAD_ARGS(payload, length, rsp, rsp_len, 5u)) {
        PT_PARA_NULL(fn, 0xe17u);
        return -1;
    }
    if (payload[4] == 0u) {
        PT_LOG0(3, fn, 0xe1eu, off, off_c);
        npmx_charger_disable_5128f8();
    } else {
        PT_LOG0(3, fn, 0xe24u, on, on_c);
        npmx_charger_enable_51299c();
    }
    uint8_t idx = 0;
    PT_HEADER(rsp, idx, 0x69u, 3u, 1u);
    rsp[idx++] = PT_STATUS_OK;
    *rsp_len = idx;
    return 0;
}

/* cmd 0x6a get_font_version: the XIP font name starts "a.b.c"; reply the
 * three digits as binary. */
int32_t pt_cmd_6B_handler(const uint8_t *payload, uint8_t length, uint8_t *rsp, uint8_t *rsp_len)
{
    static const char fn[] = "get_font_version"; /* ROM 0x782d44 */
    static const char join[] = "join in get_font_version"; /* ROM 0x770858 */
    static const char join_c[] = "[pt_protocol_procsr]join in get_font_version"; /* ROM 0x7378a4 */

    PT_LOG0(3, fn, 0xe36u, join, join_c);
    if (PT_BAD_ARGS(payload, length, rsp, rsp_len, 4u)) {
        PT_PARA_NULL(fn, 0xe39u);
        return -1;
    }
    const uint8_t *name = font_manager_xip_font_name_46d584();
    uint8_t major = name[0];
    uint8_t minor = name[2];
    uint8_t patch = name[4];
    uint8_t idx = 0;
    PT_HEADER(rsp, idx, 0x6au, 3u, 3u);
    rsp[idx++] = (uint8_t)(major - '0');
    rsp[idx++] = (uint8_t)(minor - '0');
    rsp[idx++] = (uint8_t)(patch - '0');
    *rsp_len = idx;
    return 0;
}

/* cmd 0x6b get_font_crc16: reply the boot-time font CRC failure flag. */
int32_t pt_cmd_6C_handler(const uint8_t *payload, uint8_t length, uint8_t *rsp, uint8_t *rsp_len)
{
    static const char fn[] = "get_font_crc16"; /* ROM 0x7885a0 */
    static const char join[] = "join in get_font_crc16"; /* ROM 0x77af9c */
    static const char join_c[] = "[pt_protocol_procsr]join in get_font_crc16"; /* ROM 0x7424f0 */

    PT_LOG0(3, fn, 0xe51u, join, join_c);
    if (PT_BAD_ARGS(payload, length, rsp, rsp_len, 4u)) {
        PT_PARA_NULL(fn, 0xe54u);
        return -1;
    }
    uint8_t idx = 0;
    PT_HEADER(rsp, idx, 0x6bu, 3u, 1u);
    rsp[idx++] = g2_pt_font_crc_failed;
    *rsp_len = idx;
    return 0;
}

/* cmd 0x6c calculate_font_crc16: acknowledged only; the CRC pass runs later in
 * pt_production_mode_orchestrate. */
int32_t pt_cmd_6D_handler(const uint8_t *payload, uint8_t length, uint8_t *rsp, uint8_t *rsp_len)
{
    static const char fn[] = "calculate_font_crc16"; /* ROM 0x77afb4 */
    static const char join[] = "join in calculate_font_crc16"; /* ROM 0x764610 */
    static const char join_c[] = "[pt_protocol_procsr]join in calculate_font_crc16"; /* ROM 0x72cac4 */

    PT_LOG0(3, fn, 0xe64u, join, join_c);
    if (PT_BAD_ARGS(payload, length, rsp, rsp_len, 4u)) {
        PT_PARA_NULL(fn, 0xe67u);
        return -1;
    }
    uint8_t idx = 0;
    PT_HEADER(rsp, idx, 0x6cu, 3u, 1u);
    rsp[idx++] = PT_STATUS_OK;
    *rsp_len = idx;
    return 0;
}

/* cmd 0x6d panel_show_gray_screen: starts display app 0x10f, then brightness
 * 50 (0x1bbc, 10) and the 0x60 / (0,0) / 0x20 panel setup. */
int32_t pt_cmd_6E_handler(const uint8_t *payload, uint8_t length, uint8_t *rsp, uint8_t *rsp_len)
{
    static const char fn[] = "panel_show_gray_screen"; /* ROM 0x77afcc */
    static const char join[] = "join in panel_show_gray_screen"; /* ROM 0x764630 */
    static const char join_c[] = "[pt_protocol_procsr]join in panel_show_gray_screen"; /* ROM 0x72caf8 */
    (void)payload;
    (void)length;

    PT_LOG0(3, fn, 0xe77u, join, join_c);
    uint8_t idx = 0;
    PT_HEADER(rsp, idx, 0x6du, 3u, 1u);
    if (productModeGet() == PT_PRODUCT_TEST_MODE) {
        (void)audio_uart_slave_display_start(PT_GRAY_SCREEN_APP, NULL, 0u);
        rsp[idx++] = PT_STATUS_OK;
        (void)display_driver_case4_apply(0x32u, 0x1bbcu, 10u);
        (void)display_driver_set_brightness_46c984(0x60u);
        (void)display_driver_set_offsets_46c9dc(0u, 0u);
        (void)display_driver_set_profile_46c9aa(0x20u);
    } else {
        PT_DENIED(fn, 0xe8cu);
        rsp[idx++] = PT_STATUS_NOT_TEST_MODE;
    }
    *rsp_len = idx;
    return 0;
}

/* cmd 0x6e panel_hide_gray_screen: stops display app 0x10f if the display
 * is active. */
int32_t pt_cmd_74_handler(const uint8_t *payload, uint8_t length, uint8_t *rsp, uint8_t *rsp_len)
{
    static const char fn[] = "panel_hide_gray_screen"; /* ROM 0x77afe4 */
    static const char join[] = "join in panel_hide_gray_screen"; /* ROM 0x764650 */
    static const char join_c[] = "[pt_protocol_procsr]join in panel_hide_gray_screen"; /* ROM 0x72cb2c */
    (void)payload;
    (void)length;

    PT_LOG0(3, fn, 0xe97u, join, join_c);
    uint8_t idx = 0;
    PT_HEADER(rsp, idx, 0x6eu, 3u, 1u);
    if (productModeGet() == PT_PRODUCT_TEST_MODE) {
        const uint8_t *state = display_startup_state_get_44347a();
        if (state != NULL && *state == 1u) {
            PT_LOG0(3, fn, 0xea4u, display_active, display_active_c);
            (void)audio_uart_slave_display_stop(PT_GRAY_SCREEN_APP, NULL, 0u);
        }
        rsp[idx++] = PT_STATUS_OK;
    } else {
        PT_DENIED(fn, 0xeabu);
        rsp[idx++] = PT_STATUS_NOT_TEST_MODE;
    }
    *rsp_len = idx;
    return 0;
}

/* cmd 0x74 panel_show_distortion_test_screen: display app 0x110, brightness
 * 100 (0x1bbc, 0x3f) and the same panel setup as the gray screen. */
int32_t pt_cmd_75_handler(const uint8_t *payload, uint8_t length, uint8_t *rsp, uint8_t *rsp_len)
{
    static const char fn[] = "panel_show_distortion_test_screen"; /* ROM 0x758dc0 */
    static const char join[] = "join in panel_show_distortion_test_screen"; /* ROM 0x74251c */
    static const char join_c[] = "[pt_protocol_procsr]join in panel_show_distortion_test_screen"; /* ROM 0x70e5a4 */
    (void)payload;
    (void)length;

    PT_LOG0(3, fn, 0xeb5u, join, join_c);
    uint8_t idx = 0;
    PT_HEADER(rsp, idx, 0x74u, 3u, 1u);
    if (productModeGet() == PT_PRODUCT_TEST_MODE) {
        (void)audio_uart_slave_display_start(PT_DISTORTION_SCREEN_APP, NULL, 0u);
        rsp[idx++] = PT_STATUS_OK;
        (void)display_driver_case4_apply(100u, 0x1bbcu, 0x3fu);
        (void)display_driver_set_brightness_46c984(0x60u);
        (void)display_driver_set_offsets_46c9dc(0u, 0u);
        (void)display_driver_set_profile_46c9aa(0x20u);
    } else {
        PT_DENIED(fn, 0xec9u);
        rsp[idx++] = PT_STATUS_NOT_TEST_MODE;
    }
    *rsp_len = idx;
    return 0;
}

/* cmd 0x75 panel_hide_distortion_test_screen: stops display app 0x110 if the
 * display is active. */
int32_t pt_cmd_77_handler(const uint8_t *payload, uint8_t length, uint8_t *rsp, uint8_t *rsp_len)
{
    static const char fn[] = "panel_hide_distortion_test_screen"; /* ROM 0x758de4 */
    static const char join[] = "join in panel_hide_distortion_test_screen"; /* ROM 0x742548 */
    static const char join_c[] = "[pt_protocol_procsr]join in panel_hide_distortion_test_screen"; /* ROM 0x70e5e4 */
    (void)payload;
    (void)length;

    PT_LOG0(3, fn, 0xed3u, join, join_c);
    uint8_t idx = 0;
    PT_HEADER(rsp, idx, 0x75u, 3u, 1u);
    if (productModeGet() == PT_PRODUCT_TEST_MODE) {
        const uint8_t *state = display_startup_state_get_44347a();
        if (state != NULL && *state == 1u) {
            PT_LOG0(3, fn, 0xee0u, display_active, display_active_c);
            (void)audio_uart_slave_display_stop(PT_DISTORTION_SCREEN_APP, NULL, 0u);
        }
        rsp[idx++] = PT_STATUS_OK;
    } else {
        PT_DENIED(fn, 0xee7u);
        rsp[idx++] = PT_STATUS_NOT_TEST_MODE;
    }
    *rsp_len = idx;
    return 0;
}

/* cmd 0x77 touch_set_base_line: acknowledge, then post input message id 3
 * (touch baseline reset). */
int32_t pt_cmd_F3_handler(const uint8_t *payload, uint8_t length, uint8_t *rsp, uint8_t *rsp_len)
{
    static const char fn[] = "touch_set_base_line"; /* ROM 0x782d58 */
    static const char join[] = "join in touch_set_base_line"; /* ROM 0x770874 */
    static const char join_c[] = "[pt_protocol_procsr]join in touch_set_base_line"; /* ROM 0x7378d4 */
    (void)payload;
    (void)length;

    PT_LOG0(3, fn, 0xef1u, join, join_c);
    uint8_t idx = 0;
    PT_HEADER(rsp, idx, 0x77u, 3u, 1u);
    rsp[idx++] = PT_STATUS_OK;
    audio_uart_case_in_case_side_effect_5130a6();
    *rsp_len = idx;
    return 0;
}
