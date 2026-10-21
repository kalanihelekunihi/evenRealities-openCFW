/* Apollo S200 PMIC helpers 0x55fa0e, 0x55fa40, 0x55fa22, 0x55fa18.
 * The tables at 0x78f30c, 0x78f624, and 0x78f622 remain authenticated ROM.
 */
#include <stdint.h>

extern uint32_t display_driver_uled_pmic_read_55fc38(uint32_t,uint32_t,void *,uint32_t);
extern uint32_t display_driver_uled_pmic_write_55fc2c(uint32_t,uint32_t,const void *,uint32_t);
extern uint32_t display_driver_uled_pmic_commit_lower_55f9e8(uint32_t,uint32_t);

uint32_t display_driver_uled_pmic_find_55fa0e(uint32_t base,uint32_t index) {
    return base + 0x14u + ((uint8_t)index * 8u);
}

void display_driver_uled_pmic_enable_55fa40(uint32_t descriptor,uint32_t enabled) {
    uint32_t device = *(volatile const uint32_t *)(uintptr_t)descriptor;
    uint8_t data = 0u;
    uint32_t status = display_driver_uled_pmic_read_55fc38(device,0x40fu,&data,1u);
    if (status != 0x2bad0000u) return;
    uint8_t index = *(volatile const uint8_t *)(uintptr_t)(descriptor+4u);
    uint8_t mask = *(volatile const uint8_t *)(uintptr_t)(0x78f624u+index);
    uint32_t shift = *(volatile const uint8_t *)(uintptr_t)(0x78f622u+index);
    uint32_t bit = shift < 32u ? ((uint8_t)enabled << shift) : 0u;
    data = (uint8_t)((data & (uint8_t)~mask) | (bit & mask));
    (void)display_driver_uled_pmic_write_55fc2c(device,0x40fu,&data,1u);
}

void display_driver_uled_pmic_voltage_55fa22(uint32_t descriptor,uint32_t voltage) {
    uint8_t data = (uint8_t)(voltage & 0x1fu);
    uint8_t index = *(volatile const uint8_t *)(uintptr_t)(descriptor+4u);
    uint16_t address = *(volatile const uint16_t *)(uintptr_t)(0x78f30cu+2u*index);
    uint32_t device = *(volatile const uint32_t *)(uintptr_t)descriptor;
    (void)display_driver_uled_pmic_write_55fc2c(device,address,&data,1u);
}

uint32_t display_driver_uled_pmic_commit_55fa18(uint32_t descriptor,uint32_t mode) {
    return display_driver_uled_pmic_commit_lower_55f9e8(descriptor,(uint8_t)mode);
}
