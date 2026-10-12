/* Native 0x52e788 selects live image-row count and pointer by transport. */
#include <stdint.h>
extern uint32_t audio_ble_radio_io_mode_52dd1c(uint32_t);
#define W(a) (*(volatile uint32_t *)(uintptr_t)(a))
#define B(a) (*(volatile uint8_t *)(uintptr_t)(a))
uint32_t audio_ble_radio_image_rows_52e788(uint32_t *count,uint32_t *rows,
                                            uint32_t unused,uint32_t passthrough) {
    (void)unused;
    if(audio_ble_radio_io_mode_52dd1c(0u)==0u) {
        *count=B(0x20074f50u);
        *rows=W(0x2007422cu);
    } else {
        *count=B(0x20074f52u);
        *rows=W(0x2007423cu);
    }
    return passthrough;
}
