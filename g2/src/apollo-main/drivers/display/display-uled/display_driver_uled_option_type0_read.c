/* Apollo S200 type-0 register-read packet wrapper at 0x59275e. */
#include <stdint.h>
/* Stock-RAM literals rewritten to named objects (sim-test wave 2026-10-26,
 * .waves/sim-fix/apply.py): g2ref_X is the linker symbol X. */
#include <stdint.h>
extern unsigned char g2ref_g2_jbd4010_mspi_handle[] __asm__("g2_jbd4010_mspi_handle");

extern uint32_t display_driver_uled_type0_packet_59cc40(void *);

uint32_t display_driver_uled_type0_read_59275e(uint32_t command,void *buffer,
                                                uint32_t length) {
    /* Literal at 0x59330c points to the 28-byte template at 0x76b27c. */
    uint32_t packet[7] = {0u,0u,1u,0u,1u,0u,0u};
    ((uint8_t *)packet)[9]=(uint8_t)command;
    packet[3]=length;
    packet[5]=(uint32_t)(uintptr_t)buffer;
    packet[6]=*(volatile const uint32_t *)(uintptr_t)((uint32_t)(uintptr_t)g2ref_g2_jbd4010_mspi_handle);
    return display_driver_uled_type0_packet_59cc40(packet);
}
