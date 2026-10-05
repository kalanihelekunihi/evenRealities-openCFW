/* SPDX-License-Identifier: MIT */
/* Reconstructed from stock0x4c2e30..0x4c306a, not SDK source. */
#include "transport_pads.h"
#include "../ambiq_gpio_config/gpio_config.h"
static void pad(uint32_t pin)
{
    am_hal_gpio_pincfg_t cfg;
    cfg.GP.cfg=*(volatile uint32_t *)0x0078ee48;
    (void)am_hal_gpio_pinconfig(pin,cfg);
}
void opencfw_transport_pads_raw(uint32_t instance,uint32_t operation)
{
    if(instance>=8)return;
    /* Stock combines a byte operation with shifted instance, rather than bool. */
    switch((uint8_t)operation | (instance<<2)) {
#define PAD(pin) pad(pin)
    case 0: PAD(5);PAD(7);PAD(6);PAD(50);break;
    case 4: PAD(8);PAD(10);PAD(9);PAD(51);break;
    case 8: PAD(25);PAD(27);PAD(26);PAD(11);break;
    case 12: PAD(31);PAD(33);PAD(32);PAD(13);break;
    case 16: PAD(34);PAD(36);PAD(35);PAD(16);break;
    case 20: PAD(47);PAD(49);PAD(48);PAD(17);break;
    case 24: PAD(61);PAD(63);PAD(62);PAD(117);break;
    case 28: PAD(22);PAD(24);PAD(23);PAD(19);break;
    case 1: PAD(5);PAD(6);break;
    case 5: PAD(8);PAD(9);break;
    case 9: PAD(25);PAD(26);break;
    case 13: PAD(31);PAD(32);break;
    case 17: PAD(34);PAD(35);break;
    case 21: PAD(47);PAD(48);break;
    case 25: PAD(61);PAD(62);break;
    case 29: PAD(22);PAD(23);break;
    default:break;
#undef PAD
    }
}
