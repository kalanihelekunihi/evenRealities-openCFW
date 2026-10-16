/* Apollo display-manager interface 0x776a3c: one mode word and five
 * asynchronous queue callbacks. Native callback entries 0x473e2e..0x473ff6. */
#include <stdint.h>

extern volatile uint32_t audio_uart_display_manager_queue_cell; /* 0x20000664 */
extern void audio_uart_buffer_zero(void *, uint32_t, uint32_t); /* 0x43c0e4 */
extern int32_t audio_cmsis_queue_put(void *, const void *, uint8_t, uint32_t); /* 0x449abe */
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t, const char *, const char *, const char *,
                               uint32_t, const char *, ...);
extern uint32_t compressed_log_output(uint32_t, const char *, const char *, ...);

static const char module[] = "task.displaydrvmgr";
static const char path[] = "D:\\01_workspace\\s200_ap510b_iar_git\\platform\\display_mgr\\displaydrv_manager.c";
static const char init_fn[] = "Async_GraphicsDev_init";
static const char power_up_fn[] = "Async_GraphicsDev_PowerUP";
static const char power_down_fn[] = "Async_GraphicsDev_PowerDown";
static const char bright_fn[] = "Async_GraphicsDev_BrightCtrl";
static const char clear_fn[] = "Async_GraphicsDev_clearScreen";
static const char init_error[] = "Error - Failed to send ASYNC_DISPLAY_DEVICE_INIT_COMMAND.\r\n";
static const char power_up_error[] = "Error - Failed to send ASYNC_DISPLAY_DEVICE_POWER_UP_COMMAND\r\n";
static const char power_down_error[] = "Error - Failed to send ASYNC_DISPLAY_DEVICE_POWER_DOWN_COMMAND\r\n";
static const char bright_error[] = "Error - Failed to send ASYNC_DISPLAY_DEVICE_BRIGHT_CTRL_COMMAND\r\n";
static const char clear_error[] = "Error - Failed to send ASYNC_DISPLAY_DEVICE_CLEAR_SCREEN_COMMAND.\r\n";
static const char init_short[] = "[task.displaydrvmgr]Error - Failed to send ASYNC_DISPLAY_DEVICE_INIT_COMMAND.\r\n";
static const char power_up_short[] = "[task.displaydrvmgr]Error - Failed to send ASYNC_DISPLAY_DEVICE_POWER_UP_COMMAND\r\n";
static const char power_down_short[] = "[task.displaydrvmgr]Error - Failed to send ASYNC_DISPLAY_DEVICE_POWER_DOWN_COMMAND\r\n";
static const char bright_short[] = "[task.displaydrvmgr]Error - Failed to send ASYNC_DISPLAY_DEVICE_BRIGHT_CTRL_COMMAND\r\n";
static const char clear_short[] = "[task.displaydrvmgr]Error - Failed to send ASYNC_DISPLAY_DEVICE_CLEAR_SCREEN_COMMAND.\r\n";

static void send(uint32_t command, uint32_t brightness, const char *function,
                 uint32_t line, const char *message, const char *short_message)
{
    uint32_t packet[9];
    audio_uart_buffer_zero(packet, sizeof packet, 0u);
    packet[0] = command;
    if (command == 4u) packet[7] = brightness;
    if (audio_cmsis_queue_put((void *)(uintptr_t)audio_uart_display_manager_queue_cell,
                              packet, 0u, 1000u) == 0)
        return;
    if ((audio_log_flags() & 2u) != 0u)
        audio_log_extended(2u, module, path, function, line, message);
    if ((audio_log_flags() & 1u) != 0u ||
        (audio_log_flags() & 4u) != 0u)
        (void)compressed_log_output(0x08000000u, short_message, short_message);
}

void audio_display_manager_clear_473e2e(void)
{ send(2u, 0u, clear_fn, 0x127u, clear_error, clear_short); }
void audio_display_manager_init_473ea0(void)
{ send(1u, 0u, init_fn, 0x131u, init_error, init_short); }
void audio_display_manager_power_up_473f12(void)
{ send(0u, 0u, power_up_fn, 0x13bu, power_up_error, power_up_short); }
void audio_display_manager_power_down_473f84(void)
{ send(5u, 0u, power_down_fn, 0x145u, power_down_error, power_down_short); }
void audio_display_manager_brightness_473ff6(uint32_t brightness)
{ send(4u, brightness, bright_fn, 0x150u, bright_error, bright_short); }

const uintptr_t g2_display_state_table[6] = {
    1u,
    (uintptr_t)&audio_display_manager_clear_473e2e,
    (uintptr_t)&audio_display_manager_init_473ea0,
    (uintptr_t)&audio_display_manager_power_up_473f12,
    (uintptr_t)&audio_display_manager_power_down_473f84,
    (uintptr_t)&audio_display_manager_brightness_473ff6,
};
_Static_assert(sizeof(g2_display_state_table) == 24u, "native display interface extent");
