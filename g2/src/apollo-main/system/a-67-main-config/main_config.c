/* Product entry, stock D:\01_workspace\s200_ap510b_iar_git\product\s200\app\config\main.c.
 * Native 0x5cdd14..0x5ce137; literal pool 0x5ce138..0x5ce1db.
 *
 * board_init_5cdd14 is not called directly: it is the level-0 entry of the
 * auto-init table at ROM 0x6d1e0c (row 0x6d1e2c = {0x5cdd15, 0}), which
 * 0x5bf0bc copies to RAM, sorts by level and runs from main. It latches the
 * RSTGEN reset status into g2_reset_status before the watchdog is armed,
 * enables the FPU, caches and the high-performance MCU mode, initialises the
 * heap and the GPU and initialises CmBacktrace with the application name/versions.
 *
 * main_5ce01e is the IAR program entry target (called from 0x5e42aa). The
 * kernel is started through the first slot of the thread-manager record at
 * RAM 0x200040d8 (thread_manager_kernel_start_4c9b48), which never returns. */
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

/* am_hal_reset_status_t, IAR layout: the eStatus enum is 16-bit. */
typedef struct {
    int16_t status;     /* +0x0 RSTGEN->STAT & 0x1fff */
    uint8_t ext;        /* +0x2 external reset */
    uint8_t por;        /* +0x3 power-on reset */
    uint8_t bod;        /* +0x4 brown-out reset */
    uint8_t swpor;      /* +0x5 SW power-on reset */
    uint8_t swpoi;      /* +0x6 SW power-on initialization reset */
    uint8_t dbgr;       /* +0x7 debugger reset */
    uint8_t wdt;        /* +0x8 watchdog reset */
    uint8_t bounreg;    /* +0x9 */
    uint8_t bocore;     /* +0xa */
    uint8_t bomem;      /* +0xb */
    uint8_t bohpmem;    /* +0xc */
    uint8_t reserved;   /* +0xd */
    uint8_t aircr;      /* +0xe AIRCR SYSRESETREQ ("CM55 SW reset") */
} g2_reset_status_t;
_Static_assert(sizeof(g2_reset_status_t) == 16u, "am_hal_reset_status_t");

/* First words of the thread-manager record (system/a-22-thread-manager). */
typedef struct {
    void (*kernel_start)(void); /* +0x00 */
    void (*deinit)(void);       /* +0x04 */
    void *thread;               /* +0x08 */
    uint32_t reserved[6];       /* +0x0c..+0x23 */
} g2_main_tm_state_t;
_Static_assert(sizeof(g2_main_tm_state_t) == 36u, "thread manager record");

#define AM_HAL_RESET_CONTROL_SWPOR 0u
#define AM_HAL_PWRCTRL_MCU_MODE_HIGH_PERFORMANCE 2u

extern g2_reset_status_t g2_reset_status;                  /* RAM 0x20073ea4 */
extern g2_main_tm_state_t audio_uart_thread_manager_state; /* RAM 0x200040d8 */

extern uint32_t audio_uart_ring_rtc_snapshot_4d3554(void *result); /* am_hal_reset_status_get */
extern uint32_t audio_ble_ota_reset_event(uint32_t request, uint32_t unused); /* 0x4d3534 am_hal_reset_control */
extern void watchdog_start_4b29d8(void);
extern void am_hal_sysctrl_fpu_enable(void);                     /* 0x44b068, upstream am_hal_sysctrl.c */
extern void am_hal_sysctrl_fpu_stacking_enable(bool lazy);      /* 0x44b07e, upstream am_hal_sysctrl.c */
extern void am_bsp_low_power_init_4c2ae8(void);
extern uint32_t pcm22_icache_enable(void);                        /* 0x474eb4 am_hal_cachectrl_icache_enable */
extern uint32_t am_hal_cachectrl_dcache_enable_474f32(bool write_through);
extern uint32_t am_hal_pwrctrl_mcu_mode_select_47f0a0(uint32_t mode);
extern void audio_ble_hci_boot_log_4733ee(const char *, ...);     /* am_util_stdio_printf-style */
extern void audio_uart_heap_initialize_4842e6(void);
extern void gpu_nema_init_59fae0(void);
extern void cm_backtrace_init(const char *firmware_name, const char *hardware_ver, const char *software_ver); /* 0x5939ae, upstream CmBacktrace */
extern void g2_delay_ms_4910f4(uint32_t ms);
extern void auto_init_table_run_5bf0bc(void);
extern void task_vote_init(void);

extern uint32_t audio_log_flags(void); /* 0x43d0ce */
extern void audio_log_extended(uint8_t, const char *, const char *, const char *, uint32_t, const char *, ...); /* 0x43d574 */
extern uint32_t compress_log_output(uint32_t, const char *, const char *, ...); /* 0x43ce9e */

static const char hp_mode_error[] = "Error switching to high performance mode. error num = %d\r\n"; /* ROM 0x71636c */
static const char sw_version[] = "2.2.6.10"; /* ROM 0x78b57c */
static const char hw_version[] = "V1.0.0"; /* ROM 0x78dc9c */
static const char app_name[] = "product/s200/app/Release/Exe/s200_app"; /* ROM 0x74b194 */

static const char module_tag[] = "mainThread"; /* ROM 0x78b588 */
static const char source_file[] = "D:\\01_workspace\\s200_ap510b_iar_git\\product\\s200\\app\\config\\main.c"; /* ROM 0x703acc */
static const char startup_fn[] = "startup_reason_printf"; /* ROM 0x7795ec */
static const char main_fn[] = "main"; /* ROM 0x78dca4 */

static const char rs_ext[] = "Startup reason: External reset"; /* ROM 0x762150 */
static const char rs_ext_short[] = "[mainThread]Startup reason: External reset"; /* ROM 0x73fdec */
static const char rs_por[] = "Startup reason: Power-On reset"; /* ROM 0x762170 */
static const char rs_por_short[] = "[mainThread]Startup reason: Power-On reset"; /* ROM 0x73fe18 */
static const char rs_bod[] = "Startup reason: Brown-Out reset"; /* ROM 0x762190 */
static const char rs_bod_short[] = "[mainThread]Startup reason: Brown-Out reset"; /* ROM 0x73fe44 */
static const char rs_swpor[] = "Startup reason: SW Power-On reset"; /* ROM 0x7568e8 */
static const char rs_swpor_short[] = "[mainThread]Startup reason: SW Power-On reset"; /* ROM 0x735564 */
static const char rs_swpoi[] = "Startup reason: SW Power On Initialization reset"; /* ROM 0x72aaac */
static const char rs_swpoi_short[] = "[mainThread]Startup reason: SW Power On Initialization reset"; /* ROM 0x70ca24 */
static const char rs_dbgr[] = "Startup reason: Debugger reset"; /* ROM 0x7621b0 */
static const char rs_dbgr_short[] = "[mainThread]Startup reason: Debugger reset"; /* ROM 0x73fe70 */
static const char rs_wdt[] = "Startup reason: Watch Dog Timer reset"; /* ROM 0x74b1bc */
static const char rs_wdt_short[] = "[mainThread]Startup reason: Watch Dog Timer reset"; /* ROM 0x72aae0 */
static const char rs_aircr[] = "Startup reason: CM55 SW reset"; /* ROM 0x7621d0 */
static const char rs_aircr_short[] = "[mainThread]Startup reason: CM55 SW reset"; /* ROM 0x73fe9c */
static const char rs_unknown[] = "Startup reason: Unknown reset"; /* ROM 0x7621f0 */
static const char rs_unknown_short[] = "[mainThread]Startup reason: Unknown reset"; /* ROM 0x73fec8 */
static const char rs_stat[] = "RSTGEN->STAT: 0x%02x"; /* ROM 0x779604 */
static const char rs_stat_short[] = "[mainThread]RSTGEN->STAT: 0x%02x"; /* ROM 0x75690c */

static const char boot_start[] = ">>> SYSTEM BOOT START <<<"; /* ROM 0x76dfe0 */
static const char boot_start_short[] = "[mainThread]>>> SYSTEM BOOT START <<<"; /* ROM 0x74b1e4 */
static const char boot_project[] = "Start up S200 EVT Project."; /* ROM 0x76dffc */
static const char boot_project_short[] = "[mainThread]Start up S200 EVT Project."; /* ROM 0x74b20c */
static const char git_describe[] = "master:v2.2.6.10-0-gb79923a139f5"; /* ROM 0x756930 */
static const char git_fmt[] = "Git Describe Full:[%s]."; /* ROM 0x77961c */
static const char git_fmt_short[] = "[mainThread]Git Describe Full:[%s]."; /* ROM 0x756954 */
static const char build_time[] = "21:37:52"; /* ROM 0x78b5a0, __TIME__ of the stock build */
static const char build_date[] = "Jul  6 2026"; /* ROM 0x78b594, __DATE__ of the stock build */
static const char version_fmt[] = "Software Version:[%s],Build time:[%s-%s].\r\n"; /* ROM 0x73fef4 */
static const char version_fmt_short[] = "[mainThread]Software Version:[%s],Build time:[%s-%s].\r\n"; /* ROM 0x720328 */

#define LOG_COMPRESSED() ((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)

int32_t board_init_5cdd14(void)
{
    (void)audio_uart_ring_rtc_snapshot_4d3554(&g2_reset_status);
    watchdog_start_4b29d8();
    am_hal_sysctrl_fpu_enable();
    am_hal_sysctrl_fpu_stacking_enable(true);
    am_bsp_low_power_init_4c2ae8();
    (void)pcm22_icache_enable();
    (void)am_hal_cachectrl_dcache_enable_474f32(true);
    int32_t status = (int32_t)am_hal_pwrctrl_mcu_mode_select_47f0a0(AM_HAL_PWRCTRL_MCU_MODE_HIGH_PERFORMANCE);
    if (status != 0)
        audio_ble_hci_boot_log_4733ee(hp_mode_error, status);
    audio_uart_heap_initialize_4842e6();
    gpu_nema_init_59fae0();
    cm_backtrace_init(app_name, hw_version, sw_version);
    return status;
}

/* Reports the first set reason (in this priority order) and the raw STAT.
 * A brown-out reset is answered with an immediate software POR. */
void startup_reason_printf_5cdd6c(void)
{
    const g2_reset_status_t *rs = &g2_reset_status;
    if (rs->ext != 0u) {
        if (audio_log_flags() & 2u)
            audio_log_extended(2u, module_tag, source_file, startup_fn, 53u, rs_ext);
        if (LOG_COMPRESSED())
            (void)compress_log_output(0x8000000u, rs_ext_short, rs_ext_short);
    } else if (rs->por != 0u) {
        if (audio_log_flags() & 2u)
            audio_log_extended(2u, module_tag, source_file, startup_fn, 55u, rs_por);
        if (LOG_COMPRESSED())
            (void)compress_log_output(0x8000000u, rs_por_short, rs_por_short);
    } else if (rs->bod != 0u) {
        if (audio_log_flags() & 2u)
            audio_log_extended(2u, module_tag, source_file, startup_fn, 57u, rs_bod);
        if (LOG_COMPRESSED())
            (void)compress_log_output(0x8000000u, rs_bod_short, rs_bod_short);
        (void)audio_ble_ota_reset_event(AM_HAL_RESET_CONTROL_SWPOR, 0u);
    } else if (rs->swpor != 0u) {
        if (audio_log_flags() & 2u)
            audio_log_extended(2u, module_tag, source_file, startup_fn, 61u, rs_swpor);
        if (LOG_COMPRESSED())
            (void)compress_log_output(0x8000000u, rs_swpor_short, rs_swpor_short);
    } else if (rs->swpoi != 0u) {
        if (audio_log_flags() & 2u)
            audio_log_extended(2u, module_tag, source_file, startup_fn, 63u, rs_swpoi);
        if (LOG_COMPRESSED())
            (void)compress_log_output(0x8000000u, rs_swpoi_short, rs_swpoi_short);
    } else if (rs->dbgr != 0u) {
        if (audio_log_flags() & 2u)
            audio_log_extended(2u, module_tag, source_file, startup_fn, 65u, rs_dbgr);
        if (LOG_COMPRESSED())
            (void)compress_log_output(0x8000000u, rs_dbgr_short, rs_dbgr_short);
    } else if (rs->wdt != 0u) {
        if (audio_log_flags() & 2u)
            audio_log_extended(2u, module_tag, source_file, startup_fn, 67u, rs_wdt);
        if (LOG_COMPRESSED())
            (void)compress_log_output(0x8000000u, rs_wdt_short, rs_wdt_short);
    } else if (rs->aircr != 0u) {
        if (audio_log_flags() & 2u)
            audio_log_extended(2u, module_tag, source_file, startup_fn, 69u, rs_aircr);
        if (LOG_COMPRESSED())
            (void)compress_log_output(0x8000000u, rs_aircr_short, rs_aircr_short);
    } else {
        if (audio_log_flags() & 2u)
            audio_log_extended(2u, module_tag, source_file, startup_fn, 71u, rs_unknown);
        if (LOG_COMPRESSED())
            (void)compress_log_output(0x8000000u, rs_unknown_short, rs_unknown_short);
    }
    if (audio_log_flags() & 2u)
        audio_log_extended(2u, module_tag, source_file, startup_fn, 73u, rs_stat, (int32_t)rs->status);
    if (LOG_COMPRESSED())
        (void)compress_log_output(0x8400000u, rs_stat_short, rs_stat_short, (int32_t)rs->status);
}

void main_5ce01e(void)
{
    g2_delay_ms_4910f4(200u);
    auto_init_table_run_5bf0bc();
    if (audio_log_flags() & 2u)
        audio_log_extended(4u, module_tag, source_file, main_fn, 80u, boot_start);
    if (LOG_COMPRESSED())
        (void)compress_log_output(0x10000000u, boot_start_short, boot_start_short);
    startup_reason_printf_5cdd6c();
    if (audio_log_flags() & 2u)
        audio_log_extended(2u, module_tag, source_file, main_fn, 86u, boot_project);
    if (LOG_COMPRESSED())
        (void)compress_log_output(0x8000000u, boot_project_short, boot_project_short);
    if (audio_log_flags() & 2u)
        audio_log_extended(2u, module_tag, source_file, main_fn, 87u, git_fmt, git_describe);
    if (LOG_COMPRESSED())
        (void)compress_log_output(0x8400000u, git_fmt_short, git_fmt_short, git_describe);
    if (audio_log_flags() & 2u)
        audio_log_extended(2u, module_tag, source_file, main_fn, 88u, version_fmt, sw_version,
                           build_date, build_time);
    if (LOG_COMPRESSED())
        (void)compress_log_output(0x8c00000u, version_fmt_short, version_fmt_short, sw_version,
                                  build_date, build_time);
    task_vote_init();
    audio_uart_thread_manager_state.kernel_start();
    for (;;) {
    }
}
