/* Apollo S200 type-0 register-write packet wrapper at 0x5926ee. */
#include <stdint.h>

extern uint32_t display_driver_uled_type0_packet_write_59ccdc(void *);

uint32_t display_driver_uled_type0_aux_reg_write_5926ee(uint32_t command,
                                                         const void *buffer,
                                                         uint32_t length) {
    /* Literal at 0x593288 points to the 28-byte template at 0x76b244. */
    uint32_t packet[7]={0u,0u,1u,0u,0u,0u,0u};
    ((uint8_t *)packet)[9]=(uint8_t)command;
    packet[3]=length;
    packet[5]=(uint32_t)(uintptr_t)buffer;
    packet[6]=*(volatile const uint32_t *)(uintptr_t)0x20074524u;
    return display_driver_uled_type0_packet_write_59ccdc(packet);
}
