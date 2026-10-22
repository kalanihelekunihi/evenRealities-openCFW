/* UART debug shell RX callback and task, native 0x5415e6..0x5415ff and
 * 0x541600..0x54171b (literal pool shared with uart_shell_init_54171c at
 * 0x54176c..0x54178f). Reconstructed 2026-10-21 (C3) from the 2.2.6.10
 * disassembly; compiles, byte identity not established.
 *
 * shell_rx_callback_5415e6 is the UART channel 1 RX callback installed by
 * uart_shell_init_54171c (rtos/rtos-glue-gaps/uart_shell_init.c); it pushes the
 * received bytes into the shell RX stream buffer from interrupt context.
 * shell_task_541600 registers every FreeRTOS-Plus-CLI command table, then echoes
 * each received character, edits the 128-byte input line, and on CR or LF runs
 * FreeRTOS_CLIProcessCommand until it reports no more output.
 * FreeRTOS-Plus-CLI is not integrated yet, so FreeRTOS_CLIProcessCommand
 * (0x5847fe) is called as freertos_cli_process_command_5847fe. */
#include <stdint.h>
#include <stddef.h>

#define SHELL_LINE_SIZE 0x80u
#define SHELL_PORT_MAX_DELAY 0xffffffffu

extern void *g2_shell_rx_stream;                     /* RAM 0x200748bc StreamBufferHandle_t */
extern char g2_shell_output_20071b48[SHELL_LINE_SIZE]; /* RAM 0x20071b48 CLI output buffer */
extern char g2_shell_input_20071bc8[SHELL_LINE_SIZE];  /* RAM 0x20071bc8 CLI input line */

extern size_t xStreamBufferSendFromISR(void *xStreamBuffer, const void *pvTxData, size_t xDataLengthBytes,
                                       int32_t *pxHigherPriorityTaskWoken); /* 0x57e05e */
extern size_t xStreamBufferReceive(void *xStreamBuffer, void *pvRxData, size_t xBufferLengthBytes,
                                   uint32_t xTicksToWait); /* 0x57e136 */
extern int32_t freertos_cli_process_command_5847fe(const char *input, char *write_buffer,
                                                   size_t write_buffer_len); /* FreeRTOS_CLIProcessCommand */
extern void shell_puts_5415c2(const char *text);
extern void cli_putchar_5415d8(int32_t c);
extern void audio_uart_buffer_zero(void *dst, uint32_t len, uint32_t fill); /* memset 0x43c0e4 */

extern void cli_register_system_commands_57e626(void);
extern void cli_register_info_commands_57e810(void);
extern void cli_register_filesystem_commands_57ff40(void);
extern void cli_register_display_commands_580392(void);
extern void cli_register_log_commands_5807c0(void);
extern void cli_register_imu_command_580c04(void);
extern void cli_register_audio_commands_580fec(void);
extern void cli_register_psn_command_5810d8(void);
extern void cli_register_pdm_command_581136(void);
extern void cli_register_ble_commands_581644(void);
extern void cli_register_xmodem_command_58183a(void);
extern void cli_register_ui_commands_581960(void);
extern void cli_register_touch_commands_581d60(void);
extern void cli_register_app_commands_5827d0(void);
extern void cli_register_terminal_command_5836b8(void);
extern void cli_register_set_command_583cec(void);
extern void cli_register_buzzer_command_583f74(void);
extern void cli_register_gpio_command_5840f4(void);
extern void cli_register_box_force_out_command_5841ee(void);
extern void cli_register_set_language_command_584320(void);
extern void cli_register_onboarding_command_584430(void);
extern void cli_register_get_command_584702(void);

static const char shell_newline_prompt[] = "\n#"; /* ROM 0x54176c */

void shell_rx_callback_5415e6(const uint8_t *data, uint32_t len);
void shell_task_541600(void *argument);

/* Stock 0x005415E6 (shell_rx_callback_5415e6) */
void shell_rx_callback_5415e6(const uint8_t *data, uint32_t len)
{
    if (len != 0u) {
        int32_t woken = 0;
        (void)xStreamBufferSendFromISR(g2_shell_rx_stream, data, len, &woken);
    }
}

/* Stock 0x00541600 (shell_task_541600) */
void shell_task_541600(void *argument)
{
    uint8_t rx;
    uint8_t index = 0u;
    int32_t more;

    (void)argument;
    cli_register_system_commands_57e626();
    cli_register_info_commands_57e810();
    cli_register_filesystem_commands_57ff40();
    cli_register_display_commands_580392();
    cli_register_log_commands_5807c0();
    cli_register_imu_command_580c04();
    cli_register_audio_commands_580fec();
    cli_register_psn_command_5810d8();
    cli_register_pdm_command_581136();
    cli_register_ble_commands_581644();
    cli_register_xmodem_command_58183a();
    cli_register_ui_commands_581960();
    cli_register_touch_commands_581d60();
    cli_register_app_commands_5827d0();
    cli_register_terminal_command_5836b8();
    cli_register_set_command_583cec();
    cli_register_buzzer_command_583f74();
    cli_register_gpio_command_5840f4();
    cli_register_box_force_out_command_5841ee();
    cli_register_set_language_command_584320();
    cli_register_onboarding_command_584430();
    cli_register_get_command_584702();

    for (;;) {
        (void)xStreamBufferReceive(g2_shell_rx_stream, &rx, 1u, SHELL_PORT_MAX_DELAY);
        if (rx == 0x7fu) {
            rx = '\b';
        }
        cli_putchar_5415d8(rx);
        if (rx == '\n' || rx == '\r') {
            shell_puts_5415c2(shell_newline_prompt);
            do {
                more = freertos_cli_process_command_5847fe(g2_shell_input_20071bc8, g2_shell_output_20071b48,
                                                           SHELL_LINE_SIZE);
                shell_puts_5415c2(g2_shell_output_20071b48);
                audio_uart_buffer_zero(g2_shell_output_20071b48, SHELL_LINE_SIZE, 0u);
            } while (more != 0);
            index = 0u;
            audio_uart_buffer_zero(g2_shell_input_20071bc8, SHELL_LINE_SIZE, 0u);
        } else if (rx == '\r') {
            /* unreachable second CR test kept from the stock control flow */
        } else if (rx == '\b' || rx == 0x7fu) {
            if (index != 0u) {
                index--;
                g2_shell_input_20071bc8[index] = '\0';
                cli_putchar_5415d8(' ');
                cli_putchar_5415d8('\b');
            }
        } else if (index < SHELL_LINE_SIZE) {
            g2_shell_input_20071bc8[index] = (char)rx;
            index++;
        }
    }
}
