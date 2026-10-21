/* Native image-B startup children 0x10004808, 0x1000482c, 0x100051a4,
 * 0x1000800c, 0x10008018, and 0x100081ec. These retain genuine MMIO,
 * BSS, clock, and callback contracts; no default device result is supplied.
 */
#include <stdint.h>

extern volatile uint32_t gx8002_image_b_console_port_2001739c;
extern volatile uint32_t gx8002_image_b_gpio_irq_masks_200173a0[2];
extern int32_t gx8002_image_b_uart_configure_1000451c(uint32_t,
                                                        uint32_t);
extern void gx8002_image_b_cache_stage_10004fac(void);
extern void gx8002_image_b_cache_stage_10004db4(void);
extern void gx8002_image_b_cache_stage_10004d94(void);
extern void gx8002_image_b_platform_gate_10003be8(uint32_t,
                                                    uint32_t);

void gx8002_image_b_console_initialize_10004808(uint32_t port,
                                                  uint32_t baud)
{
    gx8002_image_b_console_port_2001739c = port;
    (void)gx8002_image_b_uart_configure_1000451c(port, baud);
}

void gx8002_image_b_gpio_initialize_1000482c(void)
{
    volatile uint32_t *const irq =
        (volatile uint32_t *)(uintptr_t)UINT32_C(0xe000e100);
    irq[0] = gx8002_image_b_gpio_irq_masks_200173a0[0];
    irq[1] = gx8002_image_b_gpio_irq_masks_200173a0[1];
}

void gx8002_image_b_cache_initialize_100051a4(void)
{
    gx8002_image_b_cache_stage_10004fac();
    gx8002_image_b_cache_stage_10004db4();
    *(volatile uint32_t *)(uintptr_t)UINT32_C(0xe000f014) =
        UINT32_C(0x20000023);
    gx8002_image_b_cache_stage_10004d94();
}

/* The flash device's callback pointer fields are at +0x30 and +0x34.
 * Native 0x800c calls the type callback with no extra argument; 0x8018
 * calls the info callback with the selector or returns UINT32_MAX.
 */
const char *gx8002_image_b_flash_type_1000800c(uint32_t flash)
{
    uint32_t callback = *(const uint32_t *)(uintptr_t)(flash + 0x30u);
    if (callback == 0u)
        return (const char *)(uintptr_t)0u;
    return ((const char *(*)(void))(uintptr_t)callback)();
}

uint32_t gx8002_image_b_flash_info_10008018(uint32_t flash,
                                              uint32_t selector)
{
    uint32_t callback = *(const uint32_t *)(uintptr_t)(flash + 0x34u);
    if (callback == 0u)
        return UINT32_MAX;
    return ((uint32_t (*)(uint32_t))(uintptr_t)callback)(selector);
}

void gx8002_image_b_rtc_initialize_100081ec(void)
{
    gx8002_image_b_platform_gate_10003be8(4u, 1u);
    *(volatile uint32_t *)(uintptr_t)UINT32_C(0xa0001034) = 0u;
}
