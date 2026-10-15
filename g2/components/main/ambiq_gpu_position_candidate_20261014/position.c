/* Apollo GPU origin and extent dispatch, native 0x4b1b48..0x4b1b83. */
#include <stdint.h>

extern volatile uint32_t audio_uart_ambiq_unit_cell[1];
extern void display_driver_nema_float_translate_5228b0(float, float)
    __attribute__((pcs("aapcs-vfp")));
extern uint32_t audio_uart_nema_mask_rectangle_522ae0(int32_t, int32_t,
                                                        int32_t, int32_t);

void display_driver_gpu_position_4b1b48(int32_t x, int32_t y)
{
    display_driver_nema_float_translate_5228b0((float)x, (float)y);
    volatile uint8_t *const unit =
        (volatile uint8_t *)(uintptr_t)audio_uart_ambiq_unit_cell[0];
    int32_t const width = *(volatile int32_t *)(void *)(unit + 0x54u);
    int32_t const height = *(volatile int32_t *)(void *)(unit + 0x58u);
    (void)audio_uart_nema_mask_rectangle_522ae0(x, y, width, height);
}
