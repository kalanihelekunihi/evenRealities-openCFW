/* SPDX-License-Identifier: MIT
 * Recovered notification/UART setup; candidate pending qualification.
 */
#include <stdint.h>
struct notification_uart_config { int32_t port; uint32_t baudrate,magic,reinit_flag; };
extern int printf(const char *,...);
extern void open_cfw_gx8002_notification_gpio_value(uint32_t,uint32_t);
extern void open_cfw_gx8002_notification_gpio_direction(uint32_t,uint32_t);
extern int open_cfw_gx8002_notification_uart_done(void);
extern int open_cfw_gx8002_notification_uart_init(struct notification_uart_config *);
extern void open_cfw_gx8002_app_commands(void);
extern void *memcpy(void *,const void *,unsigned long);
const char open_cfw_gx8002_notification_pin[] __attribute__((aligned(1)))="[VC_MESSAGE]NOTIFY PIN %d\n";
const char open_cfw_gx8002_notification_uart[] __attribute__((aligned(1)))="[VC_MESSAGE]MASSAGE UART %d\n";

extern const char open_cfw_gx8002_notification_log[];
const struct { char name[16]; struct notification_uart_config config; } open_cfw_gx8002_notification_bundle={"_uartMsgInit",{0,115200,0x58585542,1}};
#define open_cfw_gx8002_notification_name open_cfw_gx8002_notification_bundle.name
#define open_cfw_gx8002_notification_config open_cfw_gx8002_notification_bundle.config
int open_cfw_gx8002_notification_setup(void)
{
    printf(open_cfw_gx8002_notification_pin,2);
    open_cfw_gx8002_notification_gpio_value(2,1);
    open_cfw_gx8002_notification_gpio_direction(2,1);
    printf(open_cfw_gx8002_notification_uart,0);
    printf(open_cfw_gx8002_notification_log,open_cfw_gx8002_notification_name,464);
    open_cfw_gx8002_notification_uart_done();
    struct notification_uart_config config;
    memcpy(&config,&open_cfw_gx8002_notification_config,sizeof config);
    open_cfw_gx8002_notification_uart_init(&config);
    open_cfw_gx8002_app_commands();return 0;
}
