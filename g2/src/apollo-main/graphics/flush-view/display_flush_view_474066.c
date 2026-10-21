/* Apollo Main display manager ASYNC_REFLASH_COMMAND 0x474066..0x4740ff.
 * Stock literal 0x4742f8 names RAM base 0x20000658; +0xc is queue handle.
 * The whole RAM layout and startup initializer remain a separate gate. */
#include <stdint.h>

extern void audio_uart_buffer_zero(void *, uint32_t, uint32_t);
extern int32_t audio_cmsis_queue_put(void *, const void *, uint8_t, uint32_t);
extern uint32_t audio_log_level(void);
extern void audio_log_extended(uint8_t, const char *, const char *,
                               const char *, uint32_t, const char *, ...);
extern uint32_t compressed_log_output(uint32_t, const char *, const char *, ...);
extern volatile uint32_t audio_uart_display_manager_queue_cell;

static const char module[] = "task.displaydrvmgr";
static const char path[] = "D:\\01_workspace\\s200_ap510b_iar_git\\platform\\display_mgr\\displaydrv_manager.c";
static const char name[] = "send_async_reflash_msg";
static const char plain[] = "Error - Failed to send ASYNC_REFLASH_COMMAND\r\n";
static const char compact[] = "[task.displaydrvmgr]Error - Failed to send ASYNC_REFLASH_COMMAND\r\n";

int32_t audio_uart_display_flush_view_474066(uint32_t a, uint32_t b,
                                               uint32_t c, uint32_t d,
                                               uint32_t e, uint32_t f) {
    uint32_t message[9];
    audio_uart_buffer_zero(message, sizeof(message), 0u);
    message[0] = 3u;
    message[1] = a;
    message[2] = b;
    message[3] = c;
    message[4] = d;
    message[5] = e;
    message[6] = f;
    uint32_t queue = audio_uart_display_manager_queue_cell;
    if (audio_cmsis_queue_put((void *)(uintptr_t)queue, message, 0u, 1000u) == 0)
        return 0;
    if ((audio_log_level() & 2u) != 0u)
        audio_log_extended(2u, module, path, name, 0x161u, plain);
    if ((audio_log_level() & 1u) != 0u || (audio_log_level() & 4u) != 0u)
        (void)compressed_log_output(0x08000000u, compact, compact);
    return -1;
}
