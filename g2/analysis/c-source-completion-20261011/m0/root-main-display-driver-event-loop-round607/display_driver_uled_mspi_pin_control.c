/* Apollo pin-control dispatcher 0x4c4530. Candidate. */
#include <stdint.h>
extern uint32_t display_driver_uled_pin_control_type0_4c3c2e(uint32_t);
extern uint32_t display_driver_uled_pin_control_type1_4c3ca2(uint32_t);
extern uint32_t display_driver_uled_pin_control_type2_4c3e9a(uint32_t);
extern uint32_t display_driver_uled_pin_control_type3_4c3d28(uint32_t);
extern uint32_t display_driver_uled_pin_control_type4_4c4016(uint32_t);
extern uint32_t display_driver_uled_pin_control_type5_4c420c(uint32_t);
extern uint32_t display_driver_uled_pin_control_type6_4c43ec(uint32_t);

uint32_t display_driver_uled_mspi_pin_control_4c4530(uint32_t kind,
                                                       uint32_t pin) {
    uint32_t index = (uint8_t)pin;
    if (index >= 0x39u) return 6u;
    switch ((uint8_t)kind) {
    case 0u: return display_driver_uled_pin_control_type0_4c3c2e(index);
    case 1u: return display_driver_uled_pin_control_type1_4c3ca2(index);
    case 2u: return display_driver_uled_pin_control_type2_4c3e9a(index);
    case 3u: return display_driver_uled_pin_control_type3_4c3d28(index);
    case 4u: return display_driver_uled_pin_control_type4_4c4016(index);
    case 5u: return display_driver_uled_pin_control_type5_4c420c(index);
    case 6u: return display_driver_uled_pin_control_type6_4c43ec(index);
    default: return 6u;
    }
}
