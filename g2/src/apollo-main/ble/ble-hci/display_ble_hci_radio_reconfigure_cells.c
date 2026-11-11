/* Native 0x52e5ce and 0x52e5f2 copy accepted product configuration into
 * authenticated live RAM cells. They do not initialize those source inputs. */
#include <stdint.h>
/* Stock-RAM literals rewritten to named objects (sim-test wave 2026-10-26,
 * .waves/sim-fix/apply.py): g2ref_X is the linker symbol X. */
#include <stdint.h>
extern unsigned char g2ref_g2_stock_ram_20074150[] __asm__("g2_stock_ram_20074150");
extern unsigned char g2ref_g2_stock_ram_20074228[] __asm__("g2_stock_ram_20074228");
extern unsigned char g2ref_g2_stock_ram_20074f30[] __asm__("g2_stock_ram_20074f30");
#define W(a) (*(volatile uint32_t *)(uintptr_t)(a))
#define B(a) (*(volatile uint8_t *)(uintptr_t)(a))
uint32_t audio_ble_radio_configure_52e5ce(void *context,uint32_t mode,uint32_t value) {
    if(context==0) return 0u;
    W(((uint32_t)(uintptr_t)g2ref_g2_stock_ram_20074228+0x4u))=(uint32_t)(uintptr_t)context;
    B(((uint32_t)(uintptr_t)g2ref_g2_stock_ram_20074f30+0x20u))=(uint8_t)mode;
    W(((uint32_t)(uintptr_t)g2ref_g2_stock_ram_20074228+0x8u))=value;
    return 1u;
}
uint32_t audio_ble_radio_tune_52e5f2(uint32_t context,uint32_t mode) {
    if(context==0u) return 0u;
    W(((uint32_t)(uintptr_t)g2ref_g2_stock_ram_20074228+0xcu))=context;
    W(((uint32_t)(uintptr_t)g2ref_g2_stock_ram_20074228+0x10u))=(uint8_t)mode;
    return 1u;
}
