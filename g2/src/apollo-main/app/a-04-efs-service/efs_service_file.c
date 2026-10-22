/* EFS file helpers, stock
 * D:\01_workspace\s200_ap510b_iar_git\platform\protocols\efs_service\efs_service.c
 * (log tag "efs.service").
 * Native 0x456580..0x456bac: log-path validators 0x456580/0x456606, littlefs
 * flags -> fopen mode 0x45669a (mode strings inline at 0x4567a0..0x4567b7),
 * file size 0x4566d8, _evenEfsReplyToAPP 0x456722, _fileCaculateCRC 0x4567b8;
 * the literal pool 0x456bac..0x456c0b follows. _efsFileCmdParse 0x456c0c is
 * the caller of the path validators and _fileCaculateCRC.
 *
 * The mode helper and size helper are byte-for-byte twins of the OTA service's
 * semantic_OtaSelectFlashOps 0x4448f4 / semantic_OtaFileSize 0x44494c; each
 * service compiles its own static copy. */
#include <stdint.h>
#include <stddef.h>

extern void *file_open(const char *path, const char *mode);      /* 0x474550 */
extern int32_t file_close(void *file);                           /* 0x4745f4 */
extern uint32_t file_read(void *buffer, uint32_t size, uint32_t count, void *file); /* 0x474634 */
extern int32_t file_seek(void *file, int32_t offset, int32_t origin); /* 0x474814 */
extern int32_t file_tell(void *file);                            /* 0x474870 */
extern uint32_t Thread_MsgEfsTxByBle(uint8_t type, uint8_t command, const void *payload,
                                     uint16_t length);           /* 0x475dfa */
extern void file_crc32c_update_47cbc4(const uint8_t *data, uint32_t length, uint32_t *crc);
extern void *aeabi_memset_43c0e4(void *dst, uint32_t len, int32_t value);
extern uint32_t g2_log_module_length(const char *text);          /* 0x44a43c strlen */
extern int32_t audio_l2c_strncmp(const char *a, const char *b, uint32_t len); /* 0x44b610 */
extern int32_t audio_uart_font_path_compare(const char *a, const char *b); /* 0x46cacc strcmp */
extern uint32_t strtoul_48d874(const char *text, char **end, int32_t base); /* _Stoulx(.., NULL) */
extern uint32_t audio_log_flags(void);                           /* 0x43d0ce */
extern void audio_log_extended(uint8_t, const char *, const char *, const char *, uint32_t,
                               const char *, ...);               /* 0x43d574 */
extern uint32_t compress_log_output(uint32_t, const char *, const char *, ...); /* 0x43ce9e */

/* EFS transfer object (RAM 0x20071cc8); only the open flag at +4 is used here. */
extern uint8_t audio_efs_transfer_state[];                       /* RAM 0x20071cc8 */
#define EFS_FILE_OPEN_FLAG (audio_efs_transfer_state[4])
/* 4 KiB CRC staging buffer (RAM 0x2035be08). */
#define EFS_CRC_CHUNK 0x1000u
extern uint8_t g2_efs_crc_buffer[EFS_CRC_CHUNK];                 /* RAM 0x2035be08 */

#define EFS_LFS_O_RDONLY 1u   /* littlefs flags fed to the mode helper */

static const char module_tag[] = "efs.service";                  /* ROM 0x78a94c */
static const char source_file[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\platform\\protocols\\efs_service\\efs_service.c"; /* ROM 0x6e772c */
static const char reply_fn[] = "_evenEfsReplyToAPP";             /* ROM 0x77f1bc */
static const char crc_fn[] = "_fileCaculateCRC";                 /* ROM 0x77f1d0 */
static const char tp_prefix[] = "/log/tp/tp_";                   /* ROM 0x78a940 */
static const char bin_suffix[] = ".bin";                         /* ROM 0x78d4ac */
static const char compress_prefix[] = "/log/compress_log_";      /* ROM 0x77f194 */
static const char hardfault_path[] = "/log/hardfault.txt";       /* ROM 0x77f1a8 */
static const char mode_w_plus[] = "w+";                          /* ROM 0x4567a0 */
static const char mode_a_plus[] = "a+";                          /* ROM 0x4567a4 */
static const char mode_r_plus[] = "r+";                          /* ROM 0x4567a8 */
static const char mode_a[] = "a";                                /* ROM 0x4567ac */
static const char mode_w[] = "w";                                /* ROM 0x4567b0 */
static const char mode_r[] = "r";                                /* ROM 0x4567b4 */

/* Stock pairs every message with a "[efs.service]"-prefixed compact copy; the
 * ROM comments give plain / compact addresses. */
#define EFS_LOG(fn, level, line, mask, fmt, ...) do { \
    if (audio_log_flags() & 2u) \
        audio_log_extended((level), module_tag, source_file, (fn), (line), fmt, ##__VA_ARGS__); \
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u)) \
        (void)compress_log_output((mask), "[efs.service]" fmt, "[efs.service]" fmt, ##__VA_ARGS__); \
} while (0)

#define EFS_FILE_CLOSE(slot, err) do { \
    if (*(slot) == NULL) { (err) = 0; } \
    else { (err) = file_close(*(slot)); *(slot) = NULL; } \
} while (0)

/* 1 when path is "/log/tp/tp_<decimal>.bin" with a non-zero number that
 * consumes everything up to the suffix. */
uint8_t efs_is_tracepoint_log_path_456580(const char *path)
{
    uint32_t prefix_len = g2_log_module_length(tp_prefix);
    uint32_t suffix_len = g2_log_module_length(bin_suffix);
    uint32_t path_len;
    char *end;

    if (path == NULL)
        return 0u;
    path_len = g2_log_module_length(path);
    if (suffix_len + prefix_len >= path_len ||
        audio_l2c_strncmp(path, tp_prefix, prefix_len) != 0 ||
        audio_uart_font_path_compare(path + path_len - suffix_len, bin_suffix) != 0)
        return 0u;
    end = NULL;
    if (strtoul_48d874(path + prefix_len, &end, 10) == 0u ||
        end != path + path_len - suffix_len)
        return 0u;
    return 1u;
}

/* 1 for "/log/hardfault.txt" or "/log/compress_log_<decimal>.bin"; unlike the
 * tracepoint check the parsed number itself is not tested. */
uint8_t efs_is_device_log_path_456606(const char *path)
{
    uint32_t path_len;
    uint32_t prefix_len;
    uint32_t suffix_len;
    char *end;

    if (path == NULL)
        return 0u;
    if (audio_uart_font_path_compare(path, hardfault_path) == 0)
        return 1u;
    path_len = g2_log_module_length(path);
    prefix_len = g2_log_module_length(compress_prefix);
    suffix_len = g2_log_module_length(bin_suffix);
    if (suffix_len + prefix_len >= path_len ||
        audio_l2c_strncmp(path, compress_prefix, prefix_len) != 0 ||
        audio_uart_font_path_compare(path + path_len - suffix_len, bin_suffix) != 0)
        return 0u;
    end = NULL;
    (void)strtoul_48d874(path + prefix_len, &end, 10);
    return end == path + path_len - suffix_len;
}

/* littlefs open flags -> fopen mode. Stock tests (flags & 3) first, so every
 * littlefs access mode (RDONLY=1 included) takes the "+" branch and the
 * WRONLY-only branch is unreachable; kept as written. */
const char *efs_open_mode_from_flags_45669a(uint32_t flags)
{
    if ((flags & 3u) != 0u) {
        if ((flags & 0x100u) != 0u)            /* LFS_O_CREAT */
            return (flags & 0x400u) != 0u ? mode_w_plus : mode_a_plus; /* LFS_O_TRUNC */
        return mode_r_plus;
    }
    if ((flags & 2u) != 0u) {                  /* LFS_O_WRONLY */
        if ((flags & 0x800u) != 0u)            /* LFS_O_APPEND */
            return mode_a;
        if ((flags & 0x100u) != 0u)
            return (flags & 0x400u) != 0u ? mode_w : mode_a;
        return mode_w;
    }
    return mode_r;
}

/* File size by seeking to the end; the original position is restored. */
int32_t efs_file_size_4566d8(void *file)
{
    int32_t position;
    int32_t size;

    if (file == NULL)
        return -1;
    position = file_tell(file);
    if (position < 0)
        return -1;
    if (file_seek(file, 0, 2) != 0)
        return -1;
    size = file_tell(file);
    (void)file_seek(file, position, 0);
    return size;
}

/* Sends the two-byte {subcommand, status} reply for an EFS command. */
void _evenEfsReplyToAPP(uint8_t command, uint8_t subcommand, uint8_t status)
{
    uint8_t reply[2];

    (void)aeabi_memset_43c0e4(reply, sizeof reply, 0);
    reply[0] = subcommand;
    reply[1] = status;
    EFS_LOG(reply_fn, 4u, 0x106u, 0x10400000u, "status = %d", status); /* ROM 0x78a958 / 0x76b4ac */
    (void)Thread_MsgEfsTxByBle(1u, command, reply, 2u);
}

/* Streams a whole file through the CRC-32C helper in 4 KiB chunks; 1 = ok. */
uint8_t _fileCaculateCRC(void **file, const char *path, uint32_t *size, uint32_t *crc)
{
    int32_t ret = -1;
    int32_t length;
    int32_t err;
    uint32_t count;
    uint32_t rest;

    *file = file_open(path, efs_open_mode_from_flags_45669a(EFS_LFS_O_RDONLY));
    if (*file == NULL) {
        EFS_FILE_OPEN_FLAG = 0u;
    } else {
        ret = 0;
        EFS_FILE_OPEN_FLAG = 1u;
    }
    if (ret < 0) {
        EFS_LOG(crc_fn, 1u, 0x11fu, 0x04800000u,
                "ERR-Open failed %s : %d", path, ret); /* ROM 0x776ff4 / 0x749c54 */
        return 0u;
    }

    length = efs_file_size_4566d8(*file);
    if (length < 0) {
        EFS_LOG(crc_fn, 1u, 0x125u, 0x04800000u,
                "ERR-get size failed %s : %d", path, length); /* ROM 0x76b4c8 / 0x73e870 */
        EFS_FILE_CLOSE(file, err);
        if (err < 0)
            EFS_LOG(crc_fn, 1u, 0x128u, 0x04800000u,
                    "ERR-Close failed %s : %d", path, err); /* ROM 0x76b4e4 / 0x749c7c */
        return 0u;
    }
    *size = (uint32_t)length;
    EFS_LOG(crc_fn, 4u, 0x12eu, 0x10400000u, "File size: %ld bytes\n", *size); /* ROM 0x77700c / 0x75411c */

    for (uint32_t i = 0u; i < (*size >> 12); i++) {
        count = file_read(g2_efs_crc_buffer, 1u, EFS_CRC_CHUNK, *file);
        if (count != EFS_CRC_CHUNK) {
            EFS_LOG(crc_fn, 1u, 0x133u, 0x04400000u, "read failed %d", count); /* ROM 0x785d40 / 0x76b500 */
            EFS_FILE_CLOSE(file, err);
            if (err < 0)
                EFS_LOG(crc_fn, 1u, 0x136u, 0x04800000u,
                        "ERR-Close failed %s : %d", path, err); /* ROM 0x76b4e4 / 0x749c7c */
            return 0u;
        }
        file_crc32c_update_47cbc4(g2_efs_crc_buffer, EFS_CRC_CHUNK, crc);
    }

    rest = *size & (EFS_CRC_CHUNK - 1u);
    if (rest != 0u) {
        count = file_read(g2_efs_crc_buffer, 1u, rest, *file);
        if (count != rest) {
            EFS_LOG(crc_fn, 1u, 0x141u, 0x04800000u,
                    "read failed %d(%d)", count, rest); /* ROM 0x77f1e4 / 0x75fab0 */
            EFS_FILE_CLOSE(file, err);
            if (err < 0)
                EFS_LOG(crc_fn, 1u, 0x144u, 0x04800000u,
                        "ERR-Close failed %s : %d", path, err); /* ROM 0x76b4e4 / 0x749c7c */
            return 0u;
        }
        file_crc32c_update_47cbc4(g2_efs_crc_buffer, rest, crc);
    }

    EFS_FILE_CLOSE(file, err);
    if (err < 0)
        EFS_LOG(crc_fn, 1u, 0x14cu, 0x04800000u,
                "ERR-Close failed %s : %d", path, err); /* ROM 0x76b4e4 / 0x749c7c */
    EFS_LOG(crc_fn, 4u, 0x14eu, 0x10c00000u,
            "filePath = %s, fileSize = %d, calc CRC = 0x%x", path, *size, *crc); /* ROM 0x733b24 / 0x7149e0 */
    return 1u;
}
