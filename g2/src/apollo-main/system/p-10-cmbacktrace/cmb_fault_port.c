/* G2 vendor additions to the CmBacktrace port (armink/CmBacktrace 7371448,
 * cm_backtrace/cm_backtrace.c, configured by
 * g2/config-recovered/cmbacktrace/g2-config/cmb_user_cfg.h + cmb_g2_port.h).
 * The library itself (0x5939a0..0x5942c7 and the vendor-patched
 * cm_backtrace_fault 0x5944bc..0x5947af) is built from the pinned upstream file
 * through the manifest's generated patch (U8 cmbacktrace part); this file keeps
 * only the two product functions the vendor inserted into that TU.
 *
 * Native 0x5942c8..0x5942ff (task state names) and 0x594334..0x594483 (thread
 * table, also called by the CLI "system info" command); literal pool
 * 0x594484..0x5944bb. The patched cm_backtrace_fault calls
 * cmb_dump_thread_table_594334() after print_call_stack() and then commits the
 * crash-log record (0x47dac0). */
#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

#define CMB_TASK_DUMP_MAX 40u
#define CMB_TASK_NAME_COLUMN 20
#define CMB_LINE_SIZE 0x80u

/* FreeRTOS 10.5.1 TaskStatus_t (configSTACK_DEPTH_TYPE uint16_t). */
typedef struct {
    void *handle;              /* +0x00 TCB; TCB +0x30 is pxStack */
    const char *name;          /* +0x04 */
    uint32_t number;           /* +0x08 */
    uint8_t state;             /* +0x0c eTaskState */
    uint32_t priority;         /* +0x10 */
    uint32_t base_priority;    /* +0x14 */
    uint32_t run_time;         /* +0x18 */
    void *stack_base;          /* +0x1c */
    uint16_t stack_high_water; /* +0x20 words */
} g2_task_status_t;
_Static_assert(sizeof(g2_task_status_t) == 0x24, "stock TaskStatus_t");

extern g2_task_status_t g2_cmb_task_status[CMB_TASK_DUMP_MAX]; /* RAM 0x20069028 */
extern char g2_cmb_line[CMB_LINE_SIZE];       /* RAM 0x20071a48 */

extern void crash_record_printf_47da78(const char *format, ...);
extern void audio_ble_hci_boot_log_4733ee(const char *format, ...); /* console printf */
extern int32_t g2_audio_dump_snprintf(char *dst, uint32_t size, const char *format, ...); /* 0x44b728 */
extern void *audio_settings_copy_text(void *dst, const void *src, uint32_t len); /* 0x44b5a0 strncpy */
extern void audio_uart_buffer_zero(void *dst, uint32_t size, uint32_t value);   /* 0x43c0e4 memset */
extern uint32_t uxTaskGetSystemState_454f38(g2_task_status_t *status, uint32_t count,
                                            uint32_t *total_run_time);
extern uint32_t uxTaskGetNumberOfTasks(void); /* 0x454f10 */

static const char state_running[] = "RUNNING";     /* ROM 0x78d194 */
static const char state_ready[] = "READY";         /* ROM 0x78d19c */
static const char state_blocked[] = "BLOCKED";     /* ROM 0x78d1a4 */
static const char state_suspended[] = "SUSPENDED"; /* ROM 0x78a604 */
static const char state_deleted[] = "DELETED";     /* ROM 0x78d1ac */
static const char state_unknown[] = "UNKNOWN";     /* ROM 0x78d1b4 */
static const char table_banner[] =
    "\n============================= Thread Info ==========================\n"; /* ROM 0x6f8a74 */
static const char table_header_fmt[] = "%-10s %-*s %-12s %-6s %-12s %-10s %-12s"; /* ROM 0x74832c */
static const char col_id[] = "Thread ID";         /* ROM 0x78a610 */
static const char col_name[] = "Name";            /* ROM 0x78d1bc */
static const char col_state[] = "State";          /* ROM 0x78d1c4 */
static const char col_prio[] = "Prio";            /* ROM 0x78d1cc */
static const char col_stack_addr[] = "StackAddr"; /* ROM 0x78a61c */
static const char col_stack_size[] = "StackSize"; /* ROM 0x78a628 */
static const char col_min_free[] = "MinFree";     /* ROM 0x78d1d4 */
static const char table_row_fmt[] =
    "Thread %-4lu %-*s %-12s %-6lu 0x%08X %-10u %-12u"; /* ROM 0x727574 */
static const char line_fmt[] = "%s\n";            /* ROM 0x59449c */
static const char newline[] = "\n";               /* ROM 0x5944a0 */
static const char table_rule[] =
    "===================================================================\n"; /* ROM 0x6f8abc */
static const char table_truncated[] = "Warning: Only showing first %d tasks\n"; /* ROM 0x748354 */

/* eTaskState -> name. */
const char *cmb_task_state_name_5942c8(uint8_t state)
{
    switch (state) {
    case 0u:
        return state_running;
    case 1u:
        return state_ready;
    case 2u:
        return state_blocked;
    case 3u:
        return state_suspended;
    case 4u:
        return state_deleted;
    default:
        return state_unknown;
    }
}

/* Thread table for the crash log. "StackSize" prints the high-water mark in
 * bytes and "MinFree" the same mark in words; StackAddr is TCB->pxStack. */
void cmb_dump_thread_table_594334(void)
{
    g2_task_status_t *status = g2_cmb_task_status;
    char name[CMB_TASK_NAME_COLUMN + 1];
    uint32_t count = uxTaskGetSystemState_454f38(status, CMB_TASK_DUMP_MAX, NULL);

    audio_ble_hci_boot_log_4733ee(table_banner);
    crash_record_printf_47da78(table_banner);
    (void)g2_audio_dump_snprintf(g2_cmb_line, CMB_LINE_SIZE, table_header_fmt, col_id,
                                 CMB_TASK_NAME_COLUMN, col_name, col_state, col_prio,
                                 col_stack_addr, col_stack_size, col_min_free);
    audio_ble_hci_boot_log_4733ee(line_fmt, g2_cmb_line);
    crash_record_printf_47da78(g2_cmb_line);
    crash_record_printf_47da78(newline);
    for (uint32_t i = 0u; i < count; i++) {
        audio_uart_buffer_zero(name, sizeof(name), 0u);
        (void)audio_settings_copy_text(name, status[i].name, CMB_TASK_NAME_COLUMN);
        name[CMB_TASK_NAME_COLUMN] = '\0';
        uint32_t stack_addr = ((const uint32_t *)status[i].handle)[12];
        (void)g2_audio_dump_snprintf(g2_cmb_line, CMB_LINE_SIZE, table_row_fmt, status[i].number,
                                     CMB_TASK_NAME_COLUMN, name,
                                     cmb_task_state_name_5942c8(status[i].state),
                                     status[i].priority, stack_addr,
                                     (uint32_t)status[i].stack_high_water << 2,
                                     (uint32_t)status[i].stack_high_water);
        audio_ble_hci_boot_log_4733ee(line_fmt, g2_cmb_line);
        crash_record_printf_47da78(g2_cmb_line);
        crash_record_printf_47da78(newline);
    }
    audio_ble_hci_boot_log_4733ee(table_rule);
    crash_record_printf_47da78(table_rule);
    if (uxTaskGetNumberOfTasks() > CMB_TASK_DUMP_MAX)
        audio_ble_hci_boot_log_4733ee(table_truncated, CMB_TASK_DUMP_MAX);
}
