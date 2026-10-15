/* Apollo pin bus command 0x4809c4. Candidate from original Thumb MMIO order. */
#include <stdint.h>
extern void display_driver_uled_delay_4807a0(uint32_t);
extern uint32_t display_driver_uled_mspi_dma_pin_prepare_4c44bc(uint32_t,uint32_t);
extern uint32_t display_driver_uled_mspi_pin_control_4c4530(uint32_t,uint32_t);

static uint32_t bus_config_bits(void) {
    uint32_t low=*(volatile uint8_t *)(uintptr_t)0x200001e0u & 0x3fu;
    uint32_t high=(*(volatile uint32_t *)(uintptr_t)0x200001e4u << 6u)&0x3c0u;
    return low | high;
}

uint32_t display_driver_uled_pin_bus_command_4809c4(uint32_t command,
                                                       uint8_t *option) {
    volatile uint32_t *control=(volatile uint32_t *)(uintptr_t)0x40020120u;
    volatile uint32_t *timing=(volatile uint32_t *)(uintptr_t)0x40020128u;
    volatile uint32_t *status=(volatile uint32_t *)(uintptr_t)0x4002012cu;
    switch ((uint8_t)command) {
    case 0u: {
        uint32_t value=*control & ~0x1fu;
        value |= option && *option==1u ? 5u : 0x19u;
        *control=value;
        return 0u;
    }
    case 1u:
        *control=*control & ~3u;
        return 0u;
    case 2u: {
        *timing=(*timing & 0xc0007000u)|bus_config_bits()|0x0fff8c00u;
        *status=(*status & ~0x22u)|2u;
        *status=*status|1u;
        *status=*status|0x10u;
        *status=*status|8u;
        display_driver_uled_delay_4807a0(5u);
        *status=*status & ~0x10u;
        if(option && *option==1u)
            *status=(*status & 0xfffffef6u)|0x100u;
        return 0u;
    }
    case 3u: {
        (void)*timing;
        *timing=bus_config_bits()|0x0fff8c00u;
        *status=(*status & ~0x22u)|0x22u;
        *status=*status|1u;
        uint32_t value=*status;
        if(option && *option==1u)value=(value & 0xfffffefeu)|0x100u;
        else value=(value & ~0x28u)|8u;
        *status=value;
        return 0u;
    }
    case 4u:
        *timing=(*timing & 0xc0007000u)|bus_config_bits()|0x03118000u;
        *status=(*status & 0xfffffed4u)|2u;
        return 0u;
    case 5u: {
        uint32_t result=display_driver_uled_mspi_dma_pin_prepare_4c44bc(2u,0x34u);
        if(result != 0u)return result;
        uint32_t setting=4u;
        if(option) {
            setting=*(const uint32_t *)(const void *)option;
            if(setting != 0u && setting-3u >= 5u)return 6u;
        }
        *timing=(*timing & ~0x7000u)|((setting<<12u)&0x7000u);
        *status=*status|0x80u;
        return 0u;
    }
    case 6u: {
        *timing=*timing|0x7000u;
        *status=*status & ~0x80u;
        return display_driver_uled_mspi_pin_control_4c4530(2u,0x34u);
    }
    default:return 6u;
    }
}
