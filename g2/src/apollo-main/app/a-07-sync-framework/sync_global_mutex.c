/* Sync framework global-variable mutex and head-up startup option,
 * stock D:\01_workspace\s200_ap510b_iar_git\framework\sync\sync_framework.c.
 * Native 0x45ba3c..0x45ba45 and 0x45ba46..0x45bae5 (literal pool 0x45bfb8..0x45bfd3,
 * shared module/source pool words 0x45bc84/0x45bc88).
 *
 * The mutex cell at RAM 0x200749c8 is the one lockGlobalVariable (0x45baf0) and
 * unlockGlobalVariable (0x45bb58) take; see app/sync-state/display_sync_state.c. */
#include <stdint.h>
#include <stddef.h>

typedef struct {
    const char *name;   /* +0x0 */
    uint32_t attr_bits; /* +0x4 osMutexRecursive | osMutexPrioInherit */
    void *cb_mem;       /* +0x8 */
    uint32_t cb_size;   /* +0xc */
} g2_os_mutex_attr_t;   /* osMutexAttr_t */
_Static_assert(sizeof(g2_os_mutex_attr_t) == 16, "osMutexAttr_t");

extern volatile uint32_t audio_uart_display_audio_lock_cell; /* RAM 0x200749c8 */

extern uint8_t *settings_get_config(void); /* 0x46b44c */
extern void *osMutexNew(const void *attr);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern uint32_t compress_log_output(uint32_t, const char *, const char *, ...);

static const char module[] = "sync.module.framework"; /* ROM 0x77c07c */
static const char source[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\framework\\sync\\sync_framework.c"; /* ROM 0x705fb8 */
static const char function_name[] = "initGlobalVariableMutex"; /* ROM 0x77c0c4 */
static const char mutex_name[] = "GlobalVarMutex"; /* ROM 0x789590 */
static const char e_failed[] = "创建全局变量互斥锁失败"; /* ROM 0x75a614 */
static const char c_failed[] = "[sync.module.framework]创建全局变量互斥锁失败"; /* ROM 0x718f7c */
static const char e_created[] = "全局变量互斥锁创建成功"; /* ROM 0x75a638 */
static const char c_created[] = "[sync.module.framework]全局变量互斥锁创建成功"; /* ROM 0x718fb8 */

static const g2_os_mutex_attr_t global_mutex_attr = { /* ROM 0x7895e0 */
    mutex_name, 3u, NULL, 0u};

/* Head-up (IMU) startup enable: settings config byte +10. Read by the
 * schedule manager before starting the dashboard on an IMU look-up event. */
uint8_t imu_startup_enable_get_45ba3c(void)
{
    return settings_get_config()[10];
}

static void log0(uint8_t level, uint32_t line, const char *e, const char *c)
{
    if (audio_log_flags() & 2u)
        audio_log_extended(level, module, source, function_name, line, e);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        (void)compress_log_output((uint32_t)level << 26, c, c);
}

/* Creates the global-variable mutex once. The schedule-manager thread calls it
 * with r0 = 0; the argument is not read. */
void initGlobalVariableMutex_45ba46(uint32_t unused)
{
    (void)unused;
    if (audio_uart_display_audio_lock_cell != 0u)
        return;
    audio_uart_display_audio_lock_cell = (uint32_t)(uintptr_t)osMutexNew(&global_mutex_attr);
    if (audio_uart_display_audio_lock_cell == 0u)
        log0(1u, 0x26bu, e_failed, c_failed);
    else
        log0(4u, 0x26du, e_created, c_created);
}
