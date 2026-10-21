/* SPDX-License-Identifier: MIT
 * Native image-A XIP sample-app one-shot initialization 0x10208e4c
 * and notification/UART setup 0x102096fc. The stack UART descriptor
 * comes from exact stock 0x1020b688..0x1020b697 initializer words.
 */
#include <stdint.h>

extern uint32_t gx8002_xip_tws_publish_10206c24(const char *, ...);
extern uint32_t g2_codec_gpio_set_level(uint32_t, uint32_t);
extern uint32_t gx8002_xip_gpio_set_direction_10205f24(uint32_t, uint32_t);
extern uint32_t gx8002_xip_uart_async_done_1020854c(void);
extern int32_t gx8002_xip_uart_async_initialize_10208458(const uint32_t *);
extern uint32_t gx8002_xip_power_lock_create_10207770(void *);
extern int32_t gx8002_xip_app_commands_10209258(void);

static volatile uint32_t *const application =
    (volatile uint32_t *)(uintptr_t)UINT32_C(0x2002e8c4);

__attribute__((section(".gx8002.xip.notification_uart_settings")))
const uint32_t gx8002_notification_uart_settings[4] = {
    0u, 115200u, UINT32_C(0x58585542), 1u
};

uint32_t gx8002_xip_notification_setup_102096fc(void)
{
    (void)gx8002_xip_tws_publish_10206c24(
        "[VC_MESSAGE]NOTIFY PIN %d\n", 2);
    (void)g2_codec_gpio_set_level(2u, 1u);
    (void)gx8002_xip_gpio_set_direction_10205f24(2u, 1u);
    (void)gx8002_xip_tws_publish_10206c24(
        "[VC_MESSAGE]MASSAGE UART %d\n", 0);
    (void)gx8002_xip_tws_publish_10206c24(
        "[%s]%d\n", "_uartMsgInit", 464);
    (void)gx8002_xip_uart_async_done_1020854c();
    uint32_t settings[4];
    for (uint32_t index = 0u; index < 4u; ++index)
        settings[index] = gx8002_notification_uart_settings[index];
    (void)gx8002_xip_uart_async_initialize_10208458(settings);
    (void)gx8002_xip_app_commands_10209258();
    return 0u;
}

uint32_t gx8002_xip_sample_app_init_10208e4c(void)
{
    if (application[4] != 0u) return 0u;
    application[4] = 1u;
    (void)gx8002_xip_tws_publish_10206c24(
        "[YW_APP][%s]%d\n", "SampleAppInit", 349);
    (void)gx8002_xip_notification_setup_102096fc();
    (void)gx8002_xip_power_lock_create_10207770(
        (void *)(uintptr_t)UINT32_C(0x2002e8cc));
    return 0u;
}
