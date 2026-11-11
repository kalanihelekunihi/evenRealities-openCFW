/* Apollo S200 JBD4010 command descriptor helper. The role-byte caller name
 * at 0x45a568 is a linker alias to audio_uart_device_role_get, not a second
 * implementation in this translation unit. */
#include <stdint.h>
/* Stock-RAM literals rewritten to named objects (sim-test wave 2026-10-26,
 * .waves/sim-fix/apply.py): g2ref_X is the linker symbol X. */
#include <stdint.h>
extern unsigned char g2ref_g2_jbd4010_mspi_handle[] __asm__("g2_jbd4010_mspi_handle");

extern uint32_t display_driver_uled_type0_packet_write_59ccdc(void *);

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
    uint32_t context=*(volatile const uint32_t *)(uintptr_t)((uint32_t)(uintptr_t)g2ref_g2_jbd4010_mspi_handle);
    for (uint32_t i=0;i<4u;i++) descriptor[24u+i]=(uint8_t)(context>>(8u*i));
    return display_driver_uled_type0_packet_write_59ccdc((void *)descriptor);
}
