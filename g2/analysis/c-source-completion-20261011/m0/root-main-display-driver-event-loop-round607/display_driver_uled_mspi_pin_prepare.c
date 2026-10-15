/* Apollo pin-prepare dispatcher 0x4c44bc. Candidate. */
#include <stdint.h>
extern uint32_t display_driver_uled_pin_prepare_type0_4c3bfc(uint32_t);
extern uint32_t display_driver_uled_pin_prepare_type1_4c3c60(uint32_t);
extern uint32_t display_driver_uled_pin_prepare_type2_4c3d9e(uint32_t);
extern uint32_t display_driver_uled_pin_prepare_type3_4c3cd4(uint32_t);
extern uint32_t display_driver_uled_pin_prepare_type4_4c3f2a(uint32_t);
extern uint32_t display_driver_uled_pin_prepare_type5_4c4086(uint32_t);
extern uint32_t display_driver_uled_pin_prepare_type6_4c427e(uint32_t);

uint32_t display_driver_uled_mspi_dma_pin_prepare_4c44bc(uint32_t kind,
                                                             uint32_t pin) {
    uint32_t index = (uint8_t)pin;
    if (index >= 0x39u) return 6u;
    switch ((uint8_t)kind) {
    case 0u: return display_driver_uled_pin_prepare_type0_4c3bfc(index);
    case 1u: return display_driver_uled_pin_prepare_type1_4c3c60(index);
    case 2u: return display_driver_uled_pin_prepare_type2_4c3d9e(index);
    case 3u: return display_driver_uled_pin_prepare_type3_4c3cd4(index);
    case 4u: return display_driver_uled_pin_prepare_type4_4c3f2a(index);
    case 5u: return display_driver_uled_pin_prepare_type5_4c4086(index);
    case 6u: return display_driver_uled_pin_prepare_type6_4c427e(index);
    default: return 6u;
    }
}
