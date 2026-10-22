/* Product FreeRTOS-Plus-CLI display / sync test commands, stock directory
 * D:\01_workspace\s200_ap510b_iar_git\kernel\FreeRTOS-Plus-CLI\prvCommand\
 * (file name not retained). Native handlers 0x580100..0x580391, pool
 * 0x5803ec..0x5803f7. The registrar 0x580392 is in
 * a-59-cli-commands/prvCommand_registrars.c.
 *
 * "disp*" drive the master (both-arm) display app manager, "single*" the
 * local (slave-side) one; udata/pdata/syncTest push raw bytes over the
 * inter-arm sync link (SendDataToBoth / SendDataToPeer). */
#include <stddef.h>
#include <stdint.h>
#include "../a-59-cli-commands/cli_commands.h"

#define SYNC_TEST_APP 1u
#define SYNC_TEST_BYTES 1024u
#define SINPUT_EVENT_A 4
#define SINPUT_EVENT_B 5
#define SINPUT_CODE_A 0x44u
#define SINPUT_CODE_B 0x45u

extern int32_t atoi_48d868(const char *text);
extern uint32_t g2_log_module_length(const char *text); /* 0x44a43c strlen */
extern int32_t g2_audio_dump_snprintf(char *dst, uint32_t size, const char *format, ...); /* 0x44b728 */
extern int32_t audio_uart_master_input_event(uint32_t device, uint32_t event, uint32_t value,
                                             uint32_t context); /* 0x465748 */
extern int32_t audio_uart_input_event_send_464d1c(uint16_t app, const void *data, uint32_t len,
                                                  uint32_t flags); /* SendDataToBoth */
extern uint32_t audio_uart_request_send(uint32_t app, const void *data, uint32_t len,
                                        uint32_t flags); /* SendDataToPeer 0x4651e0 */
extern void audio_uart_master_display_start(uint32_t app, const void *payload,
                                            uint16_t length, uint32_t extra); /* 0x464b2e */
extern void audio_uart_master_display_refresh(uint32_t app, const void *payload,
                                              uint16_t length, uint32_t extra); /* 0x464bb2 */
extern void audio_uart_master_display_stop(uint32_t app, const void *payload,
                                           uint16_t length, uint32_t extra); /* 0x464c36 */
extern void audio_uart_master_control(uint32_t enable); /* 0x464cba */
extern int32_t audio_uart_slave_display_start(uint32_t, const void *, uint32_t);   /* 0x4441ec */
extern int32_t audio_uart_slave_display_refresh(uint32_t, const void *, uint32_t); /* 0x4442d0 */
extern int32_t audio_uart_slave_display_stop(uint32_t, const void *, uint32_t);    /* 0x4443cc */
extern int32_t DispStartBlockingEn_45bca0(uint32_t timeout_ms);
extern void DispStartBlockingCancel_45be6c(void);
extern uint8_t g2_cli_sync_test_data_2006c130[SYNC_TEST_BYTES]; /* RAM 0x2006c130 */

static const char s_block_en[] = "dispBlockEn timeout=%d ms, ret=%d\r\n"; /* ROM 0x7588d4 */
static const char s_block_cancel[] = "dispBlockCancel done\r\n";           /* ROM 0x77abdc */

int32_t cli_cmd_input_580100(char *write_buffer, size_t write_buffer_len, const char *command_string);
int32_t cli_cmd_sinput_580144(char *write_buffer, size_t write_buffer_len, const char *command_string);
int32_t cli_cmd_udata_5801b4(char *write_buffer, size_t write_buffer_len, const char *command_string);
int32_t cli_cmd_sync_test_5801ee(char *write_buffer, size_t write_buffer_len, const char *command_string);
int32_t cli_cmd_pdata_58021c(char *write_buffer, size_t write_buffer_len, const char *command_string);
int32_t cli_cmd_disp_start_580256(char *write_buffer, size_t write_buffer_len, const char *command_string);
int32_t cli_cmd_single_start_580276(char *write_buffer, size_t write_buffer_len,
                                    const char *command_string);
int32_t cli_cmd_single_reflash_580292(char *write_buffer, size_t write_buffer_len,
                                      const char *command_string);
int32_t cli_cmd_disp_reflash_5802c6(char *write_buffer, size_t write_buffer_len,
                                    const char *command_string);
int32_t cli_cmd_disp_stop_5802fe(char *write_buffer, size_t write_buffer_len, const char *command_string);
int32_t cli_cmd_disp_exit_58031e(char *write_buffer, size_t write_buffer_len, const char *command_string);
int32_t cli_cmd_disp_block_en_58032a(char *write_buffer, size_t write_buffer_len,
                                     const char *command_string);
int32_t cli_cmd_disp_block_cancel_58035e(char *write_buffer, size_t write_buffer_len,
                                         const char *command_string);
int32_t cli_cmd_single_stop_580376(char *write_buffer, size_t write_buffer_len, const char *command_string);

static int32_t cli_int_param(const char *command_string, uint32_t index, int32_t *length)
{
    return atoi_48d868(freertos_cli_get_parameter_5848fc(command_string, index, length));
}

/* "input <device> <event> <value>": inject an input event (both arms). */
int32_t cli_cmd_input_580100(char *write_buffer, size_t write_buffer_len, const char *command_string)
{
    int32_t length;
    int32_t device;
    int32_t event;
    int32_t value;

    (void)write_buffer;
    (void)write_buffer_len;
    device = cli_int_param(command_string, 1u, &length);
    event = cli_int_param(command_string, 2u, &length);
    value = cli_int_param(command_string, 3u, &length);
    (void)audio_uart_master_input_event((uint16_t)device, (uint32_t)event, (uint32_t)value, 0u);
    return 0;
}

/* "sinput <a> <event> <b>": only events 4 and 5 are forwarded, as a
 * 6-byte refresh {0, 0x44|0x45, 0, 0, 0, 0} to local app 1. */
int32_t cli_cmd_sinput_580144(char *write_buffer, size_t write_buffer_len, const char *command_string)
{
    int32_t length;
    int32_t event;
    uint8_t payload[6];

    (void)write_buffer;
    (void)write_buffer_len;
    (void)cli_int_param(command_string, 1u, &length);
    event = cli_int_param(command_string, 2u, &length);
    (void)cli_int_param(command_string, 3u, &length);
    payload[0] = 0u;
    if (event == SINPUT_EVENT_A)
        payload[1] = SINPUT_CODE_A;
    else if (event == SINPUT_EVENT_B)
        payload[1] = SINPUT_CODE_B;
    else
        return 0;
    payload[2] = 0u;
    payload[3] = 0u;
    payload[4] = 0u;
    payload[5] = 0u;
    (void)audio_uart_slave_display_refresh(1u, payload, sizeof(payload));
    return 0;
}

/* "udata <app> <text>": send the text to both arms. */
int32_t cli_cmd_udata_5801b4(char *write_buffer, size_t write_buffer_len, const char *command_string)
{
    int32_t length;
    int32_t app;
    const char *text;

    (void)write_buffer;
    (void)write_buffer_len;
    app = cli_int_param(command_string, 1u, &length);
    text = freertos_cli_get_parameter_5848fc(command_string, 2u, &length);
    (void)audio_uart_input_event_send_464d1c((uint16_t)app, text,
                                             (uint16_t)g2_log_module_length(text), 0u);
    return 0;
}

/* "syncTest <n>": n sends of the 1 KiB test block to both arms, app 1. */
int32_t cli_cmd_sync_test_5801ee(char *write_buffer, size_t write_buffer_len, const char *command_string)
{
    int32_t length;
    int32_t count;
    int32_t i;

    (void)write_buffer;
    (void)write_buffer_len;
    count = cli_int_param(command_string, 1u, &length);
    for (i = 0; i < count; i++)
        (void)audio_uart_input_event_send_464d1c(SYNC_TEST_APP, g2_cli_sync_test_data_2006c130,
                                                 SYNC_TEST_BYTES, 0u);
    return 0;
}

/* "pdata <app> <text>": send the text to the peer arm. */
int32_t cli_cmd_pdata_58021c(char *write_buffer, size_t write_buffer_len, const char *command_string)
{
    int32_t length;
    int32_t app;
    const char *text;

    (void)write_buffer;
    (void)write_buffer_len;
    app = cli_int_param(command_string, 1u, &length);
    text = freertos_cli_get_parameter_5848fc(command_string, 2u, &length);
    (void)audio_uart_request_send((uint16_t)app, text, (uint16_t)g2_log_module_length(text), 0u);
    return 0;
}

int32_t cli_cmd_disp_start_580256(char *write_buffer, size_t write_buffer_len, const char *command_string)
{
    int32_t length;

    (void)write_buffer;
    (void)write_buffer_len;
    audio_uart_master_display_start((uint16_t)cli_int_param(command_string, 1u, &length), NULL, 0u, 0u);
    return 0;
}

int32_t cli_cmd_single_start_580276(char *write_buffer, size_t write_buffer_len,
                                    const char *command_string)
{
    int32_t length;

    (void)write_buffer;
    (void)write_buffer_len;
    (void)audio_uart_slave_display_start((uint32_t)cli_int_param(command_string, 1u, &length), NULL, 0u);
    return 0;
}

/* "singleReflash <app> <byte>": one-byte refresh of a local app. */
int32_t cli_cmd_single_reflash_580292(char *write_buffer, size_t write_buffer_len,
                                      const char *command_string)
{
    int32_t length;
    const char *app_text;
    uint8_t data;

    (void)write_buffer;
    (void)write_buffer_len;
    app_text = freertos_cli_get_parameter_5848fc(command_string, 1u, &length);
    data = (uint8_t)cli_int_param(command_string, 2u, &length);
    (void)audio_uart_slave_display_refresh((uint32_t)atoi_48d868(app_text), &data, 1u);
    return 0;
}

/* "dispReflash <app> <byte>": one-byte refresh on both arms. */
int32_t cli_cmd_disp_reflash_5802c6(char *write_buffer, size_t write_buffer_len,
                                    const char *command_string)
{
    int32_t length;
    int32_t app;
    uint8_t data;

    (void)write_buffer;
    (void)write_buffer_len;
    app = cli_int_param(command_string, 1u, &length);
    data = (uint8_t)cli_int_param(command_string, 2u, &length);
    audio_uart_master_display_refresh((uint16_t)app, &data, 1u, 0u);
    return 0;
}

int32_t cli_cmd_disp_stop_5802fe(char *write_buffer, size_t write_buffer_len, const char *command_string)
{
    int32_t length;

    (void)write_buffer;
    (void)write_buffer_len;
    audio_uart_master_display_stop((uint16_t)cli_int_param(command_string, 1u, &length), NULL, 0u, 0u);
    return 0;
}

/* "dispExit": exit all display apps. */
int32_t cli_cmd_disp_exit_58031e(char *write_buffer, size_t write_buffer_len, const char *command_string)
{
    (void)write_buffer;
    (void)write_buffer_len;
    (void)command_string;
    audio_uart_master_control(0u);
    return 0;
}

/* "dispBlockEn <ms>": negative timeouts clamp to 0; reply in write_buffer. */
int32_t cli_cmd_disp_block_en_58032a(char *write_buffer, size_t write_buffer_len,
                                     const char *command_string)
{
    int32_t length;
    int32_t timeout;
    int32_t ret;

    timeout = cli_int_param(command_string, 1u, &length);
    if (timeout < 0)
        timeout = 0;
    ret = DispStartBlockingEn_45bca0((uint32_t)timeout);
    (void)g2_audio_dump_snprintf(write_buffer, (uint32_t)write_buffer_len, s_block_en, timeout, ret);
    return 0;
}

int32_t cli_cmd_disp_block_cancel_58035e(char *write_buffer, size_t write_buffer_len,
                                         const char *command_string)
{
    (void)command_string;
    DispStartBlockingCancel_45be6c();
    (void)g2_audio_dump_snprintf(write_buffer, (uint32_t)write_buffer_len, s_block_cancel);
    return 0;
}

int32_t cli_cmd_single_stop_580376(char *write_buffer, size_t write_buffer_len, const char *command_string)
{
    int32_t length;

    (void)write_buffer;
    (void)write_buffer_len;
    (void)audio_uart_slave_display_stop((uint32_t)cli_int_param(command_string, 1u, &length), NULL, 0u);
    return 0;
}
