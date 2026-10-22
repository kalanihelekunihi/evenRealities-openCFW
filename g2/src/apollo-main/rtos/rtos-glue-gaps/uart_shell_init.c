/* UART debug shell start-up, native 0x54171c..0x541769 (literal pool 0x541770..0x54178f).
 * Called from the thread-manager start-up at 0x4c953e after uart_instance_init.
 * The shell task (0x541600) registers the FreeRTOS-Plus-CLI commands and feeds
 * characters from the stream buffer to FreeRTOS_CLIProcessCommand; UART channel 1
 * is the console. */
#include <stdint.h>
#include <stddef.h>

typedef struct {
    const char *name; uint32_t attr_bits; void *cb_mem; uint32_t cb_size;
    void *stack_mem; uint32_t stack_size; uint32_t priority;
    uint32_t tz_module; uint32_t reserved;
} g2_os_thread_attr_t;
_Static_assert(sizeof(g2_os_thread_attr_t) == 36, "osThreadAttr_t");

#define SHELL_UART_CHANNEL 1u
#define SHELL_RX_BUFFER_SIZE 0x800u
#define SHELL_RX_TRIGGER 1u
#define SHELL_THREAD_CB_SIZE 0x70u
#define SHELL_THREAD_STACK_SIZE 0x1000u
#define SHELL_THREAD_PRIORITY 0x18u /* osPriorityNormal */

extern void *g2_shell_rx_stream;   /* RAM 0x200748bc StreamBufferHandle_t */
extern void *g2_shell_thread;      /* RAM 0x200748b8 */
extern void shell_puts_5415c2(const char *text);                       /* strlen + UART ch1 TX */
extern void shell_rx_callback_5415e6(const uint8_t *data, uint32_t len); /* xStreamBufferSendFromISR */
extern void shell_task_541600(void *argument);
extern void log_output_hook_set_472c7c(void (*hook)(const char *text)); /* cell 0x200742f0 */
extern void codec_channel_callback(uint32_t channel, uint32_t callback); /* 0x55e8f0 */
extern void *xStreamBufferGenericCreate(size_t size, size_t trigger, int32_t is_message_buffer,
                                        void *send_completed, void *receive_completed); /* 0x57deea */
extern void *osThreadNew(void (*func)(void *), void *argument, const void *attr); /* 0x4490e2 */
extern uint32_t ulSetInterruptMask(void); /* 0x5fa0a4 */

static const char shell_thread_name[] = "uart_shell"; /* ROM 0x78c614 */
uint32_t g2_shell_thread_cb[SHELL_THREAD_CB_SIZE / 4u];       /* RAM 0x200724c0 */
uint32_t g2_shell_thread_stack[SHELL_THREAD_STACK_SIZE / 4u]; /* RAM 0x2036ee40 */
static const g2_os_thread_attr_t shell_thread_attr = { /* ROM 0x75b958 */
    shell_thread_name, 0u, g2_shell_thread_cb, SHELL_THREAD_CB_SIZE,
    g2_shell_thread_stack, SHELL_THREAD_STACK_SIZE, SHELL_THREAD_PRIORITY, 1u, 0u};

void uart_shell_init_54171c(void)
{
    log_output_hook_set_472c7c(shell_puts_5415c2);
    codec_channel_callback(SHELL_UART_CHANNEL, (uint32_t)(uintptr_t)shell_rx_callback_5415e6);
    g2_shell_rx_stream = xStreamBufferGenericCreate(SHELL_RX_BUFFER_SIZE, SHELL_RX_TRIGGER, 0, NULL, NULL);
    g2_shell_thread = osThreadNew(shell_task_541600, NULL, &shell_thread_attr);
    if (g2_shell_thread == NULL) { /* configASSERT */
        (void)ulSetInterruptMask();
        *(volatile uint32_t *)(uintptr_t)0xffffffffu = 0u;
        for (;;) {
        }
    }
}
