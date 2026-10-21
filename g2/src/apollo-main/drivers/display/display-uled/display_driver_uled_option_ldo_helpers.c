/* Apollo S200 LDO helpers 0x55fad8, 0x55faa8, 0x55fb7c, 0x55fae2.
 * Address, mask, and shift tables remain authenticated ROM data.
 */
#include <stdint.h>

extern uint32_t display_driver_uled_pmic_read_55fc38(uint32_t,uint32_t,void *,uint32_t);
extern uint32_t display_driver_uled_pmic_write_55fc2c(uint32_t,uint32_t,const void *,uint32_t);

uint32_t display_driver_uled_pmic_ldo_commit_lower_55faa8(uint32_t descriptor,
                                                            uint32_t mode) {
    uint8_t value=1u;
    uint8_t index=*(volatile const uint8_t *)(uintptr_t)(descriptor+4u);
    uint32_t table=0x78de14u+4u*(uint8_t)mode;
    uint16_t address=*(volatile const uint16_t *)(uintptr_t)(table+2u*index);
    uint32_t transport=*(volatile const uint32_t *)(uintptr_t)descriptor;
    return display_driver_uled_pmic_write_55fc2c(transport,address,&value,1u);
}

uint32_t display_driver_uled_pmic_ldo_commit_55fad8(uint32_t descriptor,
                                                      uint32_t mode) {
    return display_driver_uled_pmic_ldo_commit_lower_55faa8(descriptor,(uint8_t)mode);
}

uint32_t display_driver_uled_pmic_ldo_switch_55fb7c(uint32_t descriptor,
                                                      uint32_t enabled) {
    uint8_t index=*(volatile const uint8_t *)(uintptr_t)(descriptor+4u);
    uint16_t address=*(volatile const uint16_t *)(uintptr_t)(0x78f314u+2u*index);
    uint32_t transport=*(volatile const uint32_t *)(uintptr_t)descriptor;
    uint8_t data=0u;
    uint32_t status=display_driver_uled_pmic_read_55fc38(transport,address,&data,1u);
    if (status!=0x2bad0000u) return status;
    uint8_t mask=*(volatile const uint8_t *)(uintptr_t)(0x78f630u+index);
    uint32_t shift=*(volatile const uint8_t *)(uintptr_t)(0x78f62eu+index);
    uint32_t bit=shift<32u ? ((enabled!=0u ? 1u : 0u)<<shift) : 0u;
    data=(uint8_t)((data & (uint8_t)~mask) | (bit & mask));
    status=display_driver_uled_pmic_write_55fc2c(transport,address,&data,1u);
    return status;
}

uint32_t display_driver_uled_pmic_ldo_config_55fae2(uint32_t descriptor,
                                                      const void *configuration) {
    uint32_t transport=*(volatile const uint32_t *)(uintptr_t)descriptor;
    uint8_t index=*(volatile const uint8_t *)(uintptr_t)(descriptor+4u);
    uint8_t data=0u;
    uint32_t status=display_driver_uled_pmic_read_55fc38(transport,0x807u,&data,1u);
    if (status!=0x2bad0000u) return status;
    uint8_t mask4=*(volatile const uint8_t *)(uintptr_t)(0x78f628u+index);
    uint8_t mask0=*(volatile const uint8_t *)(uintptr_t)(0x78f62cu+index);
    uint32_t shift4=*(volatile const uint8_t *)(uintptr_t)(0x78f626u+index);
    uint32_t shift0=*(volatile const uint8_t *)(uintptr_t)(0x78f62au+index);
    const uint8_t *bytes=(const uint8_t *)configuration;
    uint32_t bit4=shift4<32u ? ((uint32_t)bytes[4]<<shift4) : 0u;
    uint32_t bit0=shift0<32u ? ((bytes[0]==0u ? 1u : 0u)<<shift0) : 0u;
    data=(uint8_t)((data & (uint8_t)~mask4 & (uint8_t)~mask0) |
                   (bit4 & mask4) | (bit0 & mask0));
    status=display_driver_uled_pmic_write_55fc2c(transport,0x807u,&data,1u);
    return status;
}
