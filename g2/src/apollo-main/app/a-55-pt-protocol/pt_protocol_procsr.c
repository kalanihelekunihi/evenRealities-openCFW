/* Product-test protocol processor core, stock
 * D:\01_workspace\s200_ap510b_iar_git\platform\product_test\pt_protocol_procsr.c
 * (path ROM 0x6ef458, module tag "pt_protocol_procsr" ROM 0x7829fc).
 * Native 0x56f178..0x56fd8d (calculate_rtc_time_diff_seconds ..
 * product_mode_config), literal pools 0x56f924..0x56f92b, 0x56fbe0..0x56fc0b,
 * 0x56fd90..0x56fdb3, 0x56ffac..0x56ffc3, 0x570120..0x57020f,
 * 0x570430..0x570437, 0x57053c..0x57056f, 0x570750..0x57077f.
 *
 * Frames come from the BLE production thread and the charging-box UART
 * (box_uart_mgr). pt_protocol_dispatch (stock process_pt_protocol) selects a
 * handler by request byte 0, lets it write the response body, then frames it
 * as 5a a5 ff <len> <body...> <sum8>. Unknown commands answer
 * <cmd> 01 03 01 02. After the response is sent, pt_production_mode_orchestrate
 * (stock pt_execute_operation) runs the deferred side effect for the command
 * found at response byte 4 (reset, file wipe, OTA frame, font CRC, ...).
 *
 * The symbol table's pt_cmd_XX_handler names do not match the command bytes
 * that select them (only 0x01, 0x05, 0x3e, 0x47, 0x48, 0x49, 0x52..0x55,
 * 0x57..0x5b agree); the comments give the real command byte. */
#include <stdint.h>
#include <stddef.h>

#define PT_HDR0              0x5au
#define PT_HDR1              0xa5u
#define PT_HDR2              0xffu
#define PT_PREFIX_LEN        4u
#define PT_FRAME_MAX         0x100u
#define PT_DATA_START        4u   /* response body offset after the prefix */
#define PT_DAY_SECONDS       86400u /* ROM 0x56f924 */

#define PT_ERR_PARAM         (-1)
#define PT_ERR_PREFIX        (-2)
#define PT_ERR_TOO_LONG      (-3)
#define PT_ERR_CHECKSUM      (-4)

/* Time record handed to the aging-time helper; only h/m/s are read. */
typedef struct {
    uint32_t reserved[6]; /* +0x00 */
    uint32_t hour;        /* +0x18 */
    uint32_t minute;      /* +0x1c */
    uint32_t second;      /* +0x20 */
} g2_pt_time_t;
_Static_assert(offsetof(g2_pt_time_t, hour) == 0x18u, "pt time hour");

typedef uint32_t (*g2_pt_handler_t)(const uint8_t *request, uint8_t length, uint8_t *response,
                                    uint8_t *response_length);

extern volatile uint8_t g2_pdm_production_bypass;  /* RAM 0x20075019, aging/production test active */
extern volatile uint8_t g2_pt_ota_frame_pending;   /* RAM 0x20075008 */
extern volatile uint32_t g2_pt_ota_frame_length;   /* RAM 0x200748e0 */
extern uint8_t g2_pt_ota_frame_buffer[];           /* RAM 0x20059ef8 */
extern volatile uint8_t g2_pt_font_crc_failed;     /* RAM 0x20004552 */

extern uint32_t audio_log_flags(void); /* 0x43d0ce */
extern void audio_log_extended(uint8_t, const char *, const char *, const char *, uint32_t,
                               const char *, ...); /* 0x43d574 */
extern uint32_t compress_log_output(uint32_t, const char *, const char *, ...); /* 0x43ce9e */
extern void *aeabi_memset_43c0e4(void *dst, uint32_t len, int32_t value); /* 0x43c0e4 */
extern int32_t file_tell(void *file);                                   /* 0x474870 */
extern int32_t file_seek(void *file, int32_t offset, int32_t origin);   /* 0x474814 */
extern void *file_open(const char *path, const char *mode);             /* 0x474550 */
extern int32_t file_close(void *file);                                  /* 0x4745f4 */
extern int32_t file_remove(const char *path);                           /* 0x47498c */
extern int32_t osDelay(uint32_t ticks);                                 /* 0x449376 */
extern void audio_ble_radio_ready_44b0ae(void);                         /* 0x44b0ae system reset wrapper */
extern void audio_uart_case_force_out_apply_4ac798(void);               /* 0x4ac798 */
extern uint32_t semantic_OtaFrameDispatch(uint8_t command, const uint8_t *data, uint16_t len); /* 0x448670 */
extern int32_t dev_setting_factory_cleanup_542d4c(void);                /* 0x542d4c alert close + KVDB/bond cleanup */
extern uint32_t product_check_font_a_crc_58f486(void);                  /* 0x58f486 */
extern uint32_t product_check_font_b_crc_58f490(void);                  /* 0x58f490 */
extern void productModeUpdate(uint8_t mode);                            /* 0x4abe66 */
extern uint8_t productModeRead(void);                                   /* 0x4abe8c */

uint32_t pt_cmd_01_handler(const uint8_t *request, uint8_t length, uint8_t *response,
                           uint8_t *response_length);

/* Command handlers (TSV names; real command byte in the comment). */
extern uint32_t pt_cmd_05_handler(const uint8_t *, uint8_t, uint8_t *, uint8_t *); /* 0x57293c, command 0x05 */
extern uint32_t pt_cmd_35_handler(const uint8_t *, uint8_t, uint8_t *, uint8_t *); /* 0x57320c, command 0x06 */
extern uint32_t pt_cmd_06_handler(const uint8_t *, uint8_t, uint8_t *, uint8_t *); /* 0x572a34, command 0x07 */
extern uint32_t pt_cmd_07_handler(const uint8_t *, uint8_t, uint8_t *, uint8_t *); /* 0x572af0, command 0x08 */
extern uint32_t pt_cmd_08_handler(const uint8_t *, uint8_t, uint8_t *, uint8_t *); /* 0x572ba0, command 0x0b */
extern uint32_t pt_cmd_0B_handler(const uint8_t *, uint8_t, uint8_t *, uint8_t *); /* 0x56ffc4, command 0x11 */
extern uint32_t pt_cmd_11_handler(const uint8_t *, uint8_t, uint8_t *, uint8_t *); /* 0x56fdb4, command 0x13 */
extern uint32_t pt_cmd_13_handler(const uint8_t *, uint8_t, uint8_t *, uint8_t *); /* 0x570780, command 0x17 */
extern uint32_t pt_cmd_17_handler(const uint8_t *, uint8_t, uint8_t *, uint8_t *); /* 0x5709c4, command 0x18 */
extern uint32_t pt_cmd_18_handler(const uint8_t *, uint8_t, uint8_t *, uint8_t *); /* 0x570d40, command 0x19 */
extern uint32_t pt_cmd_19_handler(const uint8_t *, uint8_t, uint8_t *, uint8_t *); /* 0x571064, command 0x1a */
extern uint32_t pt_cmd_1A_handler(const uint8_t *, uint8_t, uint8_t *, uint8_t *); /* 0x5713d8, command 0x1b */
extern uint32_t pt_cmd_38_handler(const uint8_t *, uint8_t, uint8_t *, uint8_t *); /* 0x573310, command 0x1c */
extern uint32_t pt_cmd_1B_handler(const uint8_t *, uint8_t, uint8_t *, uint8_t *); /* 0x57200c, command 0x20 */
extern uint32_t pt_cmd_39_handler(const uint8_t *, uint8_t, uint8_t *, uint8_t *); /* 0x5734cc, command 0x22 */
extern uint32_t pt_cmd_1C_handler(const uint8_t *, uint8_t, uint8_t *, uint8_t *); /* 0x570570, command 0x24 */
extern uint32_t pt_cmd_20_handler(const uint8_t *, uint8_t, uint8_t *, uint8_t *); /* 0x571cd4, command 0x25 */
extern uint32_t pt_cmd_22_handler(const uint8_t *, uint8_t, uint8_t *, uint8_t *); /* 0x571e44, command 0x26 */
extern uint32_t pt_cmd_24_handler(const uint8_t *, uint8_t, uint8_t *, uint8_t *); /* 0x5726f0, command 0x29 */
extern uint32_t pt_cmd_25_handler(const uint8_t *, uint8_t, uint8_t *, uint8_t *); /* 0x572858, command 0x2a */
extern uint32_t pt_cmd_3A_handler(const uint8_t *, uint8_t, uint8_t *, uint8_t *); /* 0x573604, command 0x2d */
extern uint32_t pt_cmd_3D_handler(const uint8_t *, uint8_t, uint8_t *, uint8_t *); /* 0x5738d0, command 0x2e */
extern uint32_t pt_cmd_26_handler(const uint8_t *, uint8_t, uint8_t *, uint8_t *); /* 0x57222c, command 0x30 */
extern uint32_t pt_cmd_29_handler(const uint8_t *, uint8_t, uint8_t *, uint8_t *); /* 0x572394, command 0x31 */
extern uint32_t pt_cmd_2A_handler(const uint8_t *, uint8_t, uint8_t *, uint8_t *); /* 0x572c64, command 0x35 */
extern uint32_t pt_cmd_2D_handler(const uint8_t *, uint8_t, uint8_t *, uint8_t *); /* 0x570210, command 0x38 */
extern uint32_t pt_cmd_45_handler(const uint8_t *, uint8_t, uint8_t *, uint8_t *); /* 0x570438, command 0x39 */
extern uint32_t pt_cmd_2E_handler(const uint8_t *, uint8_t, uint8_t *, uint8_t *); /* 0x570b60, command 0x3a */
extern uint32_t pt_cmd_46_handler(const uint8_t *, uint8_t, uint8_t *, uint8_t *); /* 0x574580, command 0x3d */
extern uint32_t pt_cmd_3E_handler(const uint8_t *, uint8_t, uint8_t *, uint8_t *); /* 0x573c58, command 0x3e */
extern uint32_t pt_cmd_30_handler(const uint8_t *, uint8_t, uint8_t *, uint8_t *); /* 0x5724f4, command 0x42 */
extern uint32_t pt_cmd_31_handler(const uint8_t *, uint8_t, uint8_t *, uint8_t *); /* 0x57303c, command 0x43 */
extern uint32_t pt_cmd_42_handler(const uint8_t *, uint8_t, uint8_t *, uint8_t *); /* 0x573f88, command 0x44 */
extern uint32_t pt_cmd_43_handler(const uint8_t *, uint8_t, uint8_t *, uint8_t *); /* 0x5741e0, command 0x45 */
extern uint32_t pt_cmd_44_handler(const uint8_t *, uint8_t, uint8_t *, uint8_t *); /* 0x574464, command 0x46 */
extern uint32_t pt_cmd_47_handler(const uint8_t *, uint8_t, uint8_t *, uint8_t *); /* 0x574808, command 0x47 */
extern uint32_t pt_cmd_48_handler(const uint8_t *, uint8_t, uint8_t *, uint8_t *); /* 0x574f60, command 0x48 */
extern uint32_t pt_cmd_49_handler(const uint8_t *, uint8_t, uint8_t *, uint8_t *); /* 0x57522c, command 0x49 */
extern uint32_t pt_cmd_52_handler(const uint8_t *, uint8_t, uint8_t *, uint8_t *); /* 0x575470, command 0x52 */
extern uint32_t pt_cmd_53_handler(const uint8_t *, uint8_t, uint8_t *, uint8_t *); /* 0x575548, command 0x53 */
extern uint32_t pt_cmd_54_handler(const uint8_t *, uint8_t, uint8_t *, uint8_t *); /* 0x575708, command 0x54 */
extern uint32_t pt_cmd_55_handler(const uint8_t *, uint8_t, uint8_t *, uint8_t *); /* 0x5759fc, command 0x55 */
extern uint32_t pt_cmd_57_handler(const uint8_t *, uint8_t, uint8_t *, uint8_t *); /* 0x57536c, command 0x57 */
extern uint32_t pt_cmd_58_handler(const uint8_t *, uint8_t, uint8_t *, uint8_t *); /* 0x575af8, command 0x58 */
extern uint32_t pt_cmd_59_handler(const uint8_t *, uint8_t, uint8_t *, uint8_t *); /* 0x575eb4, command 0x59 */
extern uint32_t pt_cmd_5A_handler(const uint8_t *, uint8_t, uint8_t *, uint8_t *); /* 0x57612c, command 0x5a */
extern uint32_t pt_cmd_5B_handler(const uint8_t *, uint8_t, uint8_t *, uint8_t *); /* 0x576518, command 0x5b */
extern uint32_t pt_cmd_61_handler(const uint8_t *, uint8_t, uint8_t *, uint8_t *); /* 0x576800, command 0x60 */
extern uint32_t pt_cmd_62_handler(const uint8_t *, uint8_t, uint8_t *, uint8_t *); /* 0x5768c8, command 0x61 */
extern uint32_t pt_cmd_63_handler(const uint8_t *, uint8_t, uint8_t *, uint8_t *); /* 0x576a54, command 0x62 */
extern uint32_t pt_cmd_64_handler(const uint8_t *, uint8_t, uint8_t *, uint8_t *); /* 0x576bd4, command 0x63 */
extern uint32_t pt_cmd_65_handler(const uint8_t *, uint8_t, uint8_t *, uint8_t *); /* 0x576d48, command 0x64 */
extern uint32_t pt_cmd_66_handler(const uint8_t *, uint8_t, uint8_t *, uint8_t *); /* 0x576df8, command 0x65 */
extern uint32_t pt_cmd_67_handler(const uint8_t *, uint8_t, uint8_t *, uint8_t *); /* 0x576fd0, command 0x66 */
extern uint32_t pt_cmd_69_handler(const uint8_t *, uint8_t, uint8_t *, uint8_t *); /* 0x5770cc, command 0x67 */
extern uint32_t pt_cmd_6A_handler(const uint8_t *, uint8_t, uint8_t *, uint8_t *); /* 0x5771d4, command 0x69 */
extern uint32_t pt_cmd_6B_handler(const uint8_t *, uint8_t, uint8_t *, uint8_t *); /* 0x577364, command 0x6a */
extern uint32_t pt_cmd_6C_handler(const uint8_t *, uint8_t, uint8_t *, uint8_t *); /* 0x57747c, command 0x6b */
extern uint32_t pt_cmd_6D_handler(const uint8_t *, uint8_t, uint8_t *, uint8_t *); /* 0x57757c, command 0x6c */
extern uint32_t pt_cmd_6E_handler(const uint8_t *, uint8_t, uint8_t *, uint8_t *); /* 0x577678, command 0x6d */
extern uint32_t pt_cmd_74_handler(const uint8_t *, uint8_t, uint8_t *, uint8_t *); /* 0x577794, command 0x6e */
extern uint32_t pt_cmd_75_handler(const uint8_t *, uint8_t, uint8_t *, uint8_t *); /* 0x5778d4, command 0x74 */
extern uint32_t pt_cmd_77_handler(const uint8_t *, uint8_t, uint8_t *, uint8_t *); /* 0x5779e0, command 0x75 */
extern uint32_t pt_cmd_F3_handler(const uint8_t *, uint8_t, uint8_t *, uint8_t *); /* 0x577afc, command 0x77 */
extern uint32_t pt_cmd_60_handler(const uint8_t *, uint8_t, uint8_t *, uint8_t *); /* 0x576714, command 0xf3 */

static const char module_tag[] = "pt_protocol_procsr"; /* ROM 0x7829fc */
static const char source_file[] = "D:\\01_workspace\\s200_ap510b_iar_git\\platform\\product_test\\pt_protocol_procsr.c"; /* ROM 0x6ef458 */
static const char fn_time_diff[] = "calculate_rtc_time_diff_seconds"; /* ROM 0x7642b0 */
static const char fn_file_size[] = "get_file_size_by_fp";             /* ROM 0x782a10 */
static const char fn_process[] = "process_pt_protocol";               /* ROM 0x782a38 */
static const char fn_execute[] = "pt_execute_operation";              /* ROM 0x77ac84 */
static const char fn_mode_config[] = "product_mode_config";           /* ROM 0x782a60 */

static const char time_diff[] = "Aging Time diff calculated: %d seconds (start: %02d:%02d:%02d, end: %02d:%02d:%02d)"; /* ROM 0x6e9658 */
static const char time_diff_s[] = "[pt_protocol_procsr]Aging Time diff calculated: %d seconds (start: %02d:%02d:%02d, end: %02d:%02d:%02d)"; /* ROM 0x6d976c */
static const char fp_null[] = "fp is NULL";                                      /* ROM 0x78bcf0 */
static const char fp_null_s[] = "[pt_protocol_procsr]fp is NULL";                /* ROM 0x7642d0 */
static const char tell_cur_fail[] = "ftell current position failed";             /* ROM 0x7642f0 */
static const char tell_cur_fail_s[] = "[pt_protocol_procsr]ftell current position failed"; /* ROM 0x72c410 */
static const char seek_end_fail[] = "fseek to SEEK_END failed";                  /* ROM 0x770414 */
static const char seek_end_fail_s[] = "[pt_protocol_procsr]fseek to SEEK_END failed"; /* ROM 0x737154 */
static const char tell_size_fail[] = "ftell size failed";                        /* ROM 0x782a24 */
static const char tell_size_fail_s[] = "[pt_protocol_procsr]ftell size failed";  /* ROM 0x74d264 */
static const char restore_fail[] = "restore position with SEEK_SET failed";      /* ROM 0x74d28c */
static const char restore_fail_s[] = "[pt_protocol_procsr]restore position with SEEK_SET failed"; /* ROM 0x717de8 */
static const char size_fmt[] = "size=%ld";                                       /* ROM 0x78bcfc */
static const char size_fmt_s[] = "[pt_protocol_procsr]size=%ld";                 /* ROM 0x764310 */
static const char para_error[] = "%s para is error\n";                           /* ROM 0x782a4c */
static const char para_error_s[] = "[pt_protocol_procsr]%s para is error\n";     /* ROM 0x74d2b4 */
static const char send_value[] = "send_value[data_start_idx + 3] = %d,send_value[data_start_idx + 4] = %d"; /* ROM 0x6fc344 */
static const char send_value_s[] = "[pt_protocol_procsr]send_value[data_start_idx + 3] = %d,send_value[data_start_idx + 4] = %d"; /* ROM 0x6e148c */
static const char no_file[] = "File does not exist, skip deletion: %s";          /* ROM 0x74d2dc */
static const char no_file_s[] = "[pt_protocol_procsr]File does not exist, skip deletion: %s"; /* ROM 0x717e24 */
static const char delete_fail[] = "Failed to delete file: %s";                   /* ROM 0x77044c */
static const char delete_fail_s[] = "[pt_protocol_procsr]Failed to delete file: %s"; /* ROM 0x737184 */
static const char delete_ok[] = "Successfully deleted file: %s";                 /* ROM 0x764330 */
static const char delete_ok_s[] = "[pt_protocol_procsr]Successfully deleted file: %s"; /* ROM 0x72c444 */
static const char mode_join[] = "join in product_mode_config";                   /* ROM 0x770468 */
static const char mode_join_s[] = "[pt_protocol_procsr]join in product_mode_config"; /* ROM 0x7371b4 */
static const char para_null[] = "%s para is NULL\n";                             /* ROM 0x782a74 */
static const char para_null_s[] = "[pt_protocol_procsr]%s para is NULL\n";       /* ROM 0x74d304 */
static const char bad_value[] = "[%s-%d]invalid vaule \n";                       /* ROM 0x77accc */
static const char bad_value_s[] = "[pt_protocol_procsr][%s-%d]invalid vaule \n"; /* ROM 0x741f9c */
static const char read_mode[] = "r";                                             /* ROM 0x56fd94 */

static const char path_ota[] = "ota/s200_firmware_ota.bin";   /* ROM 0x770430 */
static const char path_rear_mic[] = "audio/rear_mic_00.pcm";  /* ROM 0x77ac9c */
static const char path_front_mic[] = "audio/front_mic_00.pcm"; /* ROM 0x77acb4 */
/* Files wiped by command 0x06 (ROM 0x78bd38). */
static const char *const wipe_files[3] = {path_ota, path_rear_mic, path_front_mic};

#define LOG_E(level, fn, line, ...)                                                          \
    do {                                                                                     \
        if ((audio_log_flags() & 2u) != 0u)                                                  \
            audio_log_extended((level), module_tag, source_file, (fn), (line), __VA_ARGS__); \
    } while (0)
#define LOG_C(code, text, ...)                                                    \
    do {                                                                          \
        if ((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)     \
            (void)compress_log_output((code), (text), (text), ##__VA_ARGS__);     \
    } while (0)

/* Seconds from start to end h:m:s, wrapping once across midnight. */
int32_t calculate_rtc_time_diff_seconds_56f178(const g2_pt_time_t *end, const g2_pt_time_t *start)
{
    if (start == NULL || end == NULL)
        return 0;
    uint32_t start_s = start->hour * 3600u + start->minute * 60u + start->second;
    uint32_t end_s = end->hour * 3600u + end->minute * 60u + end->second;
    if (end_s < start_s)
        end_s += PT_DAY_SECONDS;
    int32_t diff = (int32_t)(end_s - start_s);
    LOG_E(2u, fn_time_diff, 0x140u, time_diff, diff, start->hour, start->minute, start->second,
          end->hour, end->minute, end->second);
    LOG_C(0x09c00000u, time_diff_s, diff, start->hour, start->minute, start->second, end->hour,
          end->minute, end->second);
    return diff;
}

/* File size via tell/seek-end/tell, restoring the position; -1 on failure. */
int32_t get_file_size_by_fp_56f23a(void *fp)
{
    if (fp == NULL) {
        LOG_E(1u, fn_file_size, 0x14au, fp_null);
        LOG_C(0x04000000u, fp_null_s);
        return -1;
    }
    int32_t position = file_tell(fp);
    if (position < 0) {
        LOG_E(1u, fn_file_size, 0x150u, tell_cur_fail);
        LOG_C(0x04000000u, tell_cur_fail_s);
        return -1;
    }
    if (file_seek(fp, 0, 2) != 0) {
        LOG_E(1u, fn_file_size, 0x155u, seek_end_fail);
        LOG_C(0x04000000u, seek_end_fail_s);
        return -1;
    }
    int32_t size = file_tell(fp);
    if (size < 0) {
        LOG_E(1u, fn_file_size, 0x15bu, tell_size_fail);
        LOG_C(0x04000000u, tell_size_fail_s);
    }
    if (file_seek(fp, position, 0) != 0) {
        LOG_E(2u, fn_file_size, 0x15fu, restore_fail);
        LOG_C(0x08000000u, restore_fail_s);
    }
    LOG_E(3u, fn_file_size, 0x161u, size_fmt, size);
    LOG_C(0x0c400000u, size_fmt_s, size);
    return size;
}

int32_t pt_response_prefix(uint8_t *prefix, uint8_t body_length, uint8_t *prefix_length)
{
    if (prefix == NULL || prefix_length == NULL)
        return -1;
    prefix[0] = PT_HDR0;
    prefix[1] = PT_HDR1;
    prefix[2] = PT_HDR2;
    prefix[3] = body_length;
    *prefix_length = PT_PREFIX_LEN;
    return 0;
}

/* Appends the 8-bit sum of frame[0..len) and grows len by one. */
int32_t pt_response_checksum(uint8_t *frame, uint8_t *length)
{
    if (frame == NULL || length == NULL)
        return -1;
    uint8_t sum = 0u;
    uint8_t n = *length;
    for (int32_t i = 0; i < (int32_t)n; i++)
        sum = (uint8_t)(sum + frame[i]);
    frame[n] = sum;
    *length = (uint8_t)(n + 1u);
    return 0;
}

uint32_t pt_protocol_dispatch(const uint8_t *payload, uint8_t length, uint8_t *response,
                              uint8_t *response_length)
{
    if (payload == NULL || length == 0u || response == NULL || response_length == NULL) {
        LOG_E(1u, fn_process, 399u, para_error, fn_process);
        LOG_C(0x04400000u, para_error_s, fn_process);
        return (uint32_t)PT_ERR_PARAM;
    }

    uint8_t command = payload[0];
    g2_pt_handler_t handler = NULL;
    switch (command) {
    case 0x01u: handler = pt_cmd_01_handler; break;
    case 0x05u: handler = pt_cmd_05_handler; break;
    case 0x06u: handler = pt_cmd_35_handler; break;
    case 0x07u: handler = pt_cmd_06_handler; break;
    case 0x08u: handler = pt_cmd_07_handler; break;
    case 0x0bu: handler = pt_cmd_08_handler; break;
    case 0x11u: handler = pt_cmd_0B_handler; break;
    case 0x13u: handler = pt_cmd_11_handler; break;
    case 0x17u: handler = pt_cmd_13_handler; break;
    case 0x18u: handler = pt_cmd_17_handler; break;
    case 0x19u: handler = pt_cmd_18_handler; break;
    case 0x1au: handler = pt_cmd_19_handler; break;
    case 0x1bu: handler = pt_cmd_1A_handler; break;
    case 0x1cu: handler = pt_cmd_38_handler; break;
    case 0x20u: handler = pt_cmd_1B_handler; break;
    case 0x22u: handler = pt_cmd_39_handler; break;
    case 0x24u: handler = pt_cmd_1C_handler; break;
    case 0x25u: handler = pt_cmd_20_handler; break;
    case 0x26u: handler = pt_cmd_22_handler; break;
    case 0x29u: handler = pt_cmd_24_handler; break;
    case 0x2au: handler = pt_cmd_25_handler; break;
    case 0x2du: handler = pt_cmd_3A_handler; break;
    case 0x2eu: handler = pt_cmd_3D_handler; break;
    case 0x30u: handler = pt_cmd_26_handler; break;
    case 0x31u: handler = pt_cmd_29_handler; break;
    case 0x35u: handler = pt_cmd_2A_handler; break;
    case 0x38u: handler = pt_cmd_2D_handler; break;
    case 0x39u: handler = pt_cmd_45_handler; break;
    case 0x3au: handler = pt_cmd_2E_handler; break;
    case 0x3du: handler = pt_cmd_46_handler; break;
    case 0x3eu: handler = pt_cmd_3E_handler; break;
    case 0x42u: handler = pt_cmd_30_handler; break;
    case 0x43u: handler = pt_cmd_31_handler; break;
    case 0x44u: handler = pt_cmd_42_handler; break;
    case 0x45u: handler = pt_cmd_43_handler; break;
    case 0x46u: handler = pt_cmd_44_handler; break;
    case 0x47u: handler = pt_cmd_47_handler; break;
    case 0x48u: handler = pt_cmd_48_handler; break;
    case 0x49u: handler = pt_cmd_49_handler; break;
    case 0x52u: handler = pt_cmd_52_handler; break;
    case 0x53u: handler = pt_cmd_53_handler; break;
    case 0x54u: handler = pt_cmd_54_handler; break;
    case 0x55u: handler = pt_cmd_55_handler; break;
    case 0x57u: handler = pt_cmd_57_handler; break;
    case 0x58u: handler = pt_cmd_58_handler; break;
    case 0x59u: handler = pt_cmd_59_handler; break;
    case 0x5au: handler = pt_cmd_5A_handler; break;
    case 0x5bu: handler = pt_cmd_5B_handler; break;
    case 0x60u: handler = pt_cmd_61_handler; break;
    case 0x61u: handler = pt_cmd_62_handler; break;
    case 0x62u: handler = pt_cmd_63_handler; break;
    case 0x63u: handler = pt_cmd_64_handler; break;
    case 0x64u: handler = pt_cmd_65_handler; break;
    case 0x65u: handler = pt_cmd_66_handler; break;
    case 0x66u: handler = pt_cmd_67_handler; break;
    case 0x67u: handler = pt_cmd_69_handler; break;
    case 0x69u: handler = pt_cmd_6A_handler; break;
    case 0x6au: handler = pt_cmd_6B_handler; break;
    case 0x6bu: handler = pt_cmd_6C_handler; break;
    case 0x6cu: handler = pt_cmd_6D_handler; break;
    case 0x6du: handler = pt_cmd_6E_handler; break;
    case 0x6eu: handler = pt_cmd_74_handler; break;
    case 0x74u: handler = pt_cmd_75_handler; break;
    case 0x75u: handler = pt_cmd_77_handler; break;
    case 0x77u: handler = pt_cmd_F3_handler; break;
    case 0xf3u: handler = pt_cmd_60_handler; break;
    default: handler = NULL; break;
    }
    if (handler != NULL) {
        (void)handler(payload, length, response, response_length);
    } else {
        uint8_t i = 0u;
        response[i++] = command;
        response[i++] = 1u;
        response[i++] = 3u;
        response[i++] = 1u;
        response[i++] = 2u;
        *response_length = i;
    }

    uint8_t prefix[10];
    uint8_t prefix_length;
    uint8_t body[PT_FRAME_MAX];
    (void)aeabi_memset_43c0e4(prefix, sizeof prefix, 0);
    prefix_length = 0u;
    if (pt_response_prefix(prefix, *response_length, &prefix_length) != 0)
        return (uint32_t)PT_ERR_PREFIX;
    if ((int32_t)*response_length + (int32_t)prefix_length >= (int32_t)PT_FRAME_MAX + 1)
        return (uint32_t)PT_ERR_TOO_LONG;
    (void)aeabi_memset_43c0e4(body, sizeof body, 0);
    for (int32_t i = 0; i < (int32_t)*response_length; i++)
        body[i] = response[i];
    for (int32_t i = 0; i < (int32_t)prefix_length; i++)
        response[i] = prefix[i];
    for (int32_t i = 0; i < (int32_t)*response_length; i++)
        response[(uint8_t)(i + prefix_length)] = body[i];
    *response_length = (uint8_t)(prefix_length + *response_length);
    if (pt_response_checksum(response, response_length) != 0)
        return (uint32_t)PT_ERR_CHECKSUM;
    return 0u;
}

/* Deferred action after the framed response for response[4] was sent. */
uint32_t pt_production_mode_orchestrate(const uint8_t *payload, uint8_t length, const uint8_t *response,
                                        uint8_t response_length)
{
    (void)length;
    uint8_t idx = PT_DATA_START;
    if (payload == NULL || response == NULL || response_length < idx) {
        LOG_E(1u, fn_execute, 0x35du, para_error, fn_execute);
        LOG_C(0x04400000u, para_error_s, fn_execute);
        return (uint32_t)PT_ERR_PARAM;
    }

    switch (response[idx]) {
    case 0x01: /* product mode set: reset when the status byte is 0 */
        LOG_E(3u, fn_execute, 0x366u, send_value, response[idx + 3u], response[idx + 4u]);
        LOG_C(0x0c800000u, send_value_s, response[idx + 3u], response[idx + 4u]);
        if (response[idx + 4u] == 0u) {
            (void)osDelay(1000u);
            audio_ble_radio_ready_44b0ae();
        }
        break;
    case 0x06: { /* wipe OTA image and microphone captures */
        const char *paths[3];
        paths[0] = wipe_files[0];
        paths[1] = wipe_files[1];
        paths[2] = wipe_files[2];
        for (uint32_t i = 0u; i < 3u; i++) {
            void *fp = file_open(paths[i], read_mode);
            if (fp == NULL) {
                LOG_E(3u, fn_execute, 0x3a5u, no_file, paths[i]);
                LOG_C(0x0c400000u, no_file_s, paths[i]);
                continue;
            }
            (void)file_close(fp);
            if (file_remove(paths[i]) == 0) {
                LOG_E(3u, fn_execute, 0x39cu, delete_ok, paths[i]);
                LOG_C(0x0c400000u, delete_ok_s, paths[i]);
            } else {
                LOG_E(1u, fn_execute, 0x3a0u, delete_fail, paths[i]);
                LOG_C(0x04400000u, delete_fail_s, paths[i]);
            }
        }
        break;
    }
    case 0x0b:
        (void)osDelay(1000u);
        audio_ble_radio_ready_44b0ae();
        break;
    case 0x13:
        audio_uart_case_force_out_apply_4ac798();
        break;
    case 0x3e: /* leave aging test: clear the PDM bypass and reset */
        if (payload[idx] == 0u) {
            g2_pdm_production_bypass = 0u;
            (void)osDelay(2000u);
            audio_ble_radio_ready_44b0ae();
        }
        break;
    case 0x54: /* forward the staged OTA frame */
        if (g2_pt_ota_frame_pending != 0u) {
            g2_pt_ota_frame_pending = 0u;
            (void)semantic_OtaFrameDispatch(0xc1u, g2_pt_ota_frame_buffer,
                                            (uint16_t)g2_pt_ota_frame_length);
            g2_pt_ota_frame_length = 0u;
        }
        break;
    case 0x66:
        (void)dev_setting_factory_cleanup_542d4c();
        break;
    case 0x6c: /* font image CRC self-check */
        g2_pt_font_crc_failed = 0u;
        g2_pt_font_crc_failed = (uint8_t)(product_check_font_a_crc_58f486() | g2_pt_font_crc_failed);
        g2_pt_font_crc_failed = (uint8_t)(product_check_font_b_crc_58f490() | g2_pt_font_crc_failed);
        break;
    default:
        break;
    }
    return 0u;
}

/* Command 0x01: request byte 4 selects product mode 0/1. Response status
 * byte 4: 0 changed, 4 already set, 3 invalid value. */
uint32_t pt_cmd_01_handler(const uint8_t *request, uint8_t length, uint8_t *response,
                           uint8_t *response_length)
{
    LOG_E(3u, fn_mode_config, 0x3cfu, mode_join);
    LOG_C(0x0c000000u, mode_join_s);
    if (response == NULL || response_length == NULL || request == NULL || length < 5u) {
        LOG_E(1u, fn_mode_config, 0x3d2u, para_null, fn_mode_config);
        LOG_C(0x04400000u, para_null_s, fn_mode_config);
        return (uint32_t)PT_ERR_PARAM;
    }
    uint8_t i = 0u;
    response[i++] = 1u;
    response[i++] = 1u;
    response[i++] = 3u;
    response[i++] = 1u;
    uint8_t mode = request[4];
    if (mode == 0u || mode == 1u) {
        if (mode == productModeRead()) {
            response[i++] = 4u;
        } else {
            response[i++] = 0u;
            productModeUpdate(mode);
        }
    } else {
        LOG_E(2u, fn_mode_config, 0x3dfu, bad_value, fn_mode_config, 0x3dfu);
        LOG_C(0x08800000u, bad_value_s, fn_mode_config, 0x3dfu);
        response[i++] = 3u;
    }
    *response_length = i;
    return 0u;
}
