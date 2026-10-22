/* GX8002 voice-codec firmware update from the Apollo side, stock
 * D:\01_workspace\s200_ap510b_iar_git\platform\audio\service_codec_dfu.c
 * (module tag "codec.dfu"). Native 0x577d7c..0x57a35f; literal pools
 * 0x5787d4..0x57880f, 0x578a88..0x578aab, 0x578c4c..0x578ca3,
 * 0x579124..0x57919f, 0x57963c..0x5796c7, 0x5799e4, 0x579c6c..0x579cbb,
 * 0x579f50..0x579fb7, 0x57a360..0x57a46b.
 *
 * Package: /firmware/codec.bin, a 16-byte "FWPK" header followed by 16-byte
 * <type, size, offset, crc32> records (type 1 = UART boot container, type 2 =
 * flash image); both payloads are read into file-heap buffers and checked
 * against the record's zlib CRC-32.
 *
 * Wire protocol on UART3 (all token waits fold CR to LF and restart the match
 * on the first mismatching byte):
 *   230400 baud: reboot codec, send 0xEF until the boot ROM answers 'M'
 *   stage 1:  'Y' + stage1 word count (LE u32), stage-1 body in 256-byte
 *             writes, wait "F", wait "wfb", send "OK", send stage-2 baud
 *             (LE u32, Apollo always sends 1000000, not the header value),
 *             wait "OK", switch Apollo UART to that baud, wait "GET", send "OK"
 *   stage 2:  'S' + checksum (LE u32) + size (LE u32), wait "ready", stage-2
 *             body in 256-byte writes, wait "O", wait "boot>"
 *   flash:    "serialdown 0 <size> 8192\n" + table CRC-32 of the flash image
 *             (LE u32), wait "~sta~" (9000000 ticks), then per 8192-byte
 *             chunk: send, wait "~fin~", and "~sta~" while data remains;
 *             finally wait "[Result]:" (3000) and "SUCC" (2000).
 * Every other wait uses 10000 ticks. */
#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>
#include "../gx8002-host/gx8002_host.h"

#define CODEC_FWPK_MAGIC 0x4b505746u /* "FWPK" little-endian, ROM 0x578804 */
#define CODEC_FW_TYPE_BOOT 1u
#define CODEC_FW_TYPE_FLASH 2u
#define CODEC_BOOT_HEADER_SIZE 0x20u
#define CODEC_STAGE1_BAUD 230400u
#define CODEC_STAGE2_BAUD 1000000u        /* ROM 0x57a3c4 */
#define CODEC_TOKEN_TIMEOUT 10000
#define CODEC_FLASH_START_TIMEOUT 9000000 /* ROM 0x57a36c */
#define CODEC_BOOT_CHUNK 0x100u
#define CODEC_FLASH_CHUNK 0x2000
#define CODEC_SYNC_ATTEMPTS 10000

/* FWPK package header (file offset 0). */
typedef struct {
    uint32_t magic;   /* +0x0 "FWPK" */
    uint32_t version; /* +0x4 e.g. 0x00000203 = 0.0.2.3 */
    uint32_t count;   /* +0x8 firmware records */
    uint32_t reserved;/* +0xc */
} g2_codec_package_header_t;
_Static_assert(sizeof(g2_codec_package_header_t) == 16u, "FWPK header");

/* FWPK firmware record. */
typedef struct {
    uint32_t type;   /* +0x0 1 boot container, 2 flash image */
    uint32_t size;   /* +0x4 */
    uint32_t offset; /* +0x8 file offset */
    uint32_t crc32;  /* +0xc zlib CRC-32 of the payload */
} g2_codec_firmware_info_t;
_Static_assert(sizeof(g2_codec_firmware_info_t) == 16u, "FWPK record");

/* NationalChip grus UART boot header (first 32 bytes of the boot container;
 * the four u32 fields are big-endian in the file and swapped in place). */
typedef struct {
    uint16_t chip_id;          /* +0x00 0x8002 */
    uint8_t chip_type;         /* +0x02 1 => stage-1 count is sent in words, body in bytes */
    uint8_t chip_version;      /* +0x03 */
    uint16_t boot_delay;       /* +0x04 */
    uint8_t baud_rate;         /* +0x06 */
    uint8_t reserved_1;        /* +0x07 */
    int32_t stage1_size;       /* +0x08 */
    int32_t stage2_baud_rate;  /* +0x0c printed only */
    uint32_t stage2_size;      /* +0x10 */
    uint32_t stage2_checksum;  /* +0x14 byte sum of stage 2 */
    uint32_t reserved[2];      /* +0x18 */
} g2_codec_boot_header_t;
_Static_assert(sizeof(g2_codec_boot_header_t) == CODEC_BOOT_HEADER_SIZE, "boot header");

extern g2_codec_boot_header_t g2_codec_dfu_boot_header; /* RAM 0x2007395c */
extern void *g2_codec_dfu_package_file;                 /* RAM 0x2007492c */
extern uint8_t *g2_codec_dfu_boot_image;                /* RAM 0x20074930 */
extern uint32_t g2_codec_dfu_boot_size;                 /* RAM 0x20074934 */
extern uint8_t *g2_codec_dfu_flash_image;               /* RAM 0x20074938 */
extern uint32_t g2_codec_dfu_flash_size;                /* RAM 0x2007493c */
extern uint8_t g2_gx8002_version[4];                    /* RAM 0x20074940, big-endian */
extern uint8_t g2_codec_dfu_xfer_buffer[0x2000];        /* RAM 0x2035ee18 */

extern void *file_open(const char *path, const char *mode);                      /* 0x474550 */
extern int32_t file_close(void *file);                                          /* 0x4745f4 */
extern uint32_t file_read(void *buffer, uint32_t size, uint32_t count, void *file); /* 0x474634 */
extern int32_t file_seek(void *file, int32_t offset, int32_t origin);           /* 0x474814 */
extern void *file_heap_allocate(uint32_t size);                                 /* 0x474cd2 */
extern void file_heap_free(void *buffer);                                       /* 0x474d16 */
extern void *audio_queue_copy_bytes(void *dst, const void *src, uint32_t len);  /* 0x439be4 */
extern void audio_uart_checksum_copy(void *dst, const void *src, uint32_t len); /* 0x439c04 */
extern uint32_t g2_log_module_length(const char *text);                         /* 0x44a43c strlen */
extern int32_t g2_audio_dump_snprintf(char *dst, uint32_t size, const char *format, ...); /* 0x44b728 */
extern int32_t audio_ble_format_to_buffer(char *dst, const char *format, ...); /* 0x4b4728 sprintf */
extern void g2_delay_ms_4910f4(uint32_t ms);                                    /* 0x4910f4 */
extern void DRV_Gx8002_Reboot(uint8_t skip_boot_wait);                          /* 0x57a816 */
extern int32_t GX8002_ReadVersion(uint8_t version[4], uint32_t timeout);        /* 0x57c664 */
/* codec.porting (service_codec_porting.c) */
extern int32_t audio_uart_session_open(void);  /* uart_init 0x58fb52 */
extern int32_t audio_uart_session_close(void); /* uart_close 0x58fc0c */
extern uint32_t codec_dfu_crc32_58faac(const void *data, uint32_t length); /* 0x58faac -> 0x4d34c4(data, len, 0) */
extern int32_t codec_porting_uart_set_baud_58fab6(uint32_t baud); /* 0x58fab6, channel 3, 0 ok */
extern uint64_t codec_tick_snapshot(void);                        /* 0x58fac8 */
extern uint32_t codec_read_byte_deadline(uint8_t *dst, uint32_t timeout); /* 0x58fad2, 1 ok */
extern uint32_t codec_uart_read(uint8_t *dst, uint32_t capacity); /* 0x58fb2a */
extern int32_t audio_uart_send_bytes(const void *wire, uint32_t count); /* 0x58fb38 */
extern uint32_t codec_dfu_crc32_update_58fcf0(uint32_t crc, uint32_t length,
                                              const uint8_t *data); /* 0x58fcf0, table 0x6987a8, returns crc ^ ~0 */

int32_t semantic_CodecLoadFirmwarePackage(void);
void semantic_CodecFreeFirmwareBuffers(void);
void semantic_CodecFormatVersion(uint32_t version, char *buffer, uint32_t size);
int32_t semantic_CodecParseVersionBytes(const uint8_t *bytes, uint32_t *version);
int32_t semantic_CodecGetPackageVersion(uint32_t *version);
void semantic_CodecValidateFirmwareHeader(const g2_codec_boot_header_t *header);
bool semantic_CodecHostIsLittleEndian(void);
uint32_t semantic_CodecByteSwap32(uint32_t value);
uint32_t semantic_CodecHostToBigEndian32(uint32_t value);
int32_t semantic_CodecWaitForUartToken(const char *token, int32_t timeout);
int32_t semantic_CodecReadBootHeader(void);
int32_t semantic_CodecDownloadBootStage1(uint32_t stage2_baud);
int32_t semantic_CodecDownloadBootStage2(void);
int32_t semantic_CodecFlashImage(void);
int32_t SVC_CodecDfu(uint32_t reserved);
int32_t SVC_CodecCheckAndUpgrade(uint8_t force);

static const char module[] = "codec.dfu"; /* ROM 0x78be70 */
static const char file[] = "D:\\01_workspace\\s200_ap510b_iar_git\\platform\\audio\\service_codec_dfu.c"; /* ROM 0x6fcbb4 */
static const char package_path[] = "/firmware/codec.bin"; /* ROM 0x782e84 */
static const char load_mode[] = "r+";    /* ROM 0x5780dc (inline) */
static const char version_mode[] = "r+"; /* ROM 0x5787d4 (inline) */
static const char found_text[] = "found";     /* ROM 0x78e504 */
static const char missing_text[] = "missing"; /* ROM 0x78e50c */
static const char version_format[] = "%d.%d.%d.%d"; /* ROM 0x78be7c */
static const char token_f[] = "F";       /* ROM 0x579088 (inline) */
static const char token_wfb[] = "wfb";   /* ROM 0x579124 (inline) */
static const char token_ok[] = "OK";     /* ROM 0x579128 (inline) */
static const char token_get[] = "GET";   /* ROM 0x57913c (inline) */
static const char token_o[] = "O";       /* ROM 0x579640 (inline) */
static const char token_ready[] = "ready"; /* ROM 0x78e514 */
static const char token_boot[] = "boot>";  /* ROM 0x78e51c */
static const char token_sta[] = "~sta~";   /* ROM 0x78e524 */
static const char token_fin[] = "~fin~";   /* ROM 0x78e52c */
static const char token_result[] = "[Result]:"; /* ROM 0x78bec4 */
static const char token_succ[] = "SUCC";   /* ROM 0x78e534 */
static const char serialdown_format[] = "serialdown %d %d %d\n"; /* ROM 0x77b5cc */

/* load_firmware_from_package */
static const char fn_load[] = "load_firmware_from_package"; /* ROM 0x770d0c */
static const char load_start[] = "Start loading firmware package from file system: %s"; /* ROM 0x72cfd8 */
static const char load_start_s[] = "[codec.dfu]Start loading firmware package from file system: %s"; /* ROM 0x70e9e4 */
static const char load_open[] = "Cannot open firmware package file: %s, error code: %d"; /* ROM 0x722778 */
static const char load_open_s[] = "[codec.dfu]Cannot open firmware package file: %s, error code: %d"; /* ROM 0x70566c */
static const char load_header[] = "Failed to read firmware package header: %d"; /* ROM 0x742c54 */
static const char load_header_s[] = "[codec.dfu]Failed to read firmware package header: %d"; /* ROM 0x7227b0 */
static const char bad_magic[] = "Invalid firmware package magic: 0x%08X, expected: 0x%08X"; /* ROM 0x718310 */
static const char bad_magic_s[] = "[codec.dfu]Invalid firmware package magic: 0x%08X, expected: 0x%08X"; /* ROM 0x7056b0 */
static const char load_info[] = "Firmware package info: version=0x%08X, firmware count=%d"; /* ROM 0x71834c */
static const char load_info_s[] = "[codec.dfu]Firmware package info: version=0x%08X, firmware count=%d"; /* ROM 0x7056f4 */
static const char load_record[] = "Failed to read firmware info %d: %d"; /* ROM 0x7593f0 */
static const char load_record_s[] = "[codec.dfu]Failed to read firmware info %d: %d"; /* ROM 0x737e74 */
static const char found_boot[] = "Found Boot firmware: size=%d, offset=0x%08X, CRC32=0x%08X"; /* ROM 0x718388 */
static const char found_boot_s[] = "[codec.dfu]Found Boot firmware: size=%d, offset=0x%08X, CRC32=0x%08X"; /* ROM 0x6fcbfc */
static const char found_fw[] = "Found FW firmware: size=%d, offset=0x%08X, CRC32=0x%08X"; /* ROM 0x7227e8 */
static const char found_fw_s[] = "[codec.dfu]Found FW firmware: size=%d, offset=0x%08X, CRC32=0x%08X"; /* ROM 0x705738 */
static const char load_missing[] = "Missing required firmware in package: boot=%s, fw=%s"; /* ROM 0x722820 */
static const char load_missing_s[] = "[codec.dfu]Missing required firmware in package: boot=%s, fw=%s"; /* ROM 0x70ea24 */
static const char alloc_boot[] = "Failed to allocate boot firmware memory: %d bytes"; /* ROM 0x72d00c */
static const char alloc_boot_s[] = "[codec.dfu]Failed to allocate boot firmware memory: %d bytes"; /* ROM 0x70ea64 */
static const char read_boot[] = "Failed to read boot firmware: %d/%d"; /* ROM 0x759414 */
static const char read_boot_s[] = "[codec.dfu]Failed to read boot firmware: %d/%d"; /* ROM 0x737ea4 */
static const char crc_boot[] = "Boot firmware CRC32 verification failed: calculated=0x%08X, expected=0x%08X"; /* ROM 0x6f5d78 */
static const char crc_boot_s[] = "[codec.dfu]Boot firmware CRC32 verification failed: calculated=0x%08X, expected=0x%08X"; /* ROM 0x6e4c18 */
static const char alloc_fw[] = "Failed to allocate fw firmware memory: %d bytes"; /* ROM 0x737ed4 */
static const char alloc_fw_s[] = "[codec.dfu]Failed to allocate fw firmware memory: %d bytes"; /* ROM 0x7183c4 */
static const char read_fw[] = "Failed to read fw firmware: %d/%d"; /* ROM 0x759438 */
static const char read_fw_s[] = "[codec.dfu]Failed to read fw firmware: %d/%d"; /* ROM 0x737f04 */
static const char crc_fw[] = "FW firmware CRC32 verification failed: calculated=0x%08X, expected=0x%08X"; /* ROM 0x6f5dc4 */
static const char crc_fw_s[] = "[codec.dfu]FW firmware CRC32 verification failed: calculated=0x%08X, expected=0x%08X"; /* ROM 0x6e4c70 */
static const char load_ok[] = "Firmware loaded successfully: boot=%d bytes, fw=%d bytes"; /* ROM 0x718400 */
static const char load_ok_s[] = "[codec.dfu]Firmware loaded successfully: boot=%d bytes, fw=%d bytes"; /* ROM 0x70577c */

/* get_firmware_package_version */
static const char fn_version[] = "get_firmware_package_version"; /* ROM 0x764990 */
static const char version_null[] = "Version parameter is null"; /* ROM 0x770d28 */
static const char version_null_s[] = "[codec.dfu]Version parameter is null"; /* ROM 0x74da0c */
static const char version_get[] = "Get version number from firmware package: %s"; /* ROM 0x737f34 */
static const char version_get_s[] = "[codec.dfu]Get version number from firmware package: %s"; /* ROM 0x722858 */
static const char version_open[] = "Cannot open firmware package file: %s"; /* ROM 0x74da34 */
static const char version_open_s[] = "[codec.dfu]Cannot open firmware package file: %s"; /* ROM 0x72d040 */
static const char version_header[] = "Failed to read firmware package header: %zu"; /* ROM 0x742c80 */
static const char version_header_s[] = "[codec.dfu]Failed to read firmware package header: %zu"; /* ROM 0x722890 */
static const char version_ok[] = "Firmware package version: 0x%08X"; /* ROM 0x75945c */
static const char version_ok_s[] = "[codec.dfu]Firmware package version: 0x%08X"; /* ROM 0x742cac */

/* print_bootheader */
static const char fn_print[] = "print_bootheader"; /* ROM 0x782e98 */
static const char hdr_chip_id[] = "chip_id %x"; /* ROM 0x78be88 */
static const char hdr_chip_id_s[] = "[codec.dfu]chip_id %x"; /* ROM 0x77b464 */
static const char hdr_chip_type[] = "chip_type %x"; /* ROM 0x788770 */
static const char hdr_chip_type_s[] = "[codec.dfu]chip_type %x"; /* ROM 0x77b47c */
static const char hdr_chip_version[] = "chip_version %x"; /* ROM 0x788780 */
static const char hdr_chip_version_s[] = "[codec.dfu]chip_version %x"; /* ROM 0x770d44 */
static const char hdr_boot_delay[] = "boot_delay %x"; /* ROM 0x788790 */
static const char hdr_boot_delay_s[] = "[codec.dfu]boot_delay %x"; /* ROM 0x770d60 */
static const char hdr_stage1_size[] = "stage1_size %d"; /* ROM 0x7887a0 */
static const char hdr_stage1_size_s[] = "[codec.dfu]stage1_size %d"; /* ROM 0x770d7c */
static const char hdr_stage2_baud[] = "stage2_baud_rate %d"; /* ROM 0x782eac */
static const char hdr_stage2_baud_s[] = "[codec.dfu]stage2_baud_rate %d"; /* ROM 0x7649b0 */
static const char hdr_stage2_size[] = "stage2_size %d"; /* ROM 0x7887b0 */
static const char hdr_stage2_size_s[] = "[codec.dfu]stage2_size %d"; /* ROM 0x770d98 */
static const char hdr_stage2_checksum[] = "stage2_checksum %d"; /* ROM 0x782ec0 */
static const char hdr_stage2_checksum_s[] = "[codec.dfu]stage2_checksum %d"; /* ROM 0x7649d0 */

/* parse_bootimg_header */
static const char fn_parse[] = "parse_bootimg_header"; /* ROM 0x77b494 */
static const char parse_start[] = "reading boot header ..."; /* ROM 0x77b4ac */
static const char parse_start_s[] = "[codec.dfu]reading boot header ..."; /* ROM 0x759480 */
static const char parse_bad[] = "Boot firmware invalid or size insufficient"; /* ROM 0x742cd8 */
static const char parse_bad_s[] = "[codec.dfu]Boot firmware invalid or size insufficient"; /* ROM 0x7228c8 */

/* download_bootimg_stage1 */
static const char fn_stage1[] = "download_bootimg_stage1"; /* ROM 0x77b4c4 */
static const char s1_start[] = "start boot stage1 ..."; /* ROM 0x77b4dc */
static const char s1_start_s[] = "[codec.dfu]start boot stage1 ..."; /* ROM 0x7594a4 */
static const char s1_download[] = "download boot stage1 ..."; /* ROM 0x770db4 */
static const char s1_download_s[] = "[codec.dfu]download boot stage1 ..."; /* ROM 0x7594c8 */
static const char s1_wait_f[] = "download size: %d, waiting 'F' ..."; /* ROM 0x7594ec */
static const char s1_wait_f_s[] = "[codec.dfu]download size: %d, waiting 'F' ..."; /* ROM 0x737f64 */
static const char s1_f_err[] = "wait 'F' err !"; /* ROM 0x7887c0 */
static const char s1_f_err_s[] = "[codec.dfu]wait 'F' err !"; /* ROM 0x770dd0 */
static const char s1_f_ok[] = "get 'F' !"; /* ROM 0x78be94 */
static const char s1_f_ok_s[] = "[codec.dfu]get 'F' !"; /* ROM 0x77b4f4 */
static const char s1_wfb_err[] = "Wait for \"wfb\",please check UART receive !"; /* ROM 0x742d04 */
static const char s1_wfb_err_s[] = "[codec.dfu]Wait for \"wfb\",please check UART receive !"; /* ROM 0x722900 */
static const char s1_ok_err[] = "Wait for \"OK\",please check UART receive !"; /* ROM 0x742d30 */
static const char s1_ok_err_s[] = "[codec.dfu]Wait for \"OK\",please check UART receive !"; /* ROM 0x722938 */
static const char s1_baud[] = "stage2 baud: %d"; /* ROM 0x7887d0 */
static const char s1_baud_s[] = "[codec.dfu]stage2 baud: %d"; /* ROM 0x770dec */
static const char uart_config_err[] = "Uart config error!"; /* ROM 0x782ed4 */
static const char uart_config_err_s[] = "[codec.dfu]Uart config error!"; /* ROM 0x7649f0 */
static const char s1_wait_get[] = "wait \"GET\" ..."; /* ROM 0x7887e0 */
static const char s1_wait_get_s[] = "[codec.dfu]wait \"GET\" ..."; /* ROM 0x770e08 */
static const char s1_get_err[] = "wait 'GET' err !"; /* ROM 0x782ee8 */
static const char s1_get_err_s[] = "[codec.dfu]wait 'GET' err !"; /* ROM 0x770e24 */
static const char s1_get_ok[] = "get \"GET\" !"; /* ROM 0x78bea0 */
static const char s1_get_ok_s[] = "[codec.dfu]get \"GET\" !"; /* ROM 0x77b50c */
static const char s1_ok[] = "boot stage1 ok !"; /* ROM 0x782efc */
static const char s1_ok_s[] = "[codec.dfu]boot stage1 ok !"; /* ROM 0x770e40 */

/* download_bootimg_stage2 */
static const char fn_stage2[] = "download_bootimg_stage2"; /* ROM 0x77b524 */
static const char s2_start[] = "start boot stage2 ..."; /* ROM 0x77b53c */
static const char s2_start_s[] = "[codec.dfu]start boot stage2 ..."; /* ROM 0x759510 */
static const char s2_info[] = "stage2_size = %u, checksum = %u"; /* ROM 0x764a10 */
static const char s2_info_s[] = "[codec.dfu]stage2_size = %u, checksum = %u"; /* ROM 0x742d5c */
static const char s2_info_err[] = "stage2_size or checksum err !"; /* ROM 0x764a30 */
static const char s2_info_err_s[] = "[codec.dfu]stage2_size or checksum err !"; /* ROM 0x742d88 */
static const char s2_wait_ready[] = "waiting \"ready\" ..."; /* ROM 0x782f10 */
static const char s2_wait_ready_s[] = "[codec.dfu]waiting \"ready\" ..."; /* ROM 0x764a50 */
static const char s2_ready_err[] = "wait ready error !"; /* ROM 0x782f24 */
static const char s2_ready_err_s[] = "[codec.dfu]wait ready error !"; /* ROM 0x764a70 */
static const char s2_ready_ok[] = "get \"ready\""; /* ROM 0x78beac */
static const char s2_ready_ok_s[] = "[codec.dfu]get \"ready\""; /* ROM 0x77b554 */
static const char s2_download[] = "download boot stage2 ..."; /* ROM 0x770e5c */
static const char s2_download_s[] = "[codec.dfu]download boot stage2 ..."; /* ROM 0x759534 */
static const char s2_wait_o[] = "download size: %d, waiting 'O' ..."; /* ROM 0x759558 */
static const char s2_wait_o_s[] = "[codec.dfu]download size: %d, waiting 'O' ..."; /* ROM 0x737f94 */
static const char s2_o_err[] = "wait 'O' err !"; /* ROM 0x7887f0 */
static const char s2_o_err_s[] = "[codec.dfu]wait 'O' err !"; /* ROM 0x770e78 */
static const char s2_o_ok[] = "get 'O' !"; /* ROM 0x78beb8 */
static const char s2_o_ok_s[] = "[codec.dfu]get 'O' !"; /* ROM 0x77b56c */
static const char s2_wait_boot[] = "waiting \"boot>\" ..."; /* ROM 0x782f38 */
static const char s2_wait_boot_s[] = "[codec.dfu]waiting \"boot>\" ..."; /* ROM 0x764a90 */
static const char s2_boot_err[] = "wait \"boot>\" err !"; /* ROM 0x782f4c */
static const char s2_boot_err_s[] = "[codec.dfu]wait \"boot>\" err !"; /* ROM 0x764ab0 */
static const char s2_boot_ok[] = "get \"boot>\" !"; /* ROM 0x788800 */
static const char s2_boot_ok_s[] = "[codec.dfu]get \"boot>\" !"; /* ROM 0x770e94 */
static const char s2_ok[] = "boot stage2 ok !"; /* ROM 0x782f60 */
static const char s2_ok_s[] = "[codec.dfu]boot stage2 ok !"; /* ROM 0x770eb0 */

/* download_flashimg */
static const char fn_flash[] = "download_flashimg"; /* ROM 0x782f74 */
static const char fl_start[] = "start flash image ..."; /* ROM 0x77b584 */
static const char fl_start_s[] = "[codec.dfu]start flash image ..."; /* ROM 0x75957c */
static const char fl_size[] = "flash image size = %d"; /* ROM 0x77b59c */
static const char fl_size_s[] = "[codec.dfu]flash image size = %d"; /* ROM 0x7595a0 */
static const char fl_size_err[] = "flash image size err !"; /* ROM 0x77b5b4 */
static const char fl_size_err_s[] = "[codec.dfu]flash image size err !"; /* ROM 0x7595c4 */
static const char fl_command[] = "len = %d, data_buf = %s"; /* ROM 0x77b5e4 */
static const char fl_command_s[] = "[codec.dfu]len = %d, data_buf = %s"; /* ROM 0x7595e8 */
static const char fl_wait_sta[] = "waiting \"~sta~\" ..."; /* ROM 0x782f88 */
static const char fl_wait_sta_s[] = "[codec.dfu]waiting \"~sta~\" ..."; /* ROM 0x764ad0 */
static const char fl_sta_err[] = "wait ~sta~ err !"; /* ROM 0x782f9c */
static const char fl_sta_err_s[] = "[codec.dfu]wait ~sta~ err !"; /* ROM 0x770ecc */
static const char fl_sta_ok[] = "get \"~sta~\" !"; /* ROM 0x788810 */
static const char fl_sta_ok_s[] = "[codec.dfu]get \"~sta~\" !"; /* ROM 0x770ee8 */
static const char fl_download[] = "download flash image ..."; /* ROM 0x770f04 */
static const char fl_download_s[] = "[codec.dfu]download flash image ..."; /* ROM 0x75960c */
static const char fl_chunk[] = "total_size = %d, xfer_size = %d"; /* ROM 0x764af0 */
static const char fl_chunk_s[] = "[codec.dfu]total_size = %d, xfer_size = %d"; /* ROM 0x742db4 */
static const char fl_wait_fin[] = "waiting \"~fin~\" ..."; /* ROM 0x782fb0 */
static const char fl_wait_fin_s[] = "[codec.dfu]waiting \"~fin~\" ..."; /* ROM 0x764b10 */
static const char fl_fin_err[] = "wait \"~fin~\" err !"; /* ROM 0x782fc4 */
static const char fl_fin_err_s[] = "[codec.dfu]wait \"~fin~\" err !"; /* ROM 0x764b30 */
static const char fl_fin_ok[] = "get \"~fin~\" !"; /* ROM 0x788820 */
static const char fl_fin_ok_s[] = "[codec.dfu]get \"~fin~\" !"; /* ROM 0x770f20 */
static const char fl_failed[] = "download failed"; /* ROM 0x788830 */
static const char fl_failed_s[] = "[codec.dfu]download failed"; /* ROM 0x770f3c */
static const char fl_ok[] = "flash image ok !"; /* ROM 0x782fd8 */
static const char fl_ok_s[] = "[codec.dfu]flash image ok !"; /* ROM 0x770f58 */

/* SVC_CodecDfu */
static const char fn_dfu[] = "SVC_CodecDfu"; /* ROM 0x788840 */
static const char dfu_baud[] = "stage1 baud: %d"; /* ROM 0x788850 */
static const char dfu_baud_s[] = "[codec.dfu]stage1 baud: %d"; /* ROM 0x770f74 */
static const char dfu_load_err[] = "Failed to load firmware package"; /* ROM 0x764b50 */
static const char dfu_load_err_s[] = "[codec.dfu]Failed to load firmware package"; /* ROM 0x742de0 */
static const char dfu_m_timeout[] = "wait M timeout"; /* ROM 0x788860 */
static const char dfu_m_timeout_s[] = "[codec.dfu]wait M timeout"; /* ROM 0x770f90 */
static const char dfu_m_ok[] = "get M message"; /* ROM 0x788870 */
static const char dfu_m_ok_s[] = "[codec.dfu]get M message"; /* ROM 0x770fac */
static const char dfu_ok[] = "Codec DFU upgrade successful!"; /* ROM 0x764b70 */
static const char dfu_ok_s[] = "[codec.dfu]Codec DFU upgrade successful!"; /* ROM 0x742e0c */
static const char dfu_failed[] = "Codec DFU upgrade failed!"; /* ROM 0x770fc8 */
static const char dfu_failed_s[] = "[codec.dfu]Codec DFU upgrade failed!"; /* ROM 0x74da5c */

/* SVC_CodecCheckAndUpgrade */
static const char fn_check[] = "SVC_CodecCheckAndUpgrade"; /* ROM 0x770fe4 */
static const char chk_start[] = "Start checking Codec version ..."; /* ROM 0x759630 */
static const char chk_start_s[] = "[codec.dfu]Start checking Codec version ..."; /* ROM 0x742e38 */
static const char chk_pkg_err[] = "Failed to get firmware package version: %d"; /* ROM 0x742e64 */
static const char chk_pkg_err_s[] = "[codec.dfu]Failed to get firmware package version: %d"; /* ROM 0x722970 */
static const char chk_pkg[] = "Firmware package version: %s (0x%08X)"; /* ROM 0x74da84 */
static const char chk_pkg_s[] = "[codec.dfu]Firmware package version: %s (0x%08X)"; /* ROM 0x72d074 */
static const char chk_query_err[] = "Failed to query codec version: %d, go force upgrade"; /* ROM 0x72d0a8 */
static const char chk_query_err_s[] = "[codec.dfu]Failed to query codec version: %d, go force upgrade"; /* ROM 0x70eaa4 */
static const char chk_parse_err[] = "Failed to parse codec version: %d"; /* ROM 0x759654 */
static const char chk_parse_err_s[] = "[codec.dfu]Failed to parse codec version: %d"; /* ROM 0x737fc4 */
static const char chk_current[] = "Current Codec version: %s (0x%08X)"; /* ROM 0x759678 */
static const char chk_current_s[] = "[codec.dfu]Current Codec version: %s (0x%08X)"; /* ROM 0x737ff4 */
static const char chk_same[] = "Codec version is same as package version, no upgrade needed"; /* ROM 0x71843c */
static const char chk_same_s[] = "[codec.dfu]Codec version is same as package version, no upgrade needed"; /* ROM 0x6fcc44 */
static const char chk_diff[] = "Codec version is different from package version, starting upgrade ..."; /* ROM 0x6fcc8c */
static const char chk_diff_s[] = "[codec.dfu]Codec version is different from package version, starting upgrade ..."; /* ROM 0x6e9b44 */
static const char chk_force[] = "Force upgrade mode, starting upgrade ..."; /* ROM 0x742e90 */
static const char chk_force_s[] = "[codec.dfu]Force upgrade mode, starting upgrade ..."; /* ROM 0x72d0dc */
static const char chk_failed[] = "Upgrade failed: %d"; /* ROM 0x782fec */
static const char chk_failed_s[] = "[codec.dfu]Upgrade failed: %d"; /* ROM 0x764b90 */
static const char chk_ok[] = "Codec firmware upgrade successful, new version: %s"; /* ROM 0x72d110 */
static const char chk_ok_s[] = "[codec.dfu]Codec firmware upgrade successful, new version: %s"; /* ROM 0x70eae4 */

#define DFU_LOG GX8002_LOG

/* Stock closes and clears the package handle on every failure path. */
static void close_package(void)
{
    if (g2_codec_dfu_package_file != NULL) {
        (void)file_close(g2_codec_dfu_package_file);
        g2_codec_dfu_package_file = NULL;
    }
}

/* 0x577d7c. The four "read failed" logs print a `ret` local the stock never
 * assigns (callee-saved r6 at entry); the empty asm keeps it indeterminate. */
int32_t semantic_CodecLoadFirmwarePackage(void)
{
    g2_codec_package_header_t header;
    g2_codec_firmware_info_t info;
    g2_codec_firmware_info_t boot_info;
    g2_codec_firmware_info_t fw_info;
    bool boot_found;
    bool fw_found;
    int32_t ret;
    uint32_t crc;

    __asm__("" : "=r"(ret));
    audio_uart_buffer_zero(&boot_info, sizeof(boot_info), 0u);
    audio_uart_buffer_zero(&fw_info, sizeof(fw_info), 0u);
    boot_found = false;
    fw_found = false;

    DFU_LOG(4u, 0x10400000u, fn_load, 85u, load_start, load_start_s, package_path);
    g2_codec_dfu_package_file = file_open(package_path, load_mode);
    if (g2_codec_dfu_package_file == NULL) {
        DFU_LOG(1u, 0x04800000u, fn_load, 91u, load_open, load_open_s, package_path, -1);
        return -1;
    }
    if (file_read(&header, 1u, sizeof(header), g2_codec_dfu_package_file) != sizeof(header)) {
        DFU_LOG(1u, 0x04400000u, fn_load, 98u, load_header, load_header_s, ret);
        close_package();
        return -1;
    }
    if (header.magic != CODEC_FWPK_MAGIC) {
        DFU_LOG(1u, 0x04800000u, fn_load, 105u, bad_magic, bad_magic_s, header.magic,
                CODEC_FWPK_MAGIC);
        close_package();
        return -1;
    }
    DFU_LOG(4u, 0x10800000u, fn_load, 110u, load_info, load_info_s, header.version, header.count);

    for (uint32_t i = 0u; i < header.count; i++) {
        if (file_read(&info, 1u, sizeof(info), g2_codec_dfu_package_file) != sizeof(info)) {
            DFU_LOG(1u, 0x04800000u, fn_load, 118u, load_record, load_record_s, i, ret);
            close_package();
            return -1;
        }
        if (info.type == CODEC_FW_TYPE_BOOT) {
            audio_uart_checksum_copy(&boot_info, &info, sizeof(info));
            boot_found = true;
            DFU_LOG(4u, 0x10c00000u, fn_load, 127u, found_boot, found_boot_s, info.size,
                    info.offset, info.crc32);
        } else if (info.type == CODEC_FW_TYPE_FLASH) {
            audio_uart_checksum_copy(&fw_info, &info, sizeof(info));
            fw_found = true;
            DFU_LOG(4u, 0x10c00000u, fn_load, 132u, found_fw, found_fw_s, info.size,
                    info.offset, info.crc32);
        }
    }

    if (!(boot_found && fw_found)) {
        DFU_LOG(1u, 0x04800000u, fn_load, 138u, load_missing, load_missing_s,
                boot_found ? found_text : missing_text, fw_found ? found_text : missing_text);
        close_package();
        return -1;
    }

    g2_codec_dfu_boot_size = boot_info.size;
    g2_codec_dfu_boot_image = file_heap_allocate(g2_codec_dfu_boot_size);
    if (g2_codec_dfu_boot_image == NULL) {
        DFU_LOG(1u, 0x04400000u, fn_load, 147u, alloc_boot, alloc_boot_s, g2_codec_dfu_boot_size);
        close_package();
        return -1;
    }
    (void)file_seek(g2_codec_dfu_package_file, (int32_t)boot_info.offset, 0);
    if (file_read(g2_codec_dfu_boot_image, 1u, g2_codec_dfu_boot_size,
                  g2_codec_dfu_package_file) != g2_codec_dfu_boot_size) {
        DFU_LOG(1u, 0x04800000u, fn_load, 155u, read_boot, read_boot_s, ret,
                g2_codec_dfu_boot_size);
        file_heap_free(g2_codec_dfu_boot_image);
        g2_codec_dfu_boot_image = NULL;
        close_package();
        return -1;
    }
    crc = codec_dfu_crc32_58faac(g2_codec_dfu_boot_image, g2_codec_dfu_boot_size);
    if (crc != boot_info.crc32) {
        DFU_LOG(1u, 0x04800000u, fn_load, 165u, crc_boot, crc_boot_s, crc, boot_info.crc32);
        file_heap_free(g2_codec_dfu_boot_image);
        g2_codec_dfu_boot_image = NULL;
        close_package();
        return -1;
    }

    g2_codec_dfu_flash_size = fw_info.size;
    g2_codec_dfu_flash_image = file_heap_allocate(g2_codec_dfu_flash_size);
    if (g2_codec_dfu_flash_image == NULL) {
        DFU_LOG(1u, 0x04400000u, fn_load, 176u, alloc_fw, alloc_fw_s, g2_codec_dfu_flash_size);
        file_heap_free(g2_codec_dfu_boot_image);
        g2_codec_dfu_boot_image = NULL;
        close_package();
        return -1;
    }
    (void)file_seek(g2_codec_dfu_package_file, (int32_t)fw_info.offset, 0);
    if (file_read(g2_codec_dfu_flash_image, 1u, g2_codec_dfu_flash_size,
                  g2_codec_dfu_package_file) != g2_codec_dfu_flash_size) {
        DFU_LOG(1u, 0x04800000u, fn_load, 186u, read_fw, read_fw_s, ret, g2_codec_dfu_flash_size);
        file_heap_free(g2_codec_dfu_boot_image);
        file_heap_free(g2_codec_dfu_flash_image);
        g2_codec_dfu_boot_image = NULL;
        g2_codec_dfu_flash_image = NULL;
        close_package();
        return -1;
    }
    crc = codec_dfu_crc32_58faac(g2_codec_dfu_flash_image, g2_codec_dfu_flash_size);
    if (crc != fw_info.crc32) {
        DFU_LOG(1u, 0x04800000u, fn_load, 198u, crc_fw, crc_fw_s, crc, fw_info.crc32);
        file_heap_free(g2_codec_dfu_boot_image);
        file_heap_free(g2_codec_dfu_flash_image);
        g2_codec_dfu_boot_image = NULL;
        g2_codec_dfu_flash_image = NULL;
        close_package();
        return -1;
    }
    close_package();
    DFU_LOG(3u, 0x0c800000u, fn_load, 209u, load_ok, load_ok_s, g2_codec_dfu_boot_size,
            g2_codec_dfu_flash_size);
    return 0;
}

/* 0x578530 */
void semantic_CodecFreeFirmwareBuffers(void)
{
    if (g2_codec_dfu_boot_image != NULL) {
        file_heap_free(g2_codec_dfu_boot_image);
        g2_codec_dfu_boot_image = NULL;
        g2_codec_dfu_boot_size = 0u;
    }
    if (g2_codec_dfu_flash_image != NULL) {
        file_heap_free(g2_codec_dfu_flash_image);
        g2_codec_dfu_flash_image = NULL;
        g2_codec_dfu_flash_size = 0u;
    }
}

/* 0x57856c: "a.b.c.d" from the big-endian packed version; needs >= 16 bytes. */
void semantic_CodecFormatVersion(uint32_t version, char *buffer, uint32_t size)
{
    if (buffer == NULL || size < 16u)
        return;
    (void)g2_audio_dump_snprintf(buffer, size, version_format, (uint8_t)(version >> 24),
                                 (uint8_t)(version >> 16), (uint8_t)(version >> 8),
                                 (uint8_t)version);
}

/* 0x5785a2: four codec version bytes (major first) to a packed u32. */
int32_t semantic_CodecParseVersionBytes(const uint8_t *bytes, uint32_t *version)
{
    if (bytes == NULL || version == NULL)
        return -1;
    *version = ((uint32_t)bytes[0] << 24) | ((uint32_t)bytes[1] << 16) |
               ((uint32_t)bytes[2] << 8) | (uint32_t)bytes[3];
    return 0;
}

/* 0x5785ca: FWPK header version word. The file is closed before the magic
 * check on the success path, after the log on a short read. */
int32_t semantic_CodecGetPackageVersion(uint32_t *version)
{
    g2_codec_package_header_t header;
    void *handle;
    uint32_t got;

    if (version == NULL) {
        DFU_LOG(1u, 0x04000000u, fn_version, 266u, version_null, version_null_s);
        return -1;
    }
    DFU_LOG(4u, 0x10400000u, fn_version, 270u, version_get, version_get_s, package_path);
    handle = file_open(package_path, version_mode);
    if (handle == NULL) {
        DFU_LOG(1u, 0x04400000u, fn_version, 275u, version_open, version_open_s, package_path);
        return -1;
    }
    got = file_read(&header, 1u, sizeof(header), handle);
    if (got != sizeof(header)) {
        DFU_LOG(1u, 0x04400000u, fn_version, 282u, version_header, version_header_s, got);
        if (handle != NULL)
            (void)file_close(handle);
        return -1;
    }
    if (handle != NULL)
        (void)file_close(handle);
    if (header.magic != CODEC_FWPK_MAGIC) {
        DFU_LOG(1u, 0x04800000u, fn_version, 291u, bad_magic, bad_magic_s, header.magic,
                CODEC_FWPK_MAGIC);
        return -1;
    }
    *version = header.version;
    DFU_LOG(4u, 0x10400000u, fn_version, 296u, version_ok, version_ok_s, *version);
    return 0;
}

/* 0x578810 (print_bootheader): logs only, nothing is validated. */
void semantic_CodecValidateFirmwareHeader(const g2_codec_boot_header_t *header)
{
    DFU_LOG(4u, 0x10400000u, fn_print, 358u, hdr_chip_id, hdr_chip_id_s, header->chip_id);
    DFU_LOG(4u, 0x10400000u, fn_print, 359u, hdr_chip_type, hdr_chip_type_s, header->chip_type);
    DFU_LOG(4u, 0x10400000u, fn_print, 360u, hdr_chip_version, hdr_chip_version_s,
            header->chip_version);
    DFU_LOG(4u, 0x10400000u, fn_print, 361u, hdr_boot_delay, hdr_boot_delay_s,
            header->boot_delay);
    DFU_LOG(4u, 0x10400000u, fn_print, 362u, hdr_stage1_size, hdr_stage1_size_s,
            header->stage1_size);
    DFU_LOG(4u, 0x10400000u, fn_print, 363u, hdr_stage2_baud, hdr_stage2_baud_s,
            header->stage2_baud_rate);
    DFU_LOG(4u, 0x10400000u, fn_print, 364u, hdr_stage2_size, hdr_stage2_size_s,
            header->stage2_size);
    DFU_LOG(4u, 0x10400000u, fn_print, 365u, hdr_stage2_checksum, hdr_stage2_checksum_s,
            header->stage2_checksum);
}

/* 0x578a6c: first byte of the word 0x11223344 (ROM 0x57963c) is 0x44. */
bool semantic_CodecHostIsLittleEndian(void)
{
    union {
        uint32_t word;
        uint8_t byte;
    } probe;

    probe.word = 0x11223344u;
    return probe.byte == 0x44u;
}

/* 0x578aac */
uint32_t semantic_CodecByteSwap32(uint32_t value)
{
    return ((value & 0x0000ff00u) << 8) | (value << 24) | ((value >> 8) & 0x0000ff00u) |
           (value >> 24);
}

/* 0x578ac8 (applied to big-endian file fields, i.e. ntohl) */
uint32_t semantic_CodecHostToBigEndian32(uint32_t value)
{
    if (semantic_CodecHostIsLittleEndian())
        value = semantic_CodecByteSwap32(value);
    return value;
}

/* 0x578ae0: match `token` on UART3 before the 64-bit tick deadline
 * start + timeout (timeout sign-extended). CR is read as LF; a mismatch
 * restarts the match without re-testing the mismatching byte. 0 / -1. */
int32_t semantic_CodecWaitForUartToken(const char *token, int32_t timeout)
{
    const int32_t length = (int32_t)g2_log_module_length(token);
    const uint64_t start = codec_tick_snapshot();
    const uint64_t deadline = start + (uint64_t)(int64_t)timeout;
    uint64_t now = start;
    uint8_t byte;

    while (now < deadline) {
        const uint32_t remaining = (uint32_t)(deadline - now);
        for (int32_t i = 0; i < length; i++) {
            if (codec_read_byte_deadline(&byte, remaining) != 1u)
                break;
            if (byte == '\r')
                byte = '\n';
            if (byte != (uint8_t)token[i])
                break;
            if (i + 1 == length)
                return 0;
        }
        now = codec_tick_snapshot();
    }
    return -1;
}

/* 0x578b70 (parse_bootimg_header): copy and byte-swap the 32-byte header. */
int32_t semantic_CodecReadBootHeader(void)
{
    g2_codec_boot_header_t *header = &g2_codec_dfu_boot_header;

    DFU_LOG(4u, 0x10000000u, fn_parse, 421u, parse_start, parse_start_s);
    if (g2_codec_dfu_boot_image == NULL || g2_codec_dfu_boot_size < CODEC_BOOT_HEADER_SIZE) {
        DFU_LOG(1u, 0x04000000u, fn_parse, 424u, parse_bad, parse_bad_s);
        return -1;
    }
    (void)audio_queue_copy_bytes(header, g2_codec_dfu_boot_image, CODEC_BOOT_HEADER_SIZE);
    header->stage1_size = (int32_t)semantic_CodecHostToBigEndian32((uint32_t)header->stage1_size);
    header->stage2_baud_rate =
        (int32_t)semantic_CodecHostToBigEndian32((uint32_t)header->stage2_baud_rate);
    header->stage2_size = semantic_CodecHostToBigEndian32(header->stage2_size);
    header->stage2_checksum = semantic_CodecHostToBigEndian32(header->stage2_checksum);
    semantic_CodecValidateFirmwareHeader(header);
    return 0;
}

/* 0x578ca4 (download_bootimg_stage1). The 'Y' word count is stage1_size / 4
 * (signed); the body loop runs over count * 4 bytes only for chip_type 1,
 * otherwise over the word count. Each write is a full 256 bytes. */
int32_t semantic_CodecDownloadBootStage1(uint32_t stage2_baud)
{
    uint8_t *const buffer = g2_codec_dfu_xfer_buffer;
    const uint8_t *source = g2_codec_dfu_boot_image + CODEC_BOOT_HEADER_SIZE;
    const g2_codec_boot_header_t *header = &g2_codec_dfu_boot_header;
    int32_t sent = 0;
    int32_t length;

    DFU_LOG(4u, 0x10000000u, fn_stage1, 447u, s1_start, s1_start_s);
    length = header->stage1_size / 4;
    buffer[0] = 'Y';
    buffer[1] = (uint8_t)length;
    buffer[2] = (uint8_t)(length >> 8);
    buffer[3] = (uint8_t)(length >> 16);
    buffer[4] = (uint8_t)(length >> 24);
    (void)audio_uart_send_bytes(buffer, 5u);
    if (header->chip_type == 1u)
        length <<= 2;

    DFU_LOG(4u, 0x10000000u, fn_stage1, 461u, s1_download, s1_download_s);
    for (; sent < length; sent += (int32_t)CODEC_BOOT_CHUNK) {
        (void)audio_queue_copy_bytes(buffer, source, CODEC_BOOT_CHUNK);
        source += CODEC_BOOT_CHUNK;
        (void)audio_uart_send_bytes(buffer, CODEC_BOOT_CHUNK);
    }
    DFU_LOG(4u, 0x10400000u, fn_stage1, 470u, s1_wait_f, s1_wait_f_s, sent);

    if (semantic_CodecWaitForUartToken(token_f, CODEC_TOKEN_TIMEOUT) < 0) {
        DFU_LOG(2u, 0x08000000u, fn_stage1, 472u, s1_f_err, s1_f_err_s);
        return -1;
    }
    DFU_LOG(4u, 0x10000000u, fn_stage1, 475u, s1_f_ok, s1_f_ok_s);

    if (semantic_CodecWaitForUartToken(token_wfb, CODEC_TOKEN_TIMEOUT) != 0) {
        DFU_LOG(2u, 0x08000000u, fn_stage1, 478u, s1_wfb_err, s1_wfb_err_s);
        return -1;
    }
    (void)audio_ble_format_to_buffer((char *)buffer, token_ok);
    (void)audio_uart_send_bytes(buffer, g2_log_module_length((const char *)buffer));
    buffer[0] = (uint8_t)stage2_baud;
    buffer[1] = (uint8_t)(stage2_baud >> 8);
    buffer[2] = (uint8_t)(stage2_baud >> 16);
    buffer[3] = (uint8_t)(stage2_baud >> 24);
    (void)audio_uart_send_bytes(buffer, 4u);

    if (semantic_CodecWaitForUartToken(token_ok, CODEC_TOKEN_TIMEOUT) != 0) {
        DFU_LOG(2u, 0x08000000u, fn_stage1, 494u, s1_ok_err, s1_ok_err_s);
        return -1;
    }
    DFU_LOG(4u, 0x10400000u, fn_stage1, 499u, s1_baud, s1_baud_s, stage2_baud);
    if (codec_porting_uart_set_baud_58fab6(stage2_baud) != 0) {
        DFU_LOG(2u, 0x08000000u, fn_stage1, 501u, uart_config_err, uart_config_err_s);
        return -1;
    }
    DFU_LOG(4u, 0x10000000u, fn_stage1, 505u, s1_wait_get, s1_wait_get_s);
    if (semantic_CodecWaitForUartToken(token_get, CODEC_TOKEN_TIMEOUT) < 0) {
        DFU_LOG(2u, 0x08000000u, fn_stage1, 507u, s1_get_err, s1_get_err_s);
        return -1;
    }
    DFU_LOG(4u, 0x10000000u, fn_stage1, 510u, s1_get_ok, s1_get_ok_s);
    buffer[0] = 'O';
    buffer[1] = 'K';
    (void)audio_uart_send_bytes(buffer, 2u);
    DFU_LOG(4u, 0x10000000u, fn_stage1, 516u, s1_ok, s1_ok_s);
    return 0;
}

/* 0x5791a0 (download_bootimg_stage2): stage 2 follows stage 1 in the boot
 * container; checksum and size are sent in host (little-endian) order. */
int32_t semantic_CodecDownloadBootStage2(void)
{
    const g2_codec_boot_header_t *header = &g2_codec_dfu_boot_header;
    const uint8_t *source =
        g2_codec_dfu_boot_image + header->stage1_size + CODEC_BOOT_HEADER_SIZE;
    uint8_t *const buffer = g2_codec_dfu_xfer_buffer;
    uint32_t stage2_size = 0u;
    uint32_t checksum = 0u;
    uint32_t sent = 0u;

    DFU_LOG(4u, 0x10000000u, fn_stage2, 529u, s2_start, s2_start_s);
    stage2_size = header->stage2_size;
    checksum = header->stage2_checksum;
    DFU_LOG(4u, 0x10800000u, fn_stage2, 533u, s2_info, s2_info_s, stage2_size, checksum);
    if (checksum == 0u || stage2_size == 0u) {
        DFU_LOG(2u, 0x08000000u, fn_stage2, 536u, s2_info_err, s2_info_err_s);
        return -1;
    }
    buffer[0] = 'S';
    (void)audio_uart_send_bytes(buffer, 1u);
    (void)audio_uart_send_bytes(&checksum, 4u);
    (void)audio_uart_send_bytes(&stage2_size, 4u);

    DFU_LOG(4u, 0x10000000u, fn_stage2, 545u, s2_wait_ready, s2_wait_ready_s);
    if (semantic_CodecWaitForUartToken(token_ready, CODEC_TOKEN_TIMEOUT) < 0) {
        DFU_LOG(2u, 0x08000000u, fn_stage2, 547u, s2_ready_err, s2_ready_err_s);
        return -1;
    }
    DFU_LOG(4u, 0x10000000u, fn_stage2, 550u, s2_ready_ok, s2_ready_ok_s);
    DFU_LOG(4u, 0x10000000u, fn_stage2, 552u, s2_download, s2_download_s);
    for (; sent < stage2_size; sent += CODEC_BOOT_CHUNK) {
        (void)audio_queue_copy_bytes(buffer, source, CODEC_BOOT_CHUNK);
        source += CODEC_BOOT_CHUNK;
        (void)audio_uart_send_bytes(buffer, CODEC_BOOT_CHUNK);
    }
    DFU_LOG(4u, 0x10400000u, fn_stage2, 562u, s2_wait_o, s2_wait_o_s, sent);
    if (semantic_CodecWaitForUartToken(token_o, CODEC_TOKEN_TIMEOUT) < 0) {
        DFU_LOG(2u, 0x08000000u, fn_stage2, 564u, s2_o_err, s2_o_err_s);
        return -1;
    }
    DFU_LOG(4u, 0x10000000u, fn_stage2, 567u, s2_o_ok, s2_o_ok_s);
    DFU_LOG(4u, 0x10000000u, fn_stage2, 569u, s2_wait_boot, s2_wait_boot_s);
    if (semantic_CodecWaitForUartToken(token_boot, CODEC_TOKEN_TIMEOUT) != 0) {
        DFU_LOG(2u, 0x08000000u, fn_stage2, 571u, s2_boot_err, s2_boot_err_s);
        return -1;
    }
    DFU_LOG(4u, 0x10000000u, fn_stage2, 574u, s2_boot_ok, s2_boot_ok_s);
    DFU_LOG(4u, 0x10000000u, fn_stage2, 576u, s2_ok, s2_ok_s);
    return 0;
}

/* 0x5796c8 (download_flashimg): stage-2 "serialdown" console command. */
int32_t semantic_CodecFlashImage(void)
{
    const uint8_t *const image = g2_codec_dfu_flash_image;
    char *const buffer = (char *)g2_codec_dfu_xfer_buffer;
    int32_t total;
    int32_t offset;
    int32_t chunk;
    int32_t length;
    uint32_t crc;

    audio_uart_buffer_zero(&total, sizeof(total), 0u);
    DFU_LOG(4u, 0x10000000u, fn_flash, 593u, fl_start, fl_start_s);
    total = (int32_t)g2_codec_dfu_flash_size;
    DFU_LOG(4u, 0x10400000u, fn_flash, 596u, fl_size, fl_size_s, total);
    if (total == 0) {
        DFU_LOG(2u, 0x08000000u, fn_flash, 599u, fl_size_err, fl_size_err_s);
        return -1;
    }
    audio_uart_buffer_zero(buffer, CODEC_FLASH_CHUNK, 0u);
    length = audio_ble_format_to_buffer(buffer, serialdown_format, 0, total, CODEC_FLASH_CHUNK);
    DFU_LOG(4u, 0x10800000u, fn_flash, 605u, fl_command, fl_command_s, length, buffer);
    (void)audio_uart_send_bytes(buffer, (uint32_t)length);
    crc = codec_dfu_crc32_update_58fcf0(0xffffffffu, g2_codec_dfu_flash_size,
                                        g2_codec_dfu_flash_image);
    (void)audio_uart_send_bytes(&crc, 4u);

    DFU_LOG(4u, 0x10000000u, fn_flash, 611u, fl_wait_sta, fl_wait_sta_s);
    if (semantic_CodecWaitForUartToken(token_sta, CODEC_FLASH_START_TIMEOUT) < 0) {
        DFU_LOG(2u, 0x08000000u, fn_flash, 613u, fl_sta_err, fl_sta_err_s);
        return -1;
    }
    DFU_LOG(4u, 0x10000000u, fn_flash, 616u, fl_sta_ok, fl_sta_ok_s);
    DFU_LOG(4u, 0x10000000u, fn_flash, 618u, fl_download, fl_download_s);

    offset = 0;
    while (total > 0) {
        chunk = total > CODEC_FLASH_CHUNK ? CODEC_FLASH_CHUNK : total;
        DFU_LOG(4u, 0x10800000u, fn_flash, 626u, fl_chunk, fl_chunk_s, total, chunk);
        (void)audio_uart_send_bytes(image + offset, (uint32_t)chunk);
        DFU_LOG(4u, 0x10000000u, fn_flash, 630u, fl_wait_fin, fl_wait_fin_s);
        if (semantic_CodecWaitForUartToken(token_fin, CODEC_TOKEN_TIMEOUT) < 0) {
            DFU_LOG(2u, 0x08000000u, fn_flash, 633u, fl_fin_err, fl_fin_err_s);
            return -1;
        }
        DFU_LOG(4u, 0x10000000u, fn_flash, 636u, fl_fin_ok, fl_fin_ok_s);
        total -= chunk;
        offset += chunk;
        if (total > 0) {
            DFU_LOG(4u, 0x10000000u, fn_flash, 644u, fl_wait_sta, fl_wait_sta_s);
            if (semantic_CodecWaitForUartToken(token_sta, CODEC_TOKEN_TIMEOUT) < 0) {
                DFU_LOG(2u, 0x08000000u, fn_flash, 646u, fl_sta_err, fl_sta_err_s);
                return -1;
            }
            DFU_LOG(4u, 0x10000000u, fn_flash, 649u, fl_sta_ok, fl_sta_ok_s);
        }
    }
    if (semantic_CodecWaitForUartToken(token_result, 3000) == 0 &&
        semantic_CodecWaitForUartToken(token_succ, 2000) == 0) {
        DFU_LOG(3u, 0x0c000000u, fn_flash, 657u, fl_ok, fl_ok_s);
        return 0;
    }
    DFU_LOG(2u, 0x08000000u, fn_flash, 654u, fl_failed, fl_failed_s);
    return -1;
}

/* 0x579cbc. The only caller passes 0; the argument is unused. Bring-up at
 * 230400 baud: power-cycle the codec, then send 0xEF every millisecond
 * (10001 tries) until the boot ROM answers 'M'. */
int32_t SVC_CodecDfu(uint32_t reserved)
{
    const uint32_t stage2_baud = CODEC_STAGE2_BAUD;
    int32_t result = -1;
    int32_t attempts;
    uint8_t sync[2];

    (void)reserved;
    DFU_LOG(4u, 0x10400000u, fn_dfu, 667u, dfu_baud, dfu_baud_s, CODEC_STAGE1_BAUD);
    if (semantic_CodecLoadFirmwarePackage() < 0) {
        DFU_LOG(1u, 0x04000000u, fn_dfu, 671u, dfu_load_err, dfu_load_err_s);
        return -1;
    }
    (void)audio_uart_session_open();
    if (codec_porting_uart_set_baud_58fab6(CODEC_STAGE1_BAUD) != 0) {
        DFU_LOG(2u, 0x08000000u, fn_dfu, 677u, uart_config_err, uart_config_err_s);
        goto done;
    }
    DRV_Gx8002_Reboot(1u);
    attempts = CODEC_SYNC_ATTEMPTS;
    sync[0] = 0xefu;
    (void)audio_uart_send_bytes(&sync[0], 1u);
    for (;;) {
        if (codec_uart_read(&sync[1], 1u) != 0u && sync[1] == 'M')
            break;
        (void)audio_uart_send_bytes(&sync[0], 1u);
        g2_delay_ms_4910f4(1u);
        if (attempts < 1) {
            DFU_LOG(2u, 0x08000000u, fn_dfu, 700u, dfu_m_timeout, dfu_m_timeout_s);
            goto done;
        }
        attempts--;
    }
    DFU_LOG(4u, 0x10000000u, fn_dfu, 706u, dfu_m_ok, dfu_m_ok_s);
    if (semantic_CodecReadBootHeader() < 0)
        goto done;
    if (semantic_CodecDownloadBootStage1(stage2_baud) < 0)
        goto done;
    if (semantic_CodecDownloadBootStage2() < 0)
        goto done;
    if (semantic_CodecFlashImage() < 0)
        goto done;
    (void)audio_uart_session_close();
    result = 0;
    DFU_LOG(3u, 0x0c000000u, fn_dfu, 723u, dfu_ok, dfu_ok_s);

done:
    if (result != 0) {
        DFU_LOG(1u, 0x04000000u, fn_dfu, 727u, dfu_failed, dfu_failed_s);
        (void)audio_uart_session_close();
    }
    DRV_Gx8002_Reboot(0u);
    semantic_CodecFreeFirmwareBuffers();
    return result;
}

/* 0x579fb8. Returns 0 upgraded, 1 already current, -1 package/parse error,
 * else the SVC_CodecDfu status. A failed codec version query forces the
 * upgrade. On success the RX ring is drained (100-tick byte reads) and the
 * package version is cached big-endian in g2_gx8002_version. */
int32_t SVC_CodecCheckAndUpgrade(uint8_t force)
{
    uint32_t sink;
    uint32_t package_version = 0u;
    uint32_t codec_version = 0u;
    uint8_t version_bytes[4];
    char codec_text[32];
    char package_text[32];
    int32_t status;

    audio_uart_buffer_zero(package_text, sizeof(package_text), 0u);
    audio_uart_buffer_zero(codec_text, sizeof(codec_text), 0u);
    DRV_Gx8002_Reboot(0u);
    DFU_LOG(3u, 0x0c000000u, fn_check, 751u, chk_start, chk_start_s);

    status = semantic_CodecGetPackageVersion(&package_version);
    if (status != 0) {
        DFU_LOG(1u, 0x04400000u, fn_check, 757u, chk_pkg_err, chk_pkg_err_s, status);
        return -1;
    }
    semantic_CodecFormatVersion(package_version, package_text, sizeof(package_text));
    DFU_LOG(3u, 0x0c800000u, fn_check, 762u, chk_pkg, chk_pkg_s, package_text, package_version);

    if (force == 0u) {
        audio_uart_buffer_zero(version_bytes, sizeof(version_bytes), 0u);
        status = GX8002_ReadVersion(version_bytes, GX8002_SVC_TIMEOUT);
        if (status == 0) {
            status = semantic_CodecParseVersionBytes(version_bytes, &codec_version);
            if (status != 0) {
                DFU_LOG(1u, 0x04400000u, fn_check, 777u, chk_parse_err, chk_parse_err_s, status);
                return -1;
            }
            semantic_CodecFormatVersion(codec_version, codec_text, sizeof(codec_text));
            DFU_LOG(3u, 0x0c800000u, fn_check, 782u, chk_current, chk_current_s, codec_text,
                    codec_version);
            if (codec_version == package_version) {
                DFU_LOG(3u, 0x0c000000u, fn_check, 786u, chk_same, chk_same_s);
                return 1;
            }
            DFU_LOG(3u, 0x0c000000u, fn_check, 790u, chk_diff, chk_diff_s);
        } else {
            DFU_LOG(1u, 0x04400000u, fn_check, 770u, chk_query_err, chk_query_err_s, status);
        }
    } else {
        DFU_LOG(3u, 0x0c000000u, fn_check, 792u, chk_force, chk_force_s);
    }

    status = SVC_CodecDfu(0u);
    if (status != 0) {
        DFU_LOG(1u, 0x04400000u, fn_check, 801u, chk_failed, chk_failed_s, status);
        return status;
    }
    (void)audio_uart_session_open();
    while (codec_read_byte_deadline((uint8_t *)&sink, 100u) == 1u) {
    }
    (void)audio_uart_session_close();
    DFU_LOG(3u, 0x0c400000u, fn_check, 814u, chk_ok, chk_ok_s, package_text);
    g2_gx8002_version[0] = (uint8_t)(package_version >> 24);
    g2_gx8002_version[1] = (uint8_t)(package_version >> 16);
    g2_gx8002_version[2] = (uint8_t)(package_version >> 8);
    g2_gx8002_version[3] = (uint8_t)package_version;
    return 0;
}
