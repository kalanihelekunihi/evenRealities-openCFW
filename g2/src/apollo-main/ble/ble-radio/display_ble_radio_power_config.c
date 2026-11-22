/* Native 0x4c2b68 pin-function configuration for eight radio power groups.
 * Every live source cell below is the resolved target of a native literal. */
#include <stdint.h>

extern uint32_t g2_codec_pin_function(uint32_t,uint32_t); /* native 0x480f0c */

/* sim15: 0x2000006c..0x20000110 are stock .data pad configs, now
 * g2_stock_ram_2000006c (defined in drivers/flash/nor/nor-clock-select.c; values from .waves/init_20000000.bin). 0x20074204..
 * 0x20074218 are past the stock .data image (zero .bss) and no source writes
 * them, so they map to own zeroed words (flag: stock runtime writer unknown). */
extern uint32_t g2_stock_ram_2000006c[87];
static uint32_t g2_radio_zero_pad_words[6];
#define APPLY_PAD(pin,index) ((void)g2_codec_pin_function((pin), \
    *(volatile const uint32_t *)&g2_stock_ram_2000006c[index]))
#define APPLY_ZERO(pin,index) ((void)g2_codec_pin_function((pin), \
    *(volatile const uint32_t *)&g2_radio_zero_pad_words[index]))

void audio_ble_radio_power_config_4c2b68(uint32_t group,uint32_t setting)
{
    if (group>=8u) return;
    switch ((group<<2u)|(uint32_t)setting) {
        case 0u:
            APPLY_PAD(5u,3u);APPLY_PAD(7u,1u);
            APPLY_PAD(6u,2u);APPLY_PAD(50u,0u);break;
        case 1u:
            APPLY_PAD(5u,4u);APPLY_PAD(6u,5u);break;
        case 4u:
            APPLY_PAD(8u,9u);APPLY_PAD(10u,7u);
            APPLY_PAD(9u,8u);APPLY_PAD(51u,6u);break;
        case 5u:
            APPLY_PAD(8u,10u);APPLY_PAD(9u,11u);break;
        case 8u:
            APPLY_PAD(25u,14u);APPLY_ZERO(27u,0u);
            APPLY_PAD(26u,13u);APPLY_PAD(11u,12u);break;
        case 9u:
            APPLY_PAD(25u,15u);APPLY_PAD(26u,16u);break;
        case 12u:
            APPLY_PAD(31u,19u);APPLY_ZERO(33u,1u);
            APPLY_PAD(32u,18u);APPLY_PAD(13u,17u);break;
        case 13u:
            APPLY_PAD(31u,20u);APPLY_PAD(32u,21u);break;
        case 16u:
            APPLY_PAD(34u,24u);APPLY_ZERO(36u,2u);
            APPLY_PAD(35u,23u);APPLY_PAD(16u,22u);break;
        case 17u:
            APPLY_PAD(34u,25u);APPLY_PAD(35u,26u);break;
        case 20u:
            APPLY_PAD(47u,29u);APPLY_ZERO(49u,3u);
            APPLY_PAD(48u,28u);APPLY_PAD(17u,27u);break;
        case 21u:
            APPLY_PAD(47u,30u);APPLY_PAD(48u,31u);break;
        case 24u:
            APPLY_PAD(61u,34u);APPLY_ZERO(63u,4u);
            APPLY_PAD(62u,33u);APPLY_PAD(117u,32u);break;
        case 25u:
            APPLY_PAD(61u,35u);APPLY_PAD(62u,36u);break;
        case 28u:
            APPLY_PAD(22u,39u);APPLY_ZERO(24u,5u);
            APPLY_PAD(23u,38u);APPLY_PAD(19u,37u);break;
        case 29u:
            APPLY_PAD(22u,40u);APPLY_PAD(23u,41u);break;
        default:break;
    }
}
