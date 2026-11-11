/* Apollo S200 Hongshi register-write descriptor at 0x5bbdf0. */
#include <stdint.h>
/* Stock-RAM literals rewritten to named objects (sim-test wave 2026-10-26,
 * .waves/sim-fix/apply.py): g2ref_X is the linker symbol X. */
#include <stdint.h>
/* Fix 48: stock flash 0x76b12c, 28-byte MSPI transfer template (copy loop bound; stock image bytes). */
static const uint8_t g2_uled_mspi_template_76b12c[28]={0x00u, 0x00u, 0x00u, 0x00u, 0x00u, 0x00u, 0x00u, 0x00u, 0x00u, 0x00u, 0x00u, 0x00u, 0x03u, 0x00u, 0x00u, 0x00u, 0x00u, 0x00u, 0x00u, 0x00u, 0x1cu, 0x45u, 0x07u, 0x20u, 0x00u, 0x00u, 0x00u, 0x00u};
extern unsigned char g2ref_g2_a6ng_mspi_handle[] __asm__("g2_a6ng_mspi_handle");
extern unsigned char g2ref_g2_stock_ram_20074518[] __asm__("g2_stock_ram_20074518");

extern uint32_t display_driver_uled_type0_packet_write_59ccdc(void *);

uint32_t display_driver_uled_type1_write_register_5bbdf0(
        uint32_t address,uint32_t value,uint32_t mode) {
    volatile uint8_t *command=(volatile uint8_t *)(uintptr_t)((uint32_t)(uintptr_t)g2ref_g2_stock_ram_20074518+0x4u);
    command[0]=(uint8_t)(mode==1u?0x7au:0x78u);
    command[1]=(uint8_t)address;
    command[2]=(uint8_t)value;
    uint8_t descriptor[28];
    const uint8_t *template=g2_uled_mspi_template_76b12c;
    for (uint32_t i=0;i<28u;i++) descriptor[i]=template[i];
    uint32_t handle=*(volatile const uint32_t *)(uintptr_t)((uint32_t)(uintptr_t)g2ref_g2_a6ng_mspi_handle);
    for (uint32_t i=0;i<4u;i++) descriptor[24u+i]=(uint8_t)(handle>>(8u*i));
    return display_driver_uled_type0_packet_write_59ccdc(descriptor);
}
