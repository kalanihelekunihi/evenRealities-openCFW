/* Display-driver manager thread teardown and mode request, stock
 * D:\01_workspace\s200_ap510b_iar_git\platform\display_mgr\displaydrv_manager.c.
 * Native 0x473aa4..0x473abb and 0x473bc4..0x473c41; literal pools at
 * 0x474480..0x4744a4 and 0x4742f8..0x47430c.
 *
 * The manager thread (Disp_Mgr_ThreadHandler, display-driver/display_driver_event_loop.c)
 * reads 36-byte messages {id, arg[8]} from a 0x60-deep queue:
 *   0 power up, 1 driver init + start 2 s device timer, 2 clear screen,
 *   3 partial reflash (arg0..5), 4 brightness (arg6), 5 stop timer + power down,
 *   6 timer tick: status check / recovery then full reflash, 8 set mode (arg6).
 * arg7 != 0 bypasses the dispatch gate. */
#include <stdint.h>

typedef struct {
    uint32_t id;     /* +0x00 */
    uint32_t arg[8]; /* +0x04 */
} g2_displaydrv_message_t;
_Static_assert(sizeof(g2_displaydrv_message_t) == 0x24, "stock display-driver message is 36 bytes");

struct display_driver_manager {
    void (*thread_init)(void); /* +0x0 */
    void (*queue_init)(void);  /* +0x4 */
    void *thread;              /* +0x8 */
    void *queue;               /* +0xc */
};
_Static_assert(sizeof(struct display_driver_manager) == 16u, "display driver manager ABI");

extern struct display_driver_manager audio_display_driver_manager; /* RAM 0x20000658 */

extern int32_t osThreadTerminate(void *thread);
extern int32_t osMessageQueuePut(void *queue, const void *message, uint8_t priority, uint32_t timeout);
extern void audio_uart_buffer_zero(void *dst, uint32_t len, uint32_t fill); /* 0x43c0e4 memset */
extern uint32_t audio_log_flags(void); /* 0x43d0ce */
extern void audio_log_extended(uint8_t, const char *, const char *, const char *, uint32_t, const char *, ...); /* 0x43d574 */
extern uint32_t compress_log_output(uint32_t, const char *, const char *, ...);

#define DISP_MSG_SET_MODE 8u

static const char module_tag[] = "task.displaydrvmgr"; /* ROM 0x77edc0 */
static const char source_file[] = "D:\\01_workspace\\s200_ap510b_iar_git\\platform\\display_mgr\\displaydrv_manager.c"; /* ROM 0x6ecb68 */
static const char mode_set_fn[] = "display_device_mode_set"; /* ROM 0x7769dc */
static const char send_failed[] = "async_reflash_xQueue1 send failed..\r\n"; /* ROM 0x7492cc */
static const char send_failed_short[] = "[task.displaydrvmgr]async_reflash_xQueue1 send failed..\r\n"; /* ROM 0x71438c */

void display_driver_thread_terminate_473aa4(void)
{
    if (audio_display_driver_manager.thread != 0) {
        (void)osThreadTerminate(audio_display_driver_manager.thread);
        audio_display_driver_manager.thread = 0;
    }
}

/* Queues a panel mode change (message 8, mode in arg[6]); 1 s put timeout. */
uint32_t display_device_mode_set_473bc4(uint8_t mode)
{
    g2_displaydrv_message_t message;

    audio_uart_buffer_zero(&message, sizeof message, 0u);
    message.id = DISP_MSG_SET_MODE;
    message.arg[6] = mode;
    if (osMessageQueuePut(audio_display_driver_manager.queue, &message, 0u, 1000u) == 0)
        return 0u;
    if (audio_log_flags() & 2u)
        audio_log_extended(2u, module_tag, source_file, mode_set_fn, 0xc1u, send_failed);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        (void)compress_log_output(0x08000000u, send_failed_short, send_failed_short);
    return UINT32_MAX;
}
