/* Touch-controller firmware update service, stock
 * D:\01_workspace\s200_ap510b_iar_git\platform\input\touchDFU\service_touch_dfu.c.
 * Native 0x55fcb4..0x56170f; literal pools 0x5608b0..0x56092b,
 * 0x560ed4..0x560efb, 0x561078..0x56110b, 0x561710..0x56180f and the
 * open-mode string "r+" at 0x560a64 inside load_touch_firmware_from_package.
 * 0x560ea2..0x560ea7 is padding.
 *
 * Host side of the Infineon cy_dfu bootloader protocol, described in
 * g2_touch_dfu.h. The FWPK container is described with the structs below. */
#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>
#include "g2_touch_cy8c4046.h"
#include "g2_touch_dfu.h"

/* cy_dfu packet framing and commands. */
#define DFU_SOP              0x01u
#define DFU_EOP              0x17u
#define DFU_HEADER_LEN       4u   /* SOP, cmd, len u16 */
#define DFU_OVERHEAD         7u   /* header + sum16 + EOP */
#define DFU_MAX_PACKET_DATA  32u
#define DFU_REPLY_LEN        15u
#define DFU_REPLY_TRIES      100u
#define DFU_ROW_SIZE         128u /* four 32-byte send-data packets per program-data */
#define DFU_PACKETS_PER_ROW  (DFU_ROW_SIZE / DFU_MAX_PACKET_DATA)

#define DFU_CMD_VERIFY_APP   0x31u
#define DFU_CMD_SEND_DATA    0x37u
#define DFU_CMD_ENTER        0x38u
#define DFU_CMD_EXIT         0x3bu
#define DFU_CMD_PROGRAM_DATA 0x49u
#define DFU_CMD_SET_APP_META 0x4cu

/* Host-side status values (cy_dfu status codes). */
#define DFU_ERROR_LENGTH     0x03u
#define DFU_ERROR_DATA       0x04u
#define DFU_ERROR_CHECKSUM   0x08u
#define DFU_ERROR_UNKNOWN    0x0fu
#define DFU_ERROR_FRAME      0xaau /* host-only: short reply or bad SOP */

#define TOUCH_APP_ID         1u
#define TOUCH_APP_START      0x3300u /* touch payload link address */

/* /firmware/touch.bin: 16-byte header followed by 16-byte records. */
#define FWPK_MAGIC           0x4b505746u /* "FWPK" */
#define FWPK_TYPE_TOUCH      3u
typedef struct {
    uint32_t magic;    /* +0x0 */
    uint32_t version;  /* +0x4 a.b.c.d, most significant byte first */
    uint32_t count;    /* +0x8 record count */
    uint32_t reserved; /* +0xc */
} g2_fwpk_header_t;
typedef struct {
    uint32_t type;     /* +0x0 */
    uint32_t size;     /* +0x4 includes the trailing 4 bytes */
    uint32_t offset;   /* +0x8 from file start */
    uint32_t crc32;    /* +0xc CRC-32C over size bytes */
} g2_fwpk_record_t;
_Static_assert(sizeof(g2_fwpk_header_t) == 16, "FWPK header is 16 bytes");
_Static_assert(sizeof(g2_fwpk_record_t) == 16, "FWPK record is 16 bytes");

/* Set-application-metadata payload; the stock code copies a 12-byte ROM
 * template (0x78c098) and stores the length over bytes 5..8. */
typedef struct __attribute__((packed)) {
    uint8_t app;       /* +0x0 */
    uint32_t start;    /* +0x1 */
    uint32_t length;   /* +0x5 */
    uint8_t pad[3];
} g2_touch_app_meta_t;
_Static_assert(sizeof(g2_touch_app_meta_t) == 12, "stock metadata template is 12 bytes");

typedef struct {
    uint32_t address;  /* +0x0 flash address */
    uint32_t crc32c;   /* +0x4 CRC-32C of the 128-byte row */
} g2_touch_program_data_t;

extern void *g2_touch_fw_package_file;   /* RAM 0x20074998 */
extern uint8_t *g2_touch_fw_image;       /* RAM 0x2007499c file-heap buffer */
extern uint32_t g2_touch_fw_image_length; /* RAM 0x200749a0 bytes to program */
extern char g2_touch_version_string[32]; /* RAM 0x200739bc */

/* Same-module driver helpers reconstructed in another unit. */
extern void cy8c4046fni_reset_55b64a(void);                         /* GPIO 10 low 10 ms, high, 50 ms */
extern int32_t cy8c4046fni_read_version_55b6dc(uint32_t *version);  /* cmd 1, big-endian u32 */

extern int32_t osDelay(uint32_t ticks);                             /* 0x449376 */
extern void g2_delay_ms_4910f4(uint32_t ms);
extern void *file_open(const char *path, const char *mode);         /* 0x474550 */
extern int32_t file_close(void *file);                              /* 0x4745f4 */
extern uint32_t file_read(void *dst, uint32_t size, uint32_t count, void *file); /* 0x474634 */
extern int32_t file_seek(void *file, int32_t offset, int32_t whence); /* 0x474814 */
extern void *file_heap_allocate(uint32_t size);                     /* 0x474cd2 */
extern void file_heap_free(void *ptr);                              /* 0x474d16 */
extern int32_t g2_audio_dump_snprintf(char *buf, uint32_t size, const char *fmt, ...); /* 0x44b728 */
extern uint32_t audio_log_flags(void); /* 0x43d0ce */
extern void audio_log_extended(uint8_t, const char *, const char *, const char *, uint32_t, const char *, ...); /* 0x43d574 */
extern uint32_t compress_log_output(uint32_t, const char *, const char *, ...); /* 0x43ce9e */
extern void audio_uart_buffer_zero(void *dst, uint32_t len, uint32_t fill);      /* 0x43c0e4 */
extern void *audio_queue_copy_bytes(void *dst, const void *src, uint32_t len);   /* 0x439be4 memcpy */

/* CRC-32C (Castagnoli, reflected 0x82f63b78) nibble table. */
static const uint32_t crc32c_nibble_table[16] = { /* ROM 0x70f2a4 */
    0x00000000u, 0x105ec76fu, 0x20bd8edeu, 0x30e349b1u,
    0x417b1dbcu, 0x5125dad3u, 0x61c69362u, 0x7198540du,
    0x82f63b78u, 0x92a8fc17u, 0xa24bb5a6u, 0xb21572c9u,
    0xc38d26c4u, 0xd3d3e1abu, 0xe330a81au, 0xf36e6f75u,
};

static const char open_mode[] = "r+"; /* ROM 0x560a64 */

static const char module_tag[] = "drv.touchdfu"; /* ROM 0x788f30 */
static const char source_file[] = "D:\\01_workspace\\s200_ap510b_iar_git\\platform\\input\\touchDFU\\service_touch_dfu.c"; /* ROM 0x6efae8 */
static const char fn_enter_dfu[] = "TouchEnterDFU"; /* ROM 0x788f20 */
static const char fn_set_app_meta[] = "TouchSetAppMeta"; /* ROM 0x788f40 */
static const char fn_send_one_packet[] = "TouchSendOnePacket"; /* ROM 0x783668 */
static const char fn_program_data[] = "TouchProgramData"; /* ROM 0x78367c */
static const char fn_verify_app[] = "TouchVerifyApp"; /* ROM 0x788f50 */
static const char fn_exit_dfu[] = "TouchExitDFU"; /* ROM 0x788f70 */
static const char fn_send_app_file[] = "TouchSendAppFile"; /* ROM 0x783690 */
static const char fn_free_memory[] = "free_touch_firmware_memory"; /* ROM 0x7718a4 */
static const char fn_get_package_version[] = "get_touch_firmware_package_version"; /* ROM 0x759ec4 */
static const char fn_load_firmware[] = "load_touch_firmware_from_package"; /* ROM 0x759ee8 */
static const char fn_need_upgrade[] = "isTouchNeedUpgrade"; /* ROM 0x7836b8 */
static const char fn_update_check[] = "TouchUpdateFirmwareCheck"; /* ROM 0x7718f8 */
static const char firmware_path[] = "/firmware/touch.bin"; /* ROM 0x7836a4 */
static const char version_format[] = "%d.%d.%d.%d"; /* ROM 0x78c08c */

static const char enter_tx_error[] = "touch enter dfu error :%02X"; /* ROM 0x7717c4 */
static const char enter_tx_error_short[] = "[drv.touchdfu]touch enter dfu error :%02X"; /* ROM 0x74385c */
static const char enter_rx_error[] = "touch rx enter dfu error :%02X"; /* ROM 0x765330 */
static const char enter_rx_error_short[] = "[drv.touchdfu]touch rx enter dfu error :%02X"; /* ROM 0x7387a4 */
static const char enter_ok[] = "touch enter DFU OK :%02X"; /* ROM 0x7717e0 */
static const char enter_ok_short[] = "[drv.touchdfu]touch enter DFU OK :%02X"; /* ROM 0x74e3bc */
static const char meta_tx_error[] = "touch w meta error :%02X"; /* ROM 0x7717fc */
static const char meta_tx_error_short[] = "[drv.touchdfu]touch w meta error :%02X"; /* ROM 0x74e3e4 */
static const char meta_rx_error[] = "touch rx meta error :%02X"; /* ROM 0x771818 */
static const char meta_rx_error_short[] = "[drv.touchdfu]touch rx meta error :%02X"; /* ROM 0x74e40c */
static const char meta_ok[] = "touch set meta OK"; /* ROM 0x783654 */
static const char meta_ok_short[] = "[drv.touchdfu]touch set meta OK"; /* ROM 0x765350 */
static const char packet_too_long[] = "touch length too long :%d(%d)"; /* ROM 0x765370 */
static const char packet_too_long_short[] = "[drv.touchdfu]touch length too long :%d(%d)"; /* ROM 0x743888 */
static const char packet_tx_error[] = "touch w send one packet error :%02X"; /* ROM 0x759ea0 */
static const char packet_tx_error_short[] = "[drv.touchdfu]touch w send one packet error :%02X"; /* ROM 0x72d930 */
static const char packet_rx_error[] = "touch rx send one packet error :%02X"; /* ROM 0x74e434 */
static const char packet_rx_error_short[] = "[drv.touchdfu]touch rx send one packet error :%02X"; /* ROM 0x72d964 */
static const char program_tx_error[] = "touch w program error :%02X"; /* ROM 0x771834 */
static const char program_tx_error_short[] = "[drv.touchdfu]touch w program error :%02X"; /* ROM 0x7438b4 */
static const char program_rx_error[] = "touch rx program error :%02X"; /* ROM 0x765390 */
static const char program_rx_error_short[] = "[drv.touchdfu]touch rx program error :%02X"; /* ROM 0x7438e0 */
static const char verify_tx_error[] = "touch w verify error :%02X"; /* ROM 0x771850 */
static const char verify_tx_error_short[] = "[drv.touchdfu]touch w verify error :%02X"; /* ROM 0x74390c */
static const char verify_rx_error[] = "touch rx verify error :%02X"; /* ROM 0x77186c */
static const char verify_rx_error_short[] = "[drv.touchdfu]touch rx verify error :%02X"; /* ROM 0x743938 */
static const char verify_ok[] = "touch verify OK"; /* ROM 0x788f60 */
static const char verify_ok_short[] = "[drv.touchdfu]touch verify OK"; /* ROM 0x7653b0 */
static const char exit_tx_error[] = "touch w exit error :%02X"; /* ROM 0x771888 */
static const char exit_tx_error_short[] = "[drv.touchdfu]touch w exit error :%02X"; /* ROM 0x74e45c */
static const char exit_ok[] = "TouchExitDFU OK"; /* ROM 0x788f80 */
static const char exit_ok_short[] = "[drv.touchdfu]TouchExitDFU OK"; /* ROM 0x7653d0 */
static const char send_app_error[] = "touch TouchSendOnePacket error :%02X"; /* ROM 0x74e484 */
static const char send_app_error_short[] = "[drv.touchdfu]touch TouchSendOnePacket error :%02X"; /* ROM 0x72d998 */
static const char memory_freed[] = "Touch firmware memory freed"; /* ROM 0x7718c0 */
static const char memory_freed_short[] = "[drv.touchdfu]Touch firmware memory freed"; /* ROM 0x743964 */
static const char version_param_null[] = "Version parameter is null"; /* ROM 0x7718dc */
static const char version_param_null_short[] = "[drv.touchdfu]Version parameter is null"; /* ROM 0x74e4ac */
static const char get_version_from[] = "Get version number from Touch firmware package: %s"; /* ROM 0x72d9cc */
static const char get_version_from_short[] = "[drv.touchdfu]Get version number from Touch firmware package: %s"; /* ROM 0x705d54 */
static const char cannot_open[] = "Cannot open Touch firmware package file: %s"; /* ROM 0x743990 */
static const char cannot_open_short[] = "[drv.touchdfu]Cannot open Touch firmware package file: %s"; /* ROM 0x718874 */
static const char header_read_failed[] = "Failed to read Touch firmware package header: %zu"; /* ROM 0x72da00 */
static const char header_read_failed_short[] = "[drv.touchdfu]Failed to read Touch firmware package header: %zu"; /* ROM 0x70f1a4 */
static const char invalid_magic[] = "Invalid Touch firmware package magic: 0x%08X, expected: 0x%08X"; /* ROM 0x70f1e4 */
static const char invalid_magic_short[] = "[drv.touchdfu]Invalid Touch firmware package magic: 0x%08X, expected: 0x%08X"; /* ROM 0x6efb38 */
static const char package_version[] = "Touch firmware package version: 0x%08X"; /* ROM 0x74e4d4 */
static const char package_version_short[] = "[drv.touchdfu]Touch firmware package version: 0x%08X"; /* ROM 0x723070 */
static const char start_loading[] = "Start loading Touch firmware package from file system: %s"; /* ROM 0x7188b0 */
static const char start_loading_short[] = "[drv.touchdfu]Start loading Touch firmware package from file system: %s"; /* ROM 0x6fd19c */
static const char package_info[] = "Touch firmware package info: version=0x%08X, firmware count=%d"; /* ROM 0x70f224 */
static const char package_info_short[] = "[drv.touchdfu]Touch firmware package info: version=0x%08X, firmware count=%d"; /* ROM 0x6efb88 */
static const char record_read_failed[] = "Failed to read firmware info %d: %zu"; /* ROM 0x74e4fc */
static const char record_read_failed_short[] = "[drv.touchdfu]Failed to read firmware info %d: %zu"; /* ROM 0x72da34 */
static const char record_info[] = "Firmware %d: type=0x%02X, size=%d, offset=0x%08X, crc32=0x%08X"; /* ROM 0x70f264 */
static const char record_info_short[] = "[drv.touchdfu]Firmware %d: type=0x%02X, size=%d, offset=0x%08X, crc32=0x%08X"; /* ROM 0x6efbd8 */
static const char firmware_not_found[] = "Touch firmware not found in package"; /* ROM 0x759f0c */
static const char firmware_not_found_short[] = "[drv.touchdfu]Touch firmware not found in package"; /* ROM 0x72da68 */
static const char alloc_failed[] = "Failed to allocate memory for Touch firmware: %d bytes"; /* ROM 0x7230a8 */
static const char alloc_failed_short[] = "[drv.touchdfu]Failed to allocate memory for Touch firmware: %d bytes"; /* ROM 0x6fd1e4 */
static const char seek_failed[] = "Failed to seek to Touch firmware data: %d"; /* ROM 0x7439bc */
static const char seek_failed_short[] = "[drv.touchdfu]Failed to seek to Touch firmware data: %d"; /* ROM 0x7230e0 */
static const char data_read_failed[] = "Failed to read Touch firmware data: %zu/%d"; /* ROM 0x7439e8 */
static const char data_read_failed_short[] = "[drv.touchdfu]Failed to read Touch firmware data: %zu/%d"; /* ROM 0x7188ec */
static const char crc_mismatch[] = "Touch firmware CRC32 mismatch: calculated=0x%08X, expected=0x%08X"; /* ROM 0x705d98 */
static const char crc_mismatch_short[] = "[drv.touchdfu]Touch firmware CRC32 mismatch: calculated=0x%08X, expected=0x%08X"; /* ROM 0x6efc28 */
static const char loaded_ok[] = "Touch firmware loaded successfully: %d bytes (without checksum: %d bytes)"; /* ROM 0x6f6070 */
static const char loaded_ok_short[] = "[drv.touchdfu]Touch firmware loaded successfully: %d bytes (without checksum: %d bytes)"; /* ROM 0x6e50e8 */
static const char version_compare[] = "Touch version comparison: current=0x%08X, package=0x%08X"; /* ROM 0x718928 */
static const char version_compare_short[] = "[drv.touchdfu]Touch version comparison: current=0x%08X, package=0x%08X"; /* ROM 0x6fd22c */
static const char version_same[] = "Touch firmware is the same, no upgrade needed"; /* ROM 0x7387d4 */
static const char version_same_short[] = "[drv.touchdfu]Touch firmware is the same, no upgrade needed"; /* ROM 0x718964 */
static const char upgrade_needed[] = "Touch firmware upgrade needed: %d.%d.%d.%d -> %d.%d.%d.%d"; /* ROM 0x7189a0 */
static const char upgrade_needed_short[] = "[drv.touchdfu]Touch firmware upgrade needed: %d.%d.%d.%d -> %d.%d.%d.%d"; /* ROM 0x6fd274 */
static const char mode_filesystem[] = "Touch firmware upgrade mode: Filesystem"; /* ROM 0x74e524 */
static const char mode_filesystem_short[] = "[drv.touchdfu]Touch firmware upgrade mode: Filesystem"; /* ROM 0x723118 */
static const char current_version_failed[] = "Failed to get current Touch version: %d, go force upgrade"; /* ROM 0x7189dc */
static const char current_version_failed_short[] = "[drv.touchdfu]Failed to get current Touch version: %d, go force upgrade"; /* ROM 0x6fd2bc */
static const char current_version[] = "Current Touch version: %s (0x%08X)"; /* ROM 0x759f30 */
static const char current_version_short[] = "[drv.touchdfu]Current Touch version: %s (0x%08X)"; /* ROM 0x72da9c */
static const char package_version_failed[] = "Failed to get package Touch version: %d"; /* ROM 0x74e54c */
static const char package_version_failed_short[] = "[drv.touchdfu]Failed to get package Touch version: %d"; /* ROM 0x723150 */
static const char package_version_str[] = "Package Touch version: %s (0x%08X)"; /* ROM 0x759f54 */
static const char package_version_str_short[] = "[drv.touchdfu]Package Touch version: %s (0x%08X)"; /* ROM 0x72dad0 */
static const char check_passed[] = "Touch firmware version check passed, no upgrade needed"; /* ROM 0x723188 */
static const char check_passed_short[] = "[drv.touchdfu]Touch firmware version check passed, no upgrade needed"; /* ROM 0x6fd304 */
static const char force_mode[] = "Force upgrade mode, skipping version check"; /* ROM 0x743a14 */
static const char force_mode_short[] = "[drv.touchdfu]Force upgrade mode, skipping version check"; /* ROM 0x718a18 */
static const char load_failed[] = "Failed to load Touch firmware package: %d"; /* ROM 0x743a40 */
static const char load_failed_short[] = "[drv.touchdfu]Failed to load Touch firmware package: %d"; /* ROM 0x7231c0 */
static const char switch_failed[] = "Failed to switch Touch to DFU mode: %d"; /* ROM 0x74e574 */
static const char switch_failed_short[] = "[drv.touchdfu]Failed to switch Touch to DFU mode: %d"; /* ROM 0x7231f8 */
static const char update_enter_error[] = "TouchEnterDFU error :%02X"; /* ROM 0x771914 */
static const char update_enter_error_short[] = "[drv.touchdfu]TouchEnterDFU error :%02X"; /* ROM 0x74e59c */
static const char update_enter_ok[] = "TouchEnterDFU OK"; /* ROM 0x7836cc */
static const char update_enter_ok_short[] = "[drv.touchdfu]TouchEnterDFU OK"; /* ROM 0x7653f0 */
static const char update_meta_error[] = "TouchSetAppMeta error :%02X"; /* ROM 0x771930 */
static const char update_meta_error_short[] = "[drv.touchdfu]TouchSetAppMeta error :%02X"; /* ROM 0x743a6c */
static const char update_meta_ok[] = "TouchSetAppMeta OK"; /* ROM 0x7836e0 */
static const char update_meta_ok_short[] = "[drv.touchdfu]TouchSetAppMeta OK"; /* ROM 0x759f78 */
static const char update_send_error[] = "TouchSendAppFile error :%02X"; /* ROM 0x765410 */
static const char update_send_error_short[] = "[drv.touchdfu]TouchSendAppFile error :%02X"; /* ROM 0x743a98 */
static const char update_send_ok[] = "TouchSendAppFile OK"; /* ROM 0x7836f4 */
static const char update_send_ok_short[] = "[drv.touchdfu]TouchSendAppFile OK"; /* ROM 0x759f9c */
static const char update_verify_error[] = "TouchVerifyApp error :%02X"; /* ROM 0x77194c */
static const char update_verify_error_short[] = "[drv.touchdfu]TouchVerifyApp error :%02X"; /* ROM 0x743ac4 */
static const char update_verify_ok[] = "TouchVerifyApp OK"; /* ROM 0x783708 */
static const char update_verify_ok_short[] = "[drv.touchdfu]TouchVerifyApp OK"; /* ROM 0x765430 */
static const char update_exit_error[] = "TouchExitDFU error :%02X"; /* ROM 0x771968 */
static const char update_exit_error_short[] = "[drv.touchdfu]TouchExitDFU error :%02X"; /* ROM 0x74e5c4 */
static const char update_ok[] = "TouchUpdateFirmware OK!!!"; /* ROM 0x771984 */
static const char update_ok_short[] = "[drv.touchdfu]TouchUpdateFirmware OK!!!"; /* ROM 0x74e5ec */

/* Stock logging pattern: extended record when flag bit 1 is set, compressed
 * record when bit 0 or bit 2 is set. The compressed mask is
 * (level << 26) | (argument count << 22). */
#define LOG_MASK(level, nargs) (((uint32_t)(level) << 26) | ((uint32_t)(nargs) << 22))
#define DFU_LOG(level, nargs, line, fn, msg, msg_short, ...)                            \
    do {                                                                                \
        if (audio_log_flags() & 2u)                                                     \
            audio_log_extended((level), module_tag, source_file, (fn), (line), (msg),   \
                               ##__VA_ARGS__);                                          \
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))                       \
            (void)compress_log_output(LOG_MASK(level, nargs), (msg_short), (msg_short), \
                                      ##__VA_ARGS__);                                   \
    } while (0)

/* ---- frame accessors (0x55fcb4..0x55fd75) ---- */

uint16_t semantic_TouchFrameReadU16(const void *src)
{
    uint16_t value;

    (void)audio_queue_copy_bytes(&value, src, 2u);
    return value;
}

void semantic_TouchFrameWriteU16(uint8_t *frame, uint32_t offset, uint16_t value)
{
    (void)audio_queue_copy_bytes(frame + offset, &value, 2u);
}

/* Offset of the checksum that follows payload_len payload bytes. */
uint32_t semantic_TouchFramePayload(uint32_t payload_len)
{
    return payload_len + DFU_HEADER_LEN;
}

/* Offset of the end byte that follows payload_len payload bytes. */
uint32_t semantic_TouchFrameTerminator(uint32_t payload_len)
{
    return payload_len + DFU_HEADER_LEN + 2u;
}

uint8_t semantic_TouchFrameCommand(const uint8_t *frame)
{
    return frame[1];
}

uint16_t semantic_TouchFramePayloadLength(const uint8_t *frame)
{
    return semantic_TouchFrameReadU16(frame + 2);
}

uint16_t semantic_TouchFrameChecksum(const uint8_t *frame, uint32_t payload_len)
{
    return semantic_TouchFrameReadU16(frame + semantic_TouchFramePayload(payload_len));
}

bool semantic_TouchFrameHasTerminator(const uint8_t *frame, uint32_t payload_len)
{
    return frame[semantic_TouchFrameTerminator(payload_len)] == DFU_EOP;
}

void semantic_TouchFrameInit(uint8_t *frame)
{
    frame[0] = DFU_SOP;
}

void semantic_TouchFrameSetCommand(uint8_t *frame, uint8_t cmd)
{
    frame[1] = cmd;
}

void semantic_TouchFrameSetPayloadLength(uint8_t *frame, uint16_t payload_len)
{
    semantic_TouchFrameWriteU16(frame, 2u, payload_len);
}

void semantic_TouchFrameSetChecksum(uint8_t *frame, uint32_t payload_len, uint16_t checksum)
{
    semantic_TouchFrameWriteU16(frame, semantic_TouchFramePayload(payload_len), checksum);
}

void semantic_TouchFrameSetTerminator(uint8_t *frame, uint32_t payload_len)
{
    frame[semantic_TouchFrameTerminator(payload_len)] = DFU_EOP;
}

/* cy_dfu packet checksum: two's complement of the byte sum over the 4-byte
 * header and the payload, summed from the last byte down. */
uint16_t semantic_TouchFrameChecksum16(const uint8_t *frame, uint32_t payload_len)
{
    uint16_t sum = 0;
    uint32_t n = payload_len + DFU_HEADER_LEN;

    while (n != 0u) {
        n--;
        sum = (uint16_t)(sum + frame[n]);
    }
    return (uint16_t)(~sum + 1u);
}

/* Returns the reply status byte with *ok = 1 for a well-formed frame,
 * otherwise a host error code with *ok = 0. */
uint8_t semantic_TouchValidateReply(uint8_t reply_len, const uint8_t *reply, uint8_t *ok)
{
    uint32_t payload_len;

    *ok = 0;
    if (reply_len < DFU_OVERHEAD || reply[0] != DFU_SOP) {
        *ok = 0;
        return DFU_ERROR_FRAME;
    }
    payload_len = semantic_TouchFramePayloadLength(reply);
    if (reply_len < payload_len + DFU_OVERHEAD || payload_len + DFU_OVERHEAD >= 16u) {
        *ok = 0;
        return DFU_ERROR_LENGTH;
    }
    if (!semantic_TouchFrameHasTerminator(reply, payload_len)) {
        *ok = 0;
        return DFU_ERROR_DATA;
    }
    if (semantic_TouchFrameChecksum(reply, payload_len) !=
        semantic_TouchFrameChecksum16(reply, payload_len)) {
        *ok = 0;
        return DFU_ERROR_CHECKSUM;
    }
    *ok = 1;
    return semantic_TouchFrameCommand(reply);
}

/* Poll for a reply: up to 100 raw reads, 1 ms apart. Returns the reply
 * status (0 = success) or the last transport/validation error. */
uint32_t semantic_TouchSendCommandRetry(const g2_touch_ops_t *ops, uint8_t *reply, uint8_t len)
{
    uint8_t ok = 0;
    uint8_t tries = DFU_REPLY_TRIES;
    uint32_t ret;

    do {
        g2_delay_ms_4910f4(1u);
        ret = ops->read(reply, len);
        if (ret == 0u) {
            ret = semantic_TouchValidateReply(len, reply, &ok);
            if (ok != 0u)
                break;
        }
    } while (--tries != 0u);
    return ret;
}

/* CRC-32C, init and final XOR 0xffffffff, one nibble per table step. */
uint32_t semantic_TouchCrc32(const uint8_t *data, uint32_t len)
{
    uint32_t crc = 0xffffffffu;

    for (; len != 0u; len--) {
        crc ^= *data++;
        crc = crc32c_nibble_table[crc & 0xfu] ^ (crc >> 4);
        crc = crc32c_nibble_table[crc & 0xfu] ^ (crc >> 4);
    }
    return ~crc;
}

uint32_t semantic_TouchBuildAndSendFrame(const g2_touch_ops_t *ops, uint8_t cmd,
                                         const void *payload, uint16_t payload_len)
{
    uint8_t frame[40];

    semantic_TouchFrameInit(frame);
    semantic_TouchFrameSetCommand(frame, cmd);
    semantic_TouchFrameSetPayloadLength(frame, payload_len);
    if (payload != NULL && payload_len != 0u)
        (void)audio_queue_copy_bytes(frame + DFU_HEADER_LEN, payload, payload_len);
    semantic_TouchFrameSetChecksum(frame, payload_len,
                                   semantic_TouchFrameChecksum16(frame, payload_len));
    semantic_TouchFrameSetTerminator(frame, payload_len);
    return ops->write(frame, (uint16_t)(payload_len + DFU_OVERHEAD));
}

/* ---- bootloader commands (0x55fed6..0x5604c7) ---- */

int32_t TouchEnterDFU(void)
{
    const g2_touch_ops_t *ops = &g2_touch_ops;
    uint8_t product_id[4] = { 0x04u, 0x03u, 0x02u, 0x01u }; /* ROM 0x78f3ec: 0x01020304 */
    uint8_t reply[16];
    int32_t ret;

    ret = (int32_t)semantic_TouchBuildAndSendFrame(ops, DFU_CMD_ENTER, product_id, 4u);
    if (ret != 0) {
        DFU_LOG(1u, 1u, 0x1edu, fn_enter_dfu, enter_tx_error, enter_tx_error_short, ret);
        return ret;
    }
    ret = (int32_t)semantic_TouchSendCommandRetry(ops, reply, DFU_REPLY_LEN);
    if (ret != 0)
        DFU_LOG(1u, 1u, 0x1f3u, fn_enter_dfu, enter_rx_error, enter_rx_error_short, ret);
    else
        DFU_LOG(4u, 1u, 0x1f5u, fn_enter_dfu, enter_ok, enter_ok_short, ret);
    return ret;
}

int32_t TouchSetAppMeta(uint32_t length)
{
    const g2_touch_ops_t *ops = &g2_touch_ops;
    g2_touch_app_meta_t meta = { TOUCH_APP_ID, TOUCH_APP_START, 0u, { 0u, 0u, 0u } };
    uint8_t reply[16];
    int32_t ret;

    meta.length = length;
    ret = (int32_t)semantic_TouchBuildAndSendFrame(ops, DFU_CMD_SET_APP_META, &meta, 9u);
    if (ret != 0) {
        DFU_LOG(1u, 1u, 0x207u, fn_set_app_meta, meta_tx_error, meta_tx_error_short, ret);
        return ret;
    }
    ret = (int32_t)semantic_TouchSendCommandRetry(ops, reply, DFU_REPLY_LEN);
    if (ret != 0)
        DFU_LOG(1u, 1u, 0x20du, fn_set_app_meta, meta_rx_error, meta_rx_error_short, ret);
    else
        DFU_LOG(4u, 0u, 0x20fu, fn_set_app_meta, meta_ok, meta_ok_short);
    return ret;
}

int32_t TouchSendOnePacket(const void *data, uint16_t len)
{
    const g2_touch_ops_t *ops = &g2_touch_ops;
    uint8_t reply[16];
    int32_t ret;

    if (len > DFU_MAX_PACKET_DATA) {
        DFU_LOG(1u, 2u, 0x21cu, fn_send_one_packet, packet_too_long, packet_too_long_short,
                len, DFU_MAX_PACKET_DATA);
        return DFU_ERROR_LENGTH;
    }
    ret = (int32_t)semantic_TouchBuildAndSendFrame(ops, DFU_CMD_SEND_DATA, data, len);
    if (ret != 0) {
        DFU_LOG(1u, 1u, 0x221u, fn_send_one_packet, packet_tx_error, packet_tx_error_short, ret);
        return ret;
    }
    ret = (int32_t)semantic_TouchSendCommandRetry(ops, reply, DFU_REPLY_LEN);
    if (ret != 0)
        DFU_LOG(1u, 1u, 0x228u, fn_send_one_packet, packet_rx_error, packet_rx_error_short, ret);
    return ret;
}

/* Program the row just streamed with send-data packets; offset is relative
 * to the application start. */
int32_t TouchProgramData(uint32_t offset, uint32_t crc32c)
{
    const g2_touch_ops_t *ops = &g2_touch_ops;
    g2_touch_program_data_t cmd = { offset + TOUCH_APP_START, crc32c };
    uint8_t reply[16];
    int32_t ret;

    ret = (int32_t)semantic_TouchBuildAndSendFrame(ops, DFU_CMD_PROGRAM_DATA, &cmd, 8u);
    if (ret != 0) {
        DFU_LOG(1u, 1u, 0x237u, fn_program_data, program_tx_error, program_tx_error_short, ret);
        return ret;
    }
    ret = (int32_t)semantic_TouchSendCommandRetry(ops, reply, DFU_REPLY_LEN);
    if (ret != 0)
        DFU_LOG(1u, 1u, 0x23du, fn_program_data, program_rx_error, program_rx_error_short, ret);
    return ret;
}

int32_t TouchVerifyApp(void)
{
    const g2_touch_ops_t *ops = &g2_touch_ops;
    uint8_t app = TOUCH_APP_ID;
    uint8_t reply[16];
    int32_t ret;

    ret = (int32_t)semantic_TouchBuildAndSendFrame(ops, DFU_CMD_VERIFY_APP, &app, 1u);
    if (ret != 0) {
        DFU_LOG(1u, 1u, 0x249u, fn_verify_app, verify_tx_error, verify_tx_error_short, ret);
        return ret;
    }
    ret = (int32_t)semantic_TouchSendCommandRetry(ops, reply, DFU_REPLY_LEN);
    if (ret != 0)
        DFU_LOG(1u, 1u, 0x24fu, fn_verify_app, verify_rx_error, verify_rx_error_short, ret);
    else
        DFU_LOG(4u, 0u, 0x251u, fn_verify_app, verify_ok, verify_ok_short);
    return ret;
}

/* The bootloader starts the application without replying. */
int32_t TouchExitDFU(void)
{
    int32_t ret = (int32_t)semantic_TouchBuildAndSendFrame(&g2_touch_ops, DFU_CMD_EXIT, NULL, 0u);

    if (ret != 0)
        DFU_LOG(1u, 1u, 0x25du, fn_exit_dfu, exit_tx_error, exit_tx_error_short, ret);
    else
        DFU_LOG(4u, 0u, 0x25fu, fn_exit_dfu, exit_ok, exit_ok_short);
    return ret;
}

/* Stream the image in 32-byte send-data packets and program every 128-byte
 * row with its CRC-32C. The length is rounded up to whole rows and each
 * packet copies a full 32 bytes from the image, so the last row carries
 * whatever follows the image in the heap buffer (the 4-byte trailer and
 * beyond). Returns 15 (cy_dfu unknown error) for an empty image. */
int32_t TouchSendAppFile(const uint8_t *image, int32_t length)
{
    uint8_t row[DFU_ROW_SIZE];
    int32_t ret = DFU_ERROR_UNKNOWN;
    uint16_t rows_done = 0;
    uint16_t slot = 0;
    uint32_t remaining = (uint32_t)((length + (int32_t)DFU_ROW_SIZE - 1) / (int32_t)DFU_ROW_SIZE) * DFU_ROW_SIZE;
    uint32_t last = remaining / DFU_MAX_PACKET_DATA - 1u;

    audio_uart_buffer_zero(row, DFU_ROW_SIZE, 0xffu);
    for (int16_t left = (int16_t)last; left >= 0; left--) {
        uint32_t chunk = remaining < DFU_MAX_PACKET_DATA ? remaining : DFU_MAX_PACKET_DATA;

        (void)audio_queue_copy_bytes(row + slot * DFU_MAX_PACKET_DATA,
                                     image + ((uint16_t)last - left) * DFU_MAX_PACKET_DATA,
                                     (uint16_t)chunk);
        ret = TouchSendOnePacket(row + slot * DFU_MAX_PACKET_DATA, DFU_MAX_PACKET_DATA);
        if (ret != 0) {
            DFU_LOG(1u, 1u, 0x27eu, fn_send_app_file, send_app_error, send_app_error_short, ret);
            return ret;
        }
        remaining -= (uint16_t)chunk;
        slot++;
        if (slot >= DFU_PACKETS_PER_ROW) {
            uint32_t crc = semantic_TouchCrc32(row, (uint32_t)slot * DFU_MAX_PACKET_DATA);

            ret = TouchProgramData((uint32_t)slot * rows_done * DFU_MAX_PACKET_DATA, crc);
            if (ret != 0) {
                /* Stock reuses the send-one-packet message here. */
                DFU_LOG(1u, 1u, 0x28au, fn_send_app_file, send_app_error, send_app_error_short,
                        ret);
                return ret;
            }
            slot = 0;
            rows_done++;
            audio_uart_buffer_zero(row, DFU_ROW_SIZE, 0xffu);
        }
        ret = 0;
    }
    return ret;
}

/* ---- firmware package (0x56063a..0x560ea1) ---- */

void free_touch_firmware_memory(void)
{
    if (g2_touch_fw_image == NULL)
        return;
    file_heap_free(g2_touch_fw_image);
    g2_touch_fw_image = NULL;
    g2_touch_fw_image_length = 0u;
    DFU_LOG(4u, 0u, 0x2b3u, fn_free_memory, memory_freed, memory_freed_short);
}

int32_t get_touch_firmware_package_version(uint32_t *version)
{
    g2_fwpk_header_t header;
    void *file;
    uint32_t n;

    if (version == NULL) {
        DFU_LOG(1u, 0u, 0x2bdu, fn_get_package_version, version_param_null,
                version_param_null_short);
        return -1;
    }
    DFU_LOG(4u, 1u, 0x2c1u, fn_get_package_version, get_version_from, get_version_from_short,
            firmware_path);
    file = file_open(firmware_path, open_mode);
    if (file == NULL) {
        DFU_LOG(1u, 1u, 0x2c7u, fn_get_package_version, cannot_open, cannot_open_short,
                firmware_path);
        return -1;
    }
    n = file_read(&header, 1u, sizeof(header), file);
    if (n != sizeof(header)) {
        DFU_LOG(1u, 1u, 0x2ceu, fn_get_package_version, header_read_failed,
                header_read_failed_short, n);
        if (file != NULL) {
            (void)file_close(file);
            file = NULL;
        }
        return -1;
    }
    if (file != NULL) {
        (void)file_close(file);
        file = NULL;
    }
    if (header.magic != FWPK_MAGIC) {
        DFU_LOG(1u, 2u, 0x2d7u, fn_get_package_version, invalid_magic, invalid_magic_short,
                header.magic, FWPK_MAGIC);
        return -1;
    }
    *version = header.version;
    DFU_LOG(4u, 1u, 0x2dcu, fn_get_package_version, package_version, package_version_short,
            *version);
    return 0;
}

/* Expanded inline at every exit in the stock code (no helper function). */
#define CLOSE_PACKAGE_FILE()                                  \
    do {                                                      \
        if (g2_touch_fw_package_file != NULL) {               \
            (void)file_close(g2_touch_fw_package_file);       \
            g2_touch_fw_package_file = NULL;                  \
        }                                                     \
    } while (0)

/* Load the type-3 record of /firmware/touch.bin into a file-heap buffer and
 * check its CRC-32C; on success g2_touch_fw_image_length = size - 4. */
int32_t load_touch_firmware_from_package(void)
{
    g2_fwpk_record_t record;
    g2_fwpk_header_t header;
    bool found = false;
    uint32_t n;
    int32_t ret;

    audio_uart_buffer_zero(&record, sizeof(record), 0u);
    DFU_LOG(4u, 1u, 0x2e9u, fn_load_firmware, start_loading, start_loading_short, firmware_path);
    g2_touch_fw_package_file = file_open(firmware_path, open_mode);
    if (g2_touch_fw_package_file == NULL) {
        DFU_LOG(1u, 1u, 0x2eeu, fn_load_firmware, cannot_open, cannot_open_short, firmware_path);
        return -1;
    }
    n = file_read(&header, 1u, sizeof(header), g2_touch_fw_package_file);
    if (n != sizeof(header)) {
        DFU_LOG(1u, 1u, 0x2f5u, fn_load_firmware, header_read_failed, header_read_failed_short, n);
        CLOSE_PACKAGE_FILE();
        return -1;
    }
    if (header.magic != FWPK_MAGIC) {
        DFU_LOG(1u, 2u, 0x2fcu, fn_load_firmware, invalid_magic, invalid_magic_short,
                header.magic, FWPK_MAGIC);
        CLOSE_PACKAGE_FILE();
        return -1;
    }
    DFU_LOG(4u, 2u, 0x301u, fn_load_firmware, package_info, package_info_short,
            header.version, header.count);
    for (uint32_t i = 0; i < header.count; i++) {
        n = file_read(&record, 1u, sizeof(record), g2_touch_fw_package_file);
        if (n != sizeof(record)) {
            DFU_LOG(1u, 2u, 0x307u, fn_load_firmware, record_read_failed,
                    record_read_failed_short, i, n);
            CLOSE_PACKAGE_FILE();
            return -1;
        }
        DFU_LOG(4u, 5u, 0x30du, fn_load_firmware, record_info, record_info_short,
                i, record.type, record.size, record.offset, record.crc32);
        if (record.type == FWPK_TYPE_TOUCH) {
            found = true;
            break;
        }
    }
    if (!found) {
        DFU_LOG(1u, 0u, 0x316u, fn_load_firmware, firmware_not_found, firmware_not_found_short);
        CLOSE_PACKAGE_FILE();
        return -1;
    }
    g2_touch_fw_image = file_heap_allocate(record.size);
    if (g2_touch_fw_image == NULL) {
        DFU_LOG(1u, 1u, 0x31eu, fn_load_firmware, alloc_failed, alloc_failed_short, record.size);
        CLOSE_PACKAGE_FILE();
        return -1;
    }
    ret = file_seek(g2_touch_fw_package_file, (int32_t)record.offset, 0);
    if (ret != 0) {
        DFU_LOG(1u, 1u, 0x326u, fn_load_firmware, seek_failed, seek_failed_short, ret);
        free_touch_firmware_memory();
        CLOSE_PACKAGE_FILE();
        return -1;
    }
    n = file_read(g2_touch_fw_image, 1u, record.size, g2_touch_fw_package_file);
    if (n != record.size) {
        DFU_LOG(1u, 2u, 0x32fu, fn_load_firmware, data_read_failed, data_read_failed_short,
                n, record.size);
        free_touch_firmware_memory();
        CLOSE_PACKAGE_FILE();
        return -1;
    }
    CLOSE_PACKAGE_FILE();
    n = semantic_TouchCrc32(g2_touch_fw_image, record.size);
    if (n != record.crc32) {
        DFU_LOG(1u, 2u, 0x33bu, fn_load_firmware, crc_mismatch, crc_mismatch_short,
                n, record.crc32);
        free_touch_firmware_memory();
        return -1;
    }
    g2_touch_fw_image_length = record.size - 4u;
    DFU_LOG(4u, 2u, 0x342u, fn_load_firmware, loaded_ok, loaded_ok_short,
            record.size, g2_touch_fw_image_length);
    return 0;
}

/* ---- version check and update flow (0x560ea8..0x56170f) ---- */

void semantic_TouchFormatVersion(uint32_t version, char *buf, uint32_t size)
{
    (void)g2_audio_dump_snprintf(buf, size, version_format,
                                 (uint8_t)(version >> 24), (uint8_t)(version >> 16),
                                 (uint8_t)(version >> 8), (uint8_t)version);
}

uint32_t isTouchNeedUpgrade(uint32_t current, uint32_t package)
{
    DFU_LOG(3u, 2u, 0x354u, fn_need_upgrade, version_compare, version_compare_short,
            current, package);
    if (current == package) {
        DFU_LOG(3u, 0u, 0x357u, fn_need_upgrade, version_same, version_same_short);
        return 0u;
    }
    DFU_LOG(3u, 8u, 0x35fu, fn_need_upgrade, upgrade_needed, upgrade_needed_short,
            current >> 24, (current & 0xffffffu) >> 16, (current & 0xffffu) >> 8, current & 0xffu,
            package >> 24, (package & 0xffffffu) >> 16, (package & 0xffffu) >> 8, package & 0xffu);
    return 1u;
}

/* Reset the controller, read its version and format it into the shared
 * version string (used by the AT/info paths). */
const char *semantic_TouchLogCurrentVersion(void)
{
    uint32_t version = 0;

    cy8c4046fni_reset_55b64a();
    (void)cy8c4046fni_read_version_55b6dc(&version);
    (void)g2_audio_dump_snprintf(g2_touch_version_string, sizeof(g2_touch_version_string),
                                 version_format, version >> 24, (version >> 16) & 0xffu,
                                 (version >> 8) & 0xffu, version & 0xffu);
    return g2_touch_version_string;
}

/* Compare the running touch firmware with /firmware/touch.bin and, when they
 * differ (or force is set, or the running version cannot be read), program
 * the package image through the resident bootloader. */
void TouchUpdateFirmwareCheck(uint8_t force)
{
    uint32_t current = 0;
    uint32_t package = 0;
    char package_str[32];
    char current_str[32];
    uint8_t *image;
    uint32_t image_length;
    int32_t ret;

    audio_uart_buffer_zero(package_str, sizeof(package_str), 0u);
    audio_uart_buffer_zero(current_str, sizeof(current_str), 0u);
    DFU_LOG(3u, 0u, 0x377u, fn_update_check, mode_filesystem, mode_filesystem_short);

    cy8c4046fni_reset_55b64a();
    ret = cy8c4046fni_read_version_55b6dc(&current);
    if (ret != 0) {
        DFU_LOG(1u, 1u, 0x37eu, fn_update_check, current_version_failed,
                current_version_failed_short, ret);
        force = 1u;
    }
    semantic_TouchFormatVersion(current, current_str, sizeof(current_str));
    DFU_LOG(3u, 2u, 0x382u, fn_update_check, current_version, current_version_short,
            current_str, current);

    ret = get_touch_firmware_package_version(&package);
    if (ret != 0) {
        DFU_LOG(1u, 1u, 0x387u, fn_update_check, package_version_failed,
                package_version_failed_short, ret);
        return;
    }
    semantic_TouchFormatVersion(package, package_str, sizeof(package_str));
    DFU_LOG(3u, 2u, 0x38bu, fn_update_check, package_version_str, package_version_str_short,
            package_str, package);

    if (force == 0u) {
        if (isTouchNeedUpgrade(current, package) == 0u) {
            DFU_LOG(3u, 0u, 0x390u, fn_update_check, check_passed, check_passed_short);
            return;
        }
    } else {
        DFU_LOG(3u, 0u, 0x394u, fn_update_check, force_mode, force_mode_short);
    }

    ret = load_touch_firmware_from_package();
    if (ret != 0) {
        DFU_LOG(1u, 1u, 0x39au, fn_update_check, load_failed, load_failed_short, ret);
        return;
    }
    image = g2_touch_fw_image;
    image_length = g2_touch_fw_image_length;

    ret = DRV_TouchSwitch2Dfu_55b5e4();
    if (ret != 0) {
        DFU_LOG(1u, 1u, 0x3a5u, fn_update_check, switch_failed, switch_failed_short, ret);
        free_touch_firmware_memory();
        return;
    }
    (void)osDelay(50u);

    ret = TouchEnterDFU();
    if (ret != 0) {
        DFU_LOG(1u, 1u, 0x3adu, fn_update_check, update_enter_error, update_enter_error_short, ret);
        free_touch_firmware_memory();
        return;
    }
    DFU_LOG(3u, 0u, 0x3b1u, fn_update_check, update_enter_ok, update_enter_ok_short);

    ret = TouchSetAppMeta(image_length);
    if (ret != 0) {
        DFU_LOG(1u, 1u, 0x3b7u, fn_update_check, update_meta_error, update_meta_error_short, ret);
        free_touch_firmware_memory();
        return;
    }
    DFU_LOG(3u, 0u, 0x3bbu, fn_update_check, update_meta_ok, update_meta_ok_short);

    ret = TouchSendAppFile(image, (int32_t)image_length);
    if (ret != 0) {
        DFU_LOG(1u, 1u, 0x3c1u, fn_update_check, update_send_error, update_send_error_short, ret);
        free_touch_firmware_memory();
        return;
    }
    DFU_LOG(3u, 0u, 0x3c5u, fn_update_check, update_send_ok, update_send_ok_short);

    ret = TouchVerifyApp();
    if (ret != 0) {
        DFU_LOG(1u, 1u, 0x3cbu, fn_update_check, update_verify_error, update_verify_error_short,
                ret);
        free_touch_firmware_memory();
        return;
    }
    DFU_LOG(3u, 0u, 0x3cfu, fn_update_check, update_verify_ok, update_verify_ok_short);

    ret = TouchExitDFU();
    if (ret != 0) {
        DFU_LOG(1u, 1u, 0x3d5u, fn_update_check, update_exit_error, update_exit_error_short, ret);
        free_touch_firmware_memory();
        return;
    }
    DFU_LOG(3u, 0u, 0x3d9u, fn_update_check, update_ok, update_ok_short);
    (void)osDelay(500u);
    {
        uint32_t reread = 0; /* result unused by the stock code */
        (void)cy8c4046fni_read_version_55b6dc(&reread);
    }
    free_touch_firmware_memory();
}
