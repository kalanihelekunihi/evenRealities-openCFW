/* Apollo Ambiq GPU clear wrapper 0x4b1a78..0x4b1aa9. Candidate. */
#include <stdint.h>
extern volatile uint32_t audio_uart_nema_context_cell[1]; /* selected 0x20074efc */
extern void display_driver_nema_mode_513924(uint32_t,int32_t,int32_t,int32_t);
extern void display_driver_nema_select_522a16(uint32_t);
extern void display_driver_nema_clear_522ae0(uint32_t,uint32_t,uint32_t,uint32_t);
void display_driver_gpu_clear_4b1a78(uint32_t unit) {
    display_driver_nema_mode_513924(1u,0,-1,-1);
    volatile uint8_t *ctx=(volatile uint8_t *)(uintptr_t)audio_uart_nema_context_cell[0];
    uint32_t last=*(volatile uint32_t *)(void *)(ctx+0x40u);
    uint32_t first=*(volatile uint32_t *)(void *)(ctx+0x3cu);
    display_driver_nema_select_522a16(unit);
    display_driver_nema_clear_522ae0(0u,0u,first,last);
}
