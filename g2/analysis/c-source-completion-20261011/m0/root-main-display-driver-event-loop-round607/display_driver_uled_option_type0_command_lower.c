/* Apollo S200 JBD4010 mode byte and command descriptor helpers. */
#include <stdint.h>

extern uint32_t display_driver_uled_type0_packet_write_59ccdc(void *);

uint32_t display_driver_uled_mode_45a568(void) {
    return *(volatile const uint8_t *)(uintptr_t)0x20075024u;
}

uint32_t display_driver_uled_command_5926ee(uint32_t command,
                                             const void *payload,
                                             uint32_t length) {
    uint8_t descriptor[28]={0};
    descriptor[8]=1u;
    descriptor[9]=(uint8_t)command;
    descriptor[12]=(uint8_t)length;
    descriptor[13]=(uint8_t)(length>>8);
    descriptor[14]=(uint8_t)(length>>16);
    descriptor[15]=(uint8_t)(length>>24);
    uint32_t pointer=(uint32_t)(uintptr_t)payload;
    for (uint32_t i=0;i<4u;i++) descriptor[20u+i]=(uint8_t)(pointer>>(8u*i));
    uint32_t context=*(volatile const uint32_t *)(uintptr_t)0x20074524u;
    for (uint32_t i=0;i<4u;i++) descriptor[24u+i]=(uint8_t)(context>>(8u*i));
    return display_driver_uled_type0_packet_write_59ccdc((void *)descriptor);
}
