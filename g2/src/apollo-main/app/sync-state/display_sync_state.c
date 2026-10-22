/* Apollo 0x49eb8e, 0x45baf0, 0x45bb58, 0x45bbd2. */
#include <stdint.h>

extern volatile uint32_t audio_uart_lcd_status_cell;
extern volatile uint32_t audio_uart_display_audio_lock_cell;
extern volatile uint32_t audio_uart_display_audio_flag_cell;
extern int32_t audio_file_mutex_acquire(void *, uint32_t);
extern int32_t audio_file_mutex_release(void *);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t, const char *, const char *, const char *,
                               uint32_t, const char *, ...);
extern uint32_t compressed_log_output(uint32_t, const char *, ...);

static const char module[] = "sync.module.framework";
static const char path[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\framework\\sync\\sync_framework.c";
static const char lock_name[] = "lockGlobalVariable";
static const char unlock_name[] = "unlockGlobalVariable";
static const char lock_error[] = "获取全局变量互斥锁失败，错误码: %d";
static const char unlock_error[] = "释放全局变量互斥锁失败，错误码: %d";
static const char lock_short[] =
    "[sync.module.framework]获取全局变量互斥锁失败，错误码: %d";
static const char unlock_short[] =
    "[sync.module.framework]释放全局变量互斥锁失败，错误码: %d";

/* Stock 0x49EB8E (WearDetect state getter, audio_uart_lcd_status) */
uint32_t audio_uart_lcd_status(void)
{
    return audio_uart_lcd_status_cell;
}

void audio_uart_display_audio_acquire_45baf0(void)
{
    uint32_t mutex = audio_uart_display_audio_lock_cell;
    if (mutex == 0u) return;
    int32_t result = audio_file_mutex_acquire((void *)(uintptr_t)mutex, UINT32_MAX);
    if (result == 0) return;
    if (audio_log_flags() & 2u)
        audio_log_extended(1u, module, path, lock_name, 0x279u, lock_error, result);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        (void)compressed_log_output(0x04400000u, lock_short, lock_short, result);
}

void audio_uart_display_audio_release_45bb58(void)
{
    uint32_t mutex = audio_uart_display_audio_lock_cell;
    if (mutex == 0u) return;
    int32_t result = audio_file_mutex_release((void *)(uintptr_t)mutex);
    if (result == 0) return;
    if (audio_log_flags() & 2u)
        audio_log_extended(1u, module, path, unlock_name, 0x285u,
                           unlock_error, result);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        (void)compressed_log_output(0x04400000u, unlock_short,
                                    unlock_short, result);
}

/* Stock 0x45BBD2 (clear global input-closed flag under lockGlobalVariable) */
void audio_uart_display_audio_finalize(void)
{
    audio_uart_display_audio_acquire_45baf0();
    if (audio_uart_display_audio_flag_cell == 1u)
        audio_uart_display_audio_flag_cell = 0u;
    audio_uart_display_audio_release_45bb58();
}
