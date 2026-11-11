/* Native 0x52e788 selects live image-row count and pointer by transport. */
#include <stdint.h>
/* Stock-RAM literals rewritten to named objects (sim-test wave 2026-10-26,
 * .waves/sim-fix/apply.py): g2ref_X is the linker symbol X. */
#include <stdint.h>
extern unsigned char g2ref_g2_stock_ram_20074150[] __asm__("g2_stock_ram_20074150");
extern unsigned char g2ref_g2_stock_ram_20074228[] __asm__("g2_stock_ram_20074228");
extern unsigned char g2ref_g2_stock_ram_20074f30[] __asm__("g2_stock_ram_20074f30");
extern uint32_t audio_ble_radio_io_mode_52dd1c(uint32_t);
#define W(a) (*(volatile uint32_t *)(uintptr_t)(a))
#define B(a) (*(volatile uint8_t *)(uintptr_t)(a))
uint32_t audio_ble_radio_image_rows_52e788(uint32_t *count,uint32_t *rows,
                                            uint32_t unused,uint32_t passthrough) {
    (void)unused;
    if(audio_ble_radio_io_mode_52dd1c(0u)==0u) {
        *count=B(((uint32_t)(uintptr_t)g2ref_g2_stock_ram_20074f30+0x20u));
        *rows=W(((uint32_t)(uintptr_t)g2ref_g2_stock_ram_20074228+0x4u));
    } else {
        *count=B(((uint32_t)(uintptr_t)g2ref_g2_stock_ram_20074f30+0x22u));
        *rows=W(((uint32_t)(uintptr_t)g2ref_g2_stock_ram_20074228+0x14u));
    }
    return passthrough;
}
