/* Apollo S200 Hongshi register-write descriptor at 0x5bbdf0. */
#include <stdint.h>

extern uint32_t display_driver_uled_type0_packet_write_59ccdc(void *);

uint32_t display_driver_uled_type1_write_register_5bbdf0(
        uint32_t address,uint32_t value,uint32_t mode) {
    volatile uint8_t *command=(volatile uint8_t *)(uintptr_t)0x2007451cu;
    command[0]=(uint8_t)(mode==1u?0x7au:0x78u);
    command[1]=(uint8_t)address;
    command[2]=(uint8_t)value;
    uint8_t descriptor[28];
    const uint8_t *template=(const uint8_t *)(uintptr_t)0x76b12cu;
    for (uint32_t i=0;i<28u;i++) descriptor[i]=template[i];
    uint32_t handle=*(volatile const uint32_t *)(uintptr_t)0x20074510u;
    for (uint32_t i=0;i<4u;i++) descriptor[24u+i]=(uint8_t)(handle>>(8u*i));
    return display_driver_uled_type0_packet_write_59ccdc(descriptor);
}
