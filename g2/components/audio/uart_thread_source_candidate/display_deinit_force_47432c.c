/* Stock Async_GraphicsDev_Deinit_Force, 0x47432c..0x474474. */
#include <stdint.h>

uint32_t audio_display_hw_initialized_200744ec; /* stock RAM 0x200744ec */
extern volatile uint32_t audio_uart_display_manager_queue_cell; /* 0x20000664 */
extern void audio_uart_buffer_zero(void *, uint32_t, uint32_t);
extern int32_t audio_cmsis_queue_put(void *, const void *, uint8_t, uint32_t);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t, const char *, const char *, const char *,
                               uint32_t, const char *, ...);
extern uint32_t compressed_log_output(uint32_t, const char *, const char *, ...);

static const char module[] = "task.displaydrvmgr";
static const char path[] = "D:\\01_workspace\\s200_ap510b_iar_git\\platform\\display_mgr\\displaydrv_manager.c";
static const char function[] = "Async_GraphicsDev_Deinit_Force";
static const char idle_message[] = "hardware is not initialized, no need to deinitialize";
static const char start_message[] = "Async_GraphicsDev_Deinit_Force";
static const char clear_error[] = "Error - Failed to send ASYNC_DISPLAY_DEVICE_CLEAR_SCREEN_COMMAND.\r\n";
static const char power_error[] = "Error - Failed to send ASYNC_DISPLAY_DEVICE_POWER_DOWN_COMMAND\r\n";
static const char idle_short[] = "[task.displaydrvmgr]hardware is not initialized, no need to deinitialize";
static const char start_short[] = "[task.displaydrvmgr]Async_GraphicsDev_Deinit_Force";
static const char clear_short[] = "[task.displaydrvmgr]Error - Failed to send ASYNC_DISPLAY_DEVICE_CLEAR_SCREEN_COMMAND.\r\n";
static const char power_short[] = "[task.displaydrvmgr]Error - Failed to send ASYNC_DISPLAY_DEVICE_POWER_DOWN_COMMAND\r\n";

static void log_branch(uint8_t severity, uint32_t line, const char *message,
                       uint32_t compressed_level, const char *short_message)
{
    if ((audio_log_flags() & 2u) != 0u)
        audio_log_extended(severity, module, path, function, line, message);
    if ((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)
        (void)compressed_log_output(compressed_level, short_message, short_message);
}

uint32_t audio_wear_child_47432c(void)
{
    if (audio_display_hw_initialized_200744ec == 0u) {
        log_branch(4u, 0x191u, idle_message, 0x10000000u, idle_short);
        return 0u;
    }
    log_branch(3u, 0x194u, start_message, 0x0c000000u, start_short);
    uint32_t packet[9];
    audio_uart_buffer_zero(packet, sizeof packet, 0u);
    packet[8] = 1u;
    packet[0] = 2u;
    void *queue = (void *)(uintptr_t)audio_uart_display_manager_queue_cell;
    if (audio_cmsis_queue_put(queue, packet, 0u, 1000u) != 0) {
        log_branch(2u, 0x19bu, clear_error, 0x08000000u, clear_short);
        return UINT32_MAX;
    }
    packet[0] = 5u;
    if (audio_cmsis_queue_put(queue, packet, 0u, 1000u) != 0) {
        log_branch(2u, 0x1a1u, power_error, 0x08000000u, power_short);
        return UINT32_MAX;
    }
    return 0u;
}
