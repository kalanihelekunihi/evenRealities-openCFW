/* Apollo S200 PMIC transport wrappers 0x55fc38, 0x55fc2c, 0x55f9e8.
 * The mode/register map at 0x787b30 remains authenticated ROM data.
 */
#include <stdint.h>

typedef uint32_t (*pmic_transfer)(uint32_t,uint32_t,void *,uint32_t);

uint32_t display_driver_uled_pmic_read_55fc38(uint32_t transport,
                                                uint32_t address,
                                                void *buffer,uint32_t count) {
    pmic_transfer read = *(pmic_transfer *)(uintptr_t)(transport+4u);
    uint32_t context = *(volatile const uint32_t *)(uintptr_t)(transport+8u);
    return read(context,address,buffer,count);
}

uint32_t display_driver_uled_pmic_write_55fc2c(uint32_t transport,
                                                 uint32_t address,
                                                 const void *buffer,uint32_t count) {
    pmic_transfer write = *(pmic_transfer *)(uintptr_t)transport;
    uint32_t context = *(volatile const uint32_t *)(uintptr_t)(transport+8u);
    return write(context,address,(void *)buffer,count);
}

uint32_t display_driver_uled_pmic_commit_lower_55f9e8(uint32_t descriptor,
                                                        uint32_t mode) {
    uint8_t value = 1u;
    uint8_t index = *(volatile const uint8_t *)(uintptr_t)(descriptor+4u);
    uint32_t table = 0x787b30u + 4u*(uint8_t)mode;
    uint16_t address = *(volatile const uint16_t *)(uintptr_t)(table+2u*index);
    uint32_t transport = *(volatile const uint32_t *)(uintptr_t)descriptor;
    return display_driver_uled_pmic_write_55fc2c(transport,address,&value,1u);
}
