#include <stdint.h>

/* Native 0x5a423c..0x5a4323. The route table is product RAM at
 * 0x2005665c; its producer and initial values remain external. */
extern volatile uint32_t g2_audio_voltage_routes[];

static uint32_t five(uint32_t word, uint32_t shift) {
    return (word >> shift) & 31u;
}

/* Stock 0x005A423C (PCM2.2 TON adjust) */
void callback_voltage(uint32_t source, uint32_t selection) {
    uint32_t first, second;
    if (selection == 8u)
        source = 7u;
    switch (source) {
    case 0u:
        first = five(g2_audio_voltage_routes[0x5cu / 4u], 0u);
        second = five(g2_audio_voltage_routes[0x5cu / 4u], 10u);
        break;
    case 1u:
        first = five(g2_audio_voltage_routes[0x5cu / 4u], 5u);
        second = five(g2_audio_voltage_routes[0x5cu / 4u], 15u);
        break;
    case 2u:
        first = five(g2_audio_voltage_routes[0x54u / 4u], 0u);
        second = five(g2_audio_voltage_routes[0x58u / 4u], 0u);
        break;
    case 3u:
        first = five(g2_audio_voltage_routes[0x54u / 4u], 10u);
        second = five(g2_audio_voltage_routes[0x58u / 4u], 10u);
        break;
    case 4u:
        first = five(g2_audio_voltage_routes[0x54u / 4u], 5u);
        second = five(g2_audio_voltage_routes[0x58u / 4u], 5u);
        break;
    case 6u:
        first = five(g2_audio_voltage_routes[0x60u / 4u], 0u);
        second = five(g2_audio_voltage_routes[0x60u / 4u], 10u);
        break;
    case 7u:
        first = five(*(volatile uint32_t *)(uintptr_t)0x40020344u, 11u);
        second = five(*(volatile uint32_t *)(uintptr_t)0x40020354u, 17u);
        break;
    default:
        first = five(g2_audio_voltage_routes[0x54u / 4u], 15u);
        second = five(g2_audio_voltage_routes[0x58u / 4u], 15u);
        break;
    }
    volatile uint32_t *const first_reg =
        (volatile uint32_t *)(uintptr_t)0x40020344u;
    volatile uint32_t *const second_reg =
        (volatile uint32_t *)(uintptr_t)0x40020358u;
    *first_reg = (*first_reg & ~(31u << 25)) | (first << 25);
    *second_reg = (*second_reg & ~(31u << 8)) | (second << 8);
}
