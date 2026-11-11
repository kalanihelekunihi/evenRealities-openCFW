/* Stock 0x4f1f8: report the BSN-selected touch matrix and ring size. */
#include <stdint.h>

extern uint32_t r1_hardware_variant_bsn_detect(void);
extern uint32_t r1_product_sn_letter_decode(void);
extern void r1_eat_respond_format(const char *format, ...);

void r1_eat_callback_0004f1f8(char *argument)
{
    (void)argument;
    const uint32_t variant = r1_hardware_variant_bsn_detect();
    const uint32_t size = r1_product_sn_letter_decode();
    const char *const format = variant == 1u
        ? "touch_hw:8x3(24ch), ring_size:%d\r\n"
        : "touch_hw:7x3(21ch), ring_size:%d\r\n";
    r1_eat_respond_format(format, size);
}
