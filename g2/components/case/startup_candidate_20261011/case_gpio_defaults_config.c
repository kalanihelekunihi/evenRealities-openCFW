/* SPDX-License-Identifier: MIT
 * Two CASE software-I2C GPIO descriptors from authenticated CRT RAM.
 * Native 0x08004d30 consumes words as pin mask, mode/settings, pull,
 * output speed, alternate function. See bus_gpio_config_candidate.c.
 */
#include <stdint.h>

typedef struct {
    uint32_t pin_mask;
    uint32_t mode_settings;
    uint32_t pull;
    uint32_t output_speed;
    uint32_t alternate_function;
} case_gpio_pin_config;

const case_gpio_pin_config case_gpio_port_b_pin2_default={4u,1u,0u,3u,0u};
const case_gpio_pin_config case_gpio_port_a_pin3_default={8u,1u,0u,3u,0u};
_Static_assert(sizeof(case_gpio_pin_config)==20u,"CASE GPIO descriptor size");

void case_crt_init_gpio_descriptors(void)
{
    const case_gpio_pin_config *defaults[2]={
        &case_gpio_port_b_pin2_default,&case_gpio_port_a_pin3_default};
    const uintptr_t destinations[2]={0x20000014u,0x200000a0u};
    for(uint32_t n=0u;n<2u;++n){
        volatile uint32_t *ram=(volatile uint32_t *)destinations[n];
        const uint32_t *words=(const uint32_t *)defaults[n];
        for(uint32_t i=0u;i<5u;++i)ram[i]=words[i];
    }
}
