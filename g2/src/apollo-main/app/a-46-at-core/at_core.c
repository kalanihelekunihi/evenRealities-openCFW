/* eAT command core, stock D:\01_workspace\s200_ap510b_iar_git\platform\service\eAT\core\at_core.c
 * (path ROM 0x6f8834, module tag "at.core"). Native 0x5412e0..0x541579;
 * literal pool 0x54157c..0x5415b3.
 *
 * The context at RAM 0x2037bf5c holds the registry (linker table ROM
 * 0x6c9260..0x6c93af), the output sinks and the 256-byte reply buffer.
 * AT_Handler splits "AT^CMD=a=b" on '=' into three 256-byte slots
 * (RAM 0x2037b3c0) and dispatches by exact name match. */
#include <stdint.h>
#include <stddef.h>
#include <stdarg.h>
#include "g2_at_core.h"

#define AT_ARG_SLOTS 3u
#define AT_ARG_SIZE 0x100u
#define AT_OUT_SIZE 0x100u
#define AT_NAME_LIMIT 0x100u

enum {
    AT_FLAG_INIT = 1u,       /* set by AT_CoreInit */
    AT_FLAG_READY = 2u,      /* set by AT_CoreInit */
    AT_FLAG_RESTRICTED = 4u, /* only rows with G2_AT_CMD_RESTRICTED_OK run */
};

enum { AT_OUT_ALL = 0u, AT_OUT_CHANNEL1 = 1u, AT_OUT_CHANNEL2 = 2u };

typedef struct {
    uint32_t flags;                               /* +0x00 AT_FLAG_* */
    uint32_t state;                               /* +0x04 cleared at init */
    const g2_at_cmd_t *table;                     /* +0x08 */
    uint32_t count;                               /* +0x0c */
    uint32_t output_mask;                         /* +0x10 bit n: output[n] registered */
    uint8_t output_mode;                          /* +0x14 AT_OUT_* */
    uint8_t pad[3];                               /* +0x15 */
    g2_at_output_t output[G2_AT_OUTPUT_CHANNELS]; /* +0x18 */
    char out[AT_OUT_SIZE];                        /* +0x24 */
} g2_at_core_t;
_Static_assert(offsetof(g2_at_core_t, output) == 0x18, "output sinks at +0x18");
_Static_assert(offsetof(g2_at_core_t, out) == 0x24, "reply buffer at +0x24");

extern g2_at_core_t g2_at_core;                       /* RAM 0x2037bf5c */
extern char g2_at_core_args[AT_ARG_SLOTS][AT_ARG_SIZE]; /* RAM 0x2037b3c0 */
extern const g2_at_cmd_t g2_at_cmd_table_start[];     /* ROM 0x6c9260 */
extern const g2_at_cmd_t g2_at_cmd_table_end[];       /* ROM 0x6c93b0 */
extern const char g2_at_arg_delimiter[2];             /* ROM 0x78f538 "=" */

extern void at_port_init_57ddfc(void); /* registers output channel 2 */
extern void at_core_run_async_57de0a(g2_at_handler_t handler, const char *arg1,
                                     const char *arg2); /* copies args, spawns an 8 KiB thread */
extern char *strtok_r_57deb0(char *text, const char *delimiters, char **save);
extern void *aeabi_memset_43c0e4(void *dst, uint32_t len, int32_t value);
extern int32_t g2_audio_dump_snprintf(char *dst, uint32_t size, const char *format, ...); /* 0x44b728 */
extern int32_t g2_log_vformat(char *, uint32_t, const char *, va_list); /* 0x44b76c vsnprintf */
extern uint32_t g2_log_module_length(const char *text); /* strlen 0x44a43c */
extern int32_t g2_lfs_memcmp(const void *a, const void *b, uint32_t length); /* 0x4751c8 */
extern uint32_t audio_log_flags(void); /* 0x43d0ce */
extern void audio_log_extended(uint8_t, const char *, const char *, const char *, uint32_t, const char *, ...); /* 0x43d574 */
extern uint32_t compress_log_output(uint32_t, const char *, const char *, ...); /* 0x43ce9e */

static const char module_tag[] = "at.core"; /* ROM 0x78cbbc */
static const char source_file[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\platform\\service\\eAT\\core\\at_core.c"; /* ROM 0x6f8834 */
static const char fn_init[] = "AT_CoreInit";                           /* ROM 0x78a358 */
static const char init_fmt[] = "====AT_CoreInit[%d]====";              /* ROM 0x7755cc */
static const char init_fmt_short[] = "[at.core]====AT_CoreInit[%d]===="; /* ROM 0x752370 */
static const char fn_handler[] = "AT_Handler";                         /* ROM 0x78a364 */
static const char handler_fmt[] = "AT_Handler: %s";                    /* ROM 0x785150 */
static const char handler_fmt_short[] = "[at.core]AT_Handler: %s";     /* ROM 0x7755e4 */
static const char copy_fmt[] = "%s";                                   /* ROM 0x54157c */

/* 0x5412e0 */
void at_core_register_callback(uint8_t channel, g2_at_output_t output)
{
    if (channel < G2_AT_OUTPUT_CHANNELS) {
        g2_at_core.output[channel] = output;
        g2_at_core.output_mask |= 1u << channel;
    }
}

/* 0x541302 */
void AT_CoreInit(void)
{
    g2_at_core.table = g2_at_cmd_table_start;
    g2_at_core.count = (uint32_t)(g2_at_cmd_table_end - g2_at_core.table);
    at_port_init_57ddfc();
    g2_at_core.state = 0u;
    g2_at_core.flags |= AT_FLAG_INIT;
    g2_at_core.flags |= AT_FLAG_READY;
    if (audio_log_flags() & 2u)
        audio_log_extended(4u, module_tag, source_file, fn_init, 91u, init_fmt, g2_at_core.count);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        (void)compress_log_output(0x10400000u, init_fmt_short, init_fmt_short, g2_at_core.count);
}

/* 0x54136c: the log reports `command` after strtok_r has cut it at the first '='. */
void AT_Handler(char *command)
{
    char delimiter[2];
    char *save = NULL;
    uint8_t slots = 0u;
    char *token;

    __builtin_memcpy(delimiter, g2_at_arg_delimiter, sizeof delimiter);
    (void)aeabi_memset_43c0e4(g2_at_core_args, sizeof g2_at_core_args, 0);
    token = strtok_r_57deb0(command, delimiter, &save);
    while (token != NULL && slots < AT_ARG_SLOTS) {
        (void)g2_audio_dump_snprintf(g2_at_core_args[slots], AT_ARG_SIZE, copy_fmt, token);
        slots++;
        token = strtok_r_57deb0(NULL, delimiter, &save);
    }
    if (audio_log_flags() & 2u)
        audio_log_extended(4u, module_tag, source_file, fn_handler, 171u, handler_fmt, command);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        (void)compress_log_output(0x10400000u, handler_fmt_short, handler_fmt_short, command);
    at_core_dispatch_command(g2_at_core_args[0],
                             slots >= 2u ? g2_at_core_args[1] : NULL,
                             slots >= 3u ? g2_at_core_args[2] : NULL);
}

/* 0x541430: mode 0 fans out to sinks 1 and 2 (sink 0 is never written);
 * modes 1 and 2 select one sink. */
void at_core_output(const char *fmt, ...)
{
    va_list args;
    int32_t length;

    va_start(args, fmt);
    length = g2_log_vformat(g2_at_core.out, AT_OUT_SIZE, fmt, args);
    va_end(args);
    if (length < 1)
        return;
    switch (g2_at_core.output_mode) {
    case AT_OUT_ALL:
        for (uint32_t channel = 1u; channel < G2_AT_OUTPUT_CHANNELS; channel++) {
            if (((g2_at_core.output_mask >> channel) & 1u) && g2_at_core.output[channel] != NULL)
                g2_at_core.output[channel](g2_at_core.out, length);
        }
        break;
    case AT_OUT_CHANNEL1:
        if ((g2_at_core.output_mask & 2u) && g2_at_core.output[1] != NULL)
            g2_at_core.output[1](g2_at_core.out, length);
        break;
    case AT_OUT_CHANNEL2:
        if ((g2_at_core.output_mask & 4u) && g2_at_core.output[2] != NULL)
            g2_at_core.output[2](g2_at_core.out, length);
        break;
    default:
        break;
    }
}

/* 0x5414ba: every row whose name matches runs; in restricted mode the first
 * matching row without G2_AT_CMD_RESTRICTED_OK ends the scan. */
void at_core_dispatch_command(const char *command, const char *arg1, const char *arg2)
{
    uint32_t length;

    if ((g2_at_core.flags & (AT_FLAG_INIT | AT_FLAG_READY)) != (AT_FLAG_INIT | AT_FLAG_READY) ||
        command == NULL)
        return;
    length = g2_log_module_length(command);
    if (length >= AT_NAME_LIMIT)
        return;
    for (uint32_t i = 0u; i < g2_at_core.count; i++) {
        const g2_at_cmd_t *row = &g2_at_core.table[i];
        if (g2_log_module_length(row->name) != length ||
            g2_lfs_memcmp(row->name, command, length) != 0)
            continue;
        if ((g2_at_core.flags & AT_FLAG_RESTRICTED) && !(row->type & G2_AT_CMD_RESTRICTED_OK))
            return;
        if (row->handler == NULL)
            continue;
        if ((row->type & G2_AT_CMD_ASYNC) == 0u)
            (void)row->handler(arg1, arg2);
        else
            at_core_run_async_57de0a(row->handler, arg1, arg2);
    }
}
