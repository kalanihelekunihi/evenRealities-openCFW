#ifndef OPEN_CFW_TINYFRAME_G2_CONFIG_H
#define OPEN_CFW_TINYFRAME_G2_CONFIG_H

#include <stdint.h>

/* Recovered from the official G2 2.2.6.10 Apollo-main image. */
#define TF_ID_BYTES 2
#define TF_LEN_BYTES 2
#define TF_TYPE_BYTES 2

#define TF_CKSUM_TYPE TF_CKSUM_CRC16
#define TF_USE_SOF_BYTE 1
#define TF_SOF_BYTE 0x01

typedef uint16_t TF_TICKS;
typedef uint8_t TF_COUNT;

#define TF_MAX_PAYLOAD_RX 0x6000
#define TF_SENDBUF_LEN 0x400

#define TF_MAX_ID_LST 128
#define TF_MAX_TYPE_LST 32
#define TF_MAX_GEN_LST 10

#define TF_PARSER_TIMEOUT_TICKS 100
#define TF_USE_MUTEX 0

/*
 * TF_Error is the G2 two-sink error log (stock TinyFrame.c, e.g.
 * TF_InitStatic 0x491752..0x4917A0). When audio_log_flags() 0x43D0CE has
 * bit 1, EasyLogger elog_output() 0x43D574 receives level 1, tag "TinyFrame"
 * (ROM 0x78C6C8), the IAR source path (ROM 0x6FE474), __func__, __LINE__
 * and "[TF] :error " format "\n"; when it has bit 0 or bit 2,
 * compressed_log_output() 0x43CE9E receives 0x04000000 | (argument count
 * << 22) and "[TinyFrame][TF] :error " format "\n" twice (ROM 0x71A188).
 * The ten stock line numbers are the generated TinyFrame.c's (pinned + 3
 * before TF_ClaimTx, + 5 after TF_InitStatic).
 */
#include <stdint.h>
uint32_t audio_log_flags(void);
void elog_output(uint8_t level, const char *tag, const char *file,
                 const char *func, const long line, const char *format, ...);
uint32_t compressed_log_output(uint32_t flags, const char *format,
                               const char *text, ...);
#define G2_TF_SOURCE_PATH \
    "D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\TinyFrame\\TinyFrame.c"
/* Every TF_Error in TinyFrame.c passes at most one argument. */
#define TF_Error(format, ...)                                                 \
    do {                                                                      \
        if (audio_log_flags() & 2u)                                           \
            elog_output(1u, "TinyFrame", G2_TF_SOURCE_PATH, __func__,         \
                        __LINE__, "[TF] :error " format "\n", ##__VA_ARGS__);  \
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))             \
            (void)compressed_log_output(                                      \
                0x04000000u __VA_OPT__(| (1u << 22)),                         \
                "[TinyFrame][TF] :error " format "\n",                        \
                "[TinyFrame][TF] :error " format "\n", ##__VA_ARGS__);        \
    } while (0)

#endif
