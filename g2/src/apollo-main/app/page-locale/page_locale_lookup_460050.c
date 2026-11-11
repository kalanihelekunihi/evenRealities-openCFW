/* Native locale search 0x460050..0x46008f; table contents remain a RAM gate. */
#include <stdint.h>
/* Stock-RAM literals rewritten to named objects (sim-test wave 2026-10-26,
 * .waves/sim-fix/apply.py): g2ref_X is the linker symbol X. */
#include <stdint.h>
extern unsigned char g2ref_g2_stock_ram_20002928[] __asm__("g2_stock_ram_20002928");

extern int32_t audio_uart_font_path_compare(const char *,const char *);

uint32_t audio_uart_page_460050(const char *key,const char *const *table,
                                int32_t count)
{
    uint32_t index=0u;
    while ((int32_t)(uint16_t)index<count) {
        if (audio_uart_font_path_compare(table[(uint16_t)index],key)==0)
            return (uint16_t)index;
        ++index;
    }
    return 0xffffu;
}

uint32_t audio_uart_page_460084(const char *key)
{
    return audio_uart_page_460050(key,(const char *const *)(uintptr_t)((uint32_t)(uintptr_t)g2ref_g2_stock_ram_20002928),
                                  0x9du);
}
