/* Apollo 0x55face: index one of the NPMX LDO descriptors. */
#include <stdint.h>

uint32_t display_driver_uled_pmic_ldo_find_55face(uint32_t base,uint32_t index) {
    return base + 0x50u + ((uint8_t)index * 8u);
}
