/* Native 0x4c2b68 pin-function configuration for eight radio power groups.
 * Every live source cell below is the resolved target of a native literal. */
#include <stdint.h>

extern uint32_t g2_codec_pin_function(uint32_t,uint32_t); /* native 0x480f0c */

#define APPLY(pin,address) ((void)g2_codec_pin_function((pin), \
    *(volatile const uint32_t *)(uintptr_t)(address)))

void audio_ble_radio_power_config_4c2b68(uint32_t group,uint8_t setting)
{
    if (group>=8u) return;
    switch ((group<<2u)|(uint32_t)setting) {
        case 0u:
            APPLY(5u,0x20000078u);APPLY(7u,0x20000070u);
            APPLY(6u,0x20000074u);APPLY(50u,0x2000006cu);break;
        case 1u:
            APPLY(5u,0x2000007cu);APPLY(6u,0x20000080u);break;
        case 4u:
            APPLY(8u,0x20000090u);APPLY(10u,0x20000088u);
            APPLY(9u,0x2000008cu);APPLY(51u,0x20000084u);break;
        case 5u:
            APPLY(8u,0x20000094u);APPLY(9u,0x20000098u);break;
        case 8u:
            APPLY(25u,0x200000a4u);APPLY(27u,0x20074204u);
            APPLY(26u,0x200000a0u);APPLY(11u,0x2000009cu);break;
        case 9u:
            APPLY(25u,0x200000a8u);APPLY(26u,0x200000acu);break;
        case 12u:
            APPLY(31u,0x200000b8u);APPLY(33u,0x20074208u);
            APPLY(32u,0x200000b4u);APPLY(13u,0x200000b0u);break;
        case 13u:
            APPLY(31u,0x200000bcu);APPLY(32u,0x200000c0u);break;
        case 16u:
            APPLY(34u,0x200000ccu);APPLY(36u,0x2007420cu);
            APPLY(35u,0x200000c8u);APPLY(16u,0x200000c4u);break;
        case 17u:
            APPLY(34u,0x200000d0u);APPLY(35u,0x200000d4u);break;
        case 20u:
            APPLY(47u,0x200000e0u);APPLY(49u,0x20074210u);
            APPLY(48u,0x200000dcu);APPLY(17u,0x200000d8u);break;
        case 21u:
            APPLY(47u,0x200000e4u);APPLY(48u,0x200000e8u);break;
        case 24u:
            APPLY(61u,0x200000f4u);APPLY(63u,0x20074214u);
            APPLY(62u,0x200000f0u);APPLY(117u,0x200000ecu);break;
        case 25u:
            APPLY(61u,0x200000f8u);APPLY(62u,0x200000fcu);break;
        case 28u:
            APPLY(22u,0x20000108u);APPLY(24u,0x20074218u);
            APPLY(23u,0x20000104u);APPLY(19u,0x20000100u);break;
        case 29u:
            APPLY(22u,0x2000010cu);APPLY(23u,0x20000110u);break;
        default:break;
    }
}
