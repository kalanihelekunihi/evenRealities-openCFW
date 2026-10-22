/* Product FreeRTOS-Plus-CLI filesystem module, remaining functions.
 * Stock source: D:\01_workspace\s200_ap510b_iar_git\kernel\FreeRTOS-Plus-CLI\
 *               prvCommand\prvCommand_filesystem.c
 * Native: "free" handler 0x57f550..0x57f683 (pool 0x57ffa8..0x57fff3) and
 * the module registrar 0x57ff40..0x57ff9d (pool 0x5800c4..0x5800ff).
 * The other commands of this file (ls .. df and the TLSF walker 0x57f530)
 * are in system/u-07/prvCommand_filesystem.c; rename 0x57f68c, xip
 * 0x57f8bc, file2xip 0x57f980 and xip2file 0x57fcac have no inventory
 * rows.
 *
 * "free" reports the file/codec TLSF heap (cell RAM 0x20074abc), a
 * 0x70800-byte (450 KiB) pool. Its "TLSF Overhead" line is
 * tlsf_pool_overhead() plus tlsf_size(), the latter folded to 0xc74. */
#include <stddef.h>
#include <stdint.h>
#include "cli_commands.h"

#define FREE_POOL_BYTES 0x70800u      /* 460800 */
#define FREE_TLSF_CONTROL_BYTES 0xc74u /* tlsf_size(): sizeof(control_t) */
#define FREE_WARN_PERCENT 91          /* > 90 % */
#define FREE_CAUTION_PERCENT 76       /* > 75 % */

/* Totals filled by cli_heap_walker_57f530. */
typedef struct {
    uint32_t free_bytes;  /* +0x0 */
    uint32_t used_bytes;  /* +0x4 */
    uint32_t blocks;      /* +0x8 */
    uint32_t free_blocks; /* +0xc */
} g2_heap_walk_totals_t;
_Static_assert(sizeof(g2_heap_walk_totals_t) == 16u, "walker totals");

extern g2_cli_command_t g2_cli_cmd_ls_20003234;       /* "ls", 0 params */
extern g2_cli_command_t g2_cli_cmd_cat_20003244;      /* "cat", 1 */
extern g2_cli_command_t g2_cli_cmd_rm_20003254;       /* "rm", 1 */
extern g2_cli_command_t g2_cli_cmd_cd_20003264;       /* "cd", 1 */
extern g2_cli_command_t g2_cli_cmd_mkdir_20003274;    /* "mkdir", 1 */
extern g2_cli_command_t g2_cli_cmd_touch_20003284;    /* "touch", 1 */
extern g2_cli_command_t g2_cli_cmd_pwd_20003294;      /* "pwd", 0 */
extern g2_cli_command_t g2_cli_cmd_mv_200032a4;       /* "mv", 2 */
extern g2_cli_command_t g2_cli_cmd_md5_200032b4;      /* "md5", 1 */
extern g2_cli_command_t g2_cli_cmd_df_200032c4;       /* "df", 0 */
extern g2_cli_command_t g2_cli_cmd_free_200032d4;     /* "free", 0 */
extern g2_cli_command_t g2_cli_cmd_rename_200032e4;   /* "rename", 2 */
extern g2_cli_command_t g2_cli_cmd_xip_200032f4;      /* "xip", 2 */
extern g2_cli_command_t g2_cli_cmd_file2xip_20003304; /* "file2xip", 2 */
extern g2_cli_command_t g2_cli_cmd_xip2file_20003314; /* "xip2file", 3 */

extern void *g2_codec_heap_pool; /* RAM 0x20074abc: tlsf_t of the file/codec heap */
extern void *tlsf_get_pool_4d0716(void *tlsf);
extern void tlsf_walk_pool_4d0580(void *pool, void (*walker)(void *, uint32_t, int32_t, void *),
                                  void *user);
extern uint32_t tlsf_pool_overhead_4d05fa(void);
extern void cli_heap_walker_57f530(void *block, uint32_t size, int32_t used, void *user);
extern void *aeabi_memset_43c0e4(void *dst, uint32_t len, int32_t value);

static const char s_free_no_tlsf[] = "TLSF not initialized\r\n";     /* ROM 0x77aa74 */
static const char s_free_no_pool[] = "TLSF pool not available\r\n";  /* ROM 0x76fef0 */
static const char s_free_header[] =
    "               total        used        free      shared  buff/cache   available\r\n"; /* ROM 0x6e94b4 */
static const char s_free_row[] =
    "Mem:        %8lu    %8lu    %8lu           0           0    %8lu\r\n"; /* ROM 0x7049f0 */
static const char s_free_details[] = "\r\n=== TLSF Memory Details ===\r\n"; /* ROM 0x763c90 */
static const char s_free_pool[] = "Pool Size:         %lu KB (%lu bytes)\r\n"; /* ROM 0x74cc74 */
static const char s_free_overhead[] = "TLSF Overhead:     %lu bytes\r\n";        /* ROM 0x763cb0 */
static const char s_free_usable[] = "Usable Memory:     %lu KB (%lu bytes)\r\n"; /* ROM 0x74cc9c */
static const char s_free_used[] = "Used Memory:       %lu KB (%lu bytes)\r\n";   /* ROM 0x74ccc4 */
static const char s_free_free[] = "Free Memory:       %lu KB (%lu bytes)\r\n";   /* ROM 0x74ccec */
static const char s_free_usage[] = "Memory Usage:      %d%%\r\n";                 /* ROM 0x76ff0c */
static const char s_free_blocks[] = "Total Blocks:      %lu\r\n";                 /* ROM 0x76ff28 */
static const char s_free_free_blocks[] = "Free Blocks:       %lu\r\n";            /* ROM 0x76ff44 */
static const char s_free_used_blocks[] = "Used Blocks:       %lu\r\n";            /* ROM 0x76ff60 */
static const char s_free_rule[] = "===========================\r\n";            /* ROM 0x763cd0 */
static const char s_free_warning[] = "WARNING: Memory usage is very high (>90%%)\r\n"; /* ROM 0x736d64 */
static const char s_free_caution[] = "CAUTION: Memory usage is high (>75%%)\r\n";     /* ROM 0x74cd14 */

int32_t cli_cmd_free_57f550(char *write_buffer, size_t write_buffer_len, const char *command_string);
void cli_register_filesystem_commands_57ff40(void);

int32_t cli_cmd_free_57f550(char *write_buffer, size_t write_buffer_len, const char *command_string)
{
    g2_heap_walk_totals_t totals;
    void *pool;
    uint32_t usable;
    uint32_t overhead;
    uint32_t percent;
    uint32_t pool_bytes = FREE_POOL_BYTES;

    (void)write_buffer;
    (void)write_buffer_len;
    (void)command_string;
    if (g2_codec_heap_pool == NULL) {
        audio_ble_hci_boot_log_4733ee(s_free_no_tlsf);
        return 0;
    }
    pool = tlsf_get_pool_4d0716(g2_codec_heap_pool);
    if (pool == NULL) {
        audio_ble_hci_boot_log_4733ee(s_free_no_pool);
        return 0;
    }
    (void)aeabi_memset_43c0e4(&totals, sizeof(totals), 0);
    tlsf_walk_pool_4d0580(pool, cli_heap_walker_57f530, &totals);
    usable = totals.free_bytes + totals.used_bytes;
    overhead = tlsf_pool_overhead_4d05fa() + FREE_TLSF_CONTROL_BYTES;
    percent = usable != 0u ? (totals.used_bytes * 100u) / usable : 0u;

    audio_ble_hci_boot_log_4733ee(s_free_header);
    audio_ble_hci_boot_log_4733ee(s_free_row, usable >> 10, totals.used_bytes >> 10,
                                  totals.free_bytes >> 10, totals.free_bytes >> 10);
    audio_ble_hci_boot_log_4733ee(s_free_details);
    audio_ble_hci_boot_log_4733ee(s_free_pool, pool_bytes >> 10, pool_bytes);
    audio_ble_hci_boot_log_4733ee(s_free_overhead, overhead);
    audio_ble_hci_boot_log_4733ee(s_free_usable, usable >> 10, usable);
    audio_ble_hci_boot_log_4733ee(s_free_used, totals.used_bytes >> 10, totals.used_bytes);
    audio_ble_hci_boot_log_4733ee(s_free_free, totals.free_bytes >> 10, totals.free_bytes);
    audio_ble_hci_boot_log_4733ee(s_free_usage, percent);
    audio_ble_hci_boot_log_4733ee(s_free_blocks, totals.blocks);
    audio_ble_hci_boot_log_4733ee(s_free_free_blocks, totals.free_blocks);
    audio_ble_hci_boot_log_4733ee(s_free_used_blocks, totals.blocks - totals.free_blocks);
    audio_ble_hci_boot_log_4733ee(s_free_rule);
    if ((int32_t)percent >= FREE_WARN_PERCENT)
        audio_ble_hci_boot_log_4733ee(s_free_warning);
    else if ((int32_t)percent >= FREE_CAUTION_PERCENT)
        audio_ble_hci_boot_log_4733ee(s_free_caution);
    return 0;
}

void cli_register_filesystem_commands_57ff40(void)
{
    (void)freertos_cli_register_command_5847ac(&g2_cli_cmd_ls_20003234);
    (void)freertos_cli_register_command_5847ac(&g2_cli_cmd_cat_20003244);
    (void)freertos_cli_register_command_5847ac(&g2_cli_cmd_rm_20003254);
    (void)freertos_cli_register_command_5847ac(&g2_cli_cmd_cd_20003264);
    (void)freertos_cli_register_command_5847ac(&g2_cli_cmd_mkdir_20003274);
    (void)freertos_cli_register_command_5847ac(&g2_cli_cmd_touch_20003284);
    (void)freertos_cli_register_command_5847ac(&g2_cli_cmd_pwd_20003294);
    (void)freertos_cli_register_command_5847ac(&g2_cli_cmd_mv_200032a4);
    (void)freertos_cli_register_command_5847ac(&g2_cli_cmd_md5_200032b4);
    (void)freertos_cli_register_command_5847ac(&g2_cli_cmd_df_200032c4);
    (void)freertos_cli_register_command_5847ac(&g2_cli_cmd_free_200032d4);
    (void)freertos_cli_register_command_5847ac(&g2_cli_cmd_rename_200032e4);
    (void)freertos_cli_register_command_5847ac(&g2_cli_cmd_xip_200032f4);
    (void)freertos_cli_register_command_5847ac(&g2_cli_cmd_file2xip_20003304);
    (void)freertos_cli_register_command_5847ac(&g2_cli_cmd_xip2file_20003314);
}
