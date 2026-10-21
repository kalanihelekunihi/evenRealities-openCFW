/* Stock Async_GraphicsDev_Init_Force, 0x474100..0x4742f8. */
#include <stdint.h>

extern uint32_t audio_display_hw_initialized_200744ec; /* 0x200744ec */
extern volatile uint32_t audio_uart_display_manager_queue_cell; /* 0x20000664 */
extern uint32_t audio_log_wake_allowed(void); /* 0x443484 */
extern void audio_uart_buffer_zero(void *, uint32_t, uint32_t); /* 0x43c0e4 */
extern int32_t audio_cmsis_queue_put(void *, const void *, uint8_t, uint32_t); /* 0x449abe */
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t, const char *, const char *, const char *,
                               uint32_t, const char *, ...);
extern uint32_t compressed_log_output(uint32_t, const char *, const char *, ...);

static const char module[] = "task.displaydrvmgr";
static const char path[] = "D:\\01_workspace\\s200_ap510b_iar_git\\platform\\display_mgr\\displaydrv_manager.c";
static const char function[] = "Async_GraphicsDev_Init_Force";
static const char already_message[] = "hardware is already initialized, no need to initialize";
static const char stopped_message[] = "display is not running, skip init";
static const char start_message[] = "Async_GraphicsDev_Init_Force";
static const char power_error[] = "Error - Failed to send ASYNC_DISPLAY_DEVICE_POWER_UP_COMMAND\r\n";
static const char init_error[] = "Error - Failed to send ASYNC_DISPLAY_DEVICE_INIT_COMMAND.\r\n";
static const char reflash_error[] = "Error - Failed to send ASYNC_REFLASH_COMMAND.\r\n";
static const char already_short[] = "[task.displaydrvmgr]hardware is already initialized, no need to initialize";
static const char stopped_short[] = "[task.displaydrvmgr]display is not running, skip init";
static const char start_short[] = "[task.displaydrvmgr]Async_GraphicsDev_Init_Force";
static const char power_short[] = "[task.displaydrvmgr]Error - Failed to send ASYNC_DISPLAY_DEVICE_POWER_UP_COMMAND\r\n";
static const char init_short[] = "[task.displaydrvmgr]Error - Failed to send ASYNC_DISPLAY_DEVICE_INIT_COMMAND.\r\n";
static const char reflash_short[] = "[task.displaydrvmgr]Error - Failed to send ASYNC_REFLASH_COMMAND.\r\n";

static void log_branch(uint8_t severity, uint32_t line, const char *message,
                       uint32_t compressed_level, const char *short_message)
{
    if ((audio_log_flags() & 2u) != 0u)
        audio_log_extended(severity, module, path, function, line, message);
    if ((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)
        (void)compressed_log_output(compressed_level, short_message, short_message);
}

uint32_t audio_wear_child_474100(void)
{
    if (audio_display_hw_initialized_200744ec != 0u) {
        log_branch(4u, 0x16au, already_message, 0x10000000u, already_short);
        return 0u;
    }
    if (audio_log_wake_allowed() == 0u) {
        log_branch(3u, 0x170u, stopped_message, 0x0c000000u, stopped_short);
        return 0u;
    }
    log_branch(3u, 0x174u, start_message, 0x0c000000u, start_short);
    uint32_t packet[9];
    audio_uart_buffer_zero(packet, sizeof packet, 0u);
    packet[8] = 1u;
    void *queue = (void *)(uintptr_t)audio_uart_display_manager_queue_cell;
    static const uint32_t commands[3] = {0u, 1u, 3u};
    static const uint32_t lines[3] = {0x17cu, 0x182u, 0x188u};
    static const char *const messages[3] = {power_error, init_error, reflash_error};
    static const char *const short_messages[3] = {power_short, init_short, reflash_short};
    for (uint32_t i = 0u; i < 3u; ++i) {
        packet[0] = commands[i];
        if (audio_cmsis_queue_put(queue, packet, 0u, 1000u) != 0) {
            log_branch(2u, lines[i], messages[i], 0x08000000u, short_messages[i]);
            return UINT32_MAX;
        }
    }
    return 0u;
}
