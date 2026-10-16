/* Native0x565f4 registrar and source-owned device_stacmd record. */
#include <stdint.h>
#include "native_stacmd.h"
extern void r1_twi_gpio_low(uint32_t),r1_twi_gpio_high(uint32_t),r1_twi_gpio_output(uint32_t),r1_twi_gpio_input(uint32_t,uint32_t),r1_twi_gpio_release(uint32_t);
extern uint32_t r1_twi_gpio_read(uint32_t);
extern void r1_rtt_delay_cycles(uint32_t);
void r1_stacmd_delay_us(uint32_t us) {if (us) r1_rtt_delay_cycles(us<<6);}
const char r1_stacmd_name[] __attribute__((section(".r1.stacmd.name")))="device_stacmd";
r1_stacmd_configuration r1_stacmd __attribute__((section(".r1.stacmd.configuration")))={
 .name=r1_stacmd_name,.config_08=5,.pin=33,.low=r1_twi_gpio_low,.high=r1_twi_gpio_high,.output=r1_twi_gpio_output,.input=r1_twi_gpio_input,
 .pull=3,.delay_us=r1_stacmd_delay_us,.read_pin=r1_twi_gpio_read,.release=r1_twi_gpio_release,
 .ops={.open=r1_stacmd_open,.close=r1_stacmd_close,.read=r1_stacmd_read,.write=r1_stacmd_write}
};
uint32_t r1_yhm2710_stacmd_binding_configuration(void) {
 r1_stacmd.device.name=r1_stacmd.name;r1_stacmd.device.ops=(const void *)&r1_stacmd.ops;
 return r1_stock_registry_register(&r1_stacmd.device);
}
