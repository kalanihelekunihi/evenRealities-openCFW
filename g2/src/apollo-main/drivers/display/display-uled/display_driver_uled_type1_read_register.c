/* Apollo S200 Hongshi register-read descriptor at 0x5bbe3e. */
#include <stdint.h>
/* Stock-RAM literals rewritten to named objects (sim-test wave 2026-10-26,
 * .waves/sim-fix/apply.py): g2ref_X is the linker symbol X. */
#include <stdint.h>
/* Fix 48: stock flash 0x76b148, 28-byte MSPI transfer template (copy loop bound; stock image bytes). */
static const uint8_t g2_uled_mspi_template_76b148[28]={0x01u, 0x00u, 0x00u, 0x00u, 0x00u, 0x00u, 0x00u, 0x00u, 0x00u, 0x00u, 0x00u, 0x00u, 0x00u, 0x00u, 0x00u, 0x00u, 0x01u, 0x00u, 0x00u, 0x00u, 0x00u, 0x00u, 0x00u, 0x00u, 0x00u, 0x00u, 0x00u, 0x00u};
extern unsigned char g2ref_g2_a6ng_mspi_handle[] __asm__("g2_a6ng_mspi_handle");

extern uint32_t display_driver_uled_type0_packet_59cc40(void *);

uint32_t display_driver_uled_type1_read_register_5bbe3e(
        uint32_t bank,uint32_t *output,uint32_t count,uint32_t mode) {
    uint8_t descriptor[28];
    const uint8_t *template=g2_uled_mspi_template_76b148;
    for (uint32_t i=0;i<28u;i++) descriptor[i]=template[i];
    uint32_t command=(bank&0xffu)|((mode==1u?0x7bu:0x79u)<<8);
    uint32_t words[4]={command,count,(uint32_t)(uintptr_t)output,
        *(volatile const uint32_t *)(uintptr_t)((uint32_t)(uintptr_t)g2ref_g2_a6ng_mspi_handle)};
    const uint32_t offsets[4]={4u,12u,20u,24u};
    for (uint32_t j=0;j<4u;j++)
        for (uint32_t i=0;i<4u;i++)
            descriptor[offsets[j]+i]=(uint8_t)(words[j]>>(8u*i));
    return display_driver_uled_type0_packet_59cc40(descriptor);
}
