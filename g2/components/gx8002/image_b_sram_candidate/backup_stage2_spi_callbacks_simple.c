/* Native image-B SPI descriptor callback leaves 0x1000827c and
 * 0x10008538. The latter preserves even-divider rounding and the
 * already-registered master error path; no clock frequency is assumed.
 */
#include <stdint.h>

extern uint32_t gx8002_image_b_clock_frequency_10003cf0(uint32_t);
extern volatile uint32_t gx8002_image_b_spi_device_state_20017670[21];

void gx8002_image_b_spi_callback_1000827c(uint32_t *master)
{
    uint32_t *device = (uint32_t *)(uintptr_t)master[0];
    uint32_t *descriptor = (uint32_t *)(uintptr_t)device[0x18u / 4u];
    volatile uint32_t *controller =
        (volatile uint32_t *)(uintptr_t)descriptor[1];
    controller[0x08u / 4u] = 0u;
}

int32_t gx8002_image_b_spi_callback_10008538(uint8_t *record)
{
    *(uint16_t *)(void *)(record + 0x0au) = 0u;
    if (record[0x09u] == 0u)
        record[0x09u] = 8u;
    volatile uint32_t *device =
        (volatile uint32_t *)(uintptr_t)
            *(uint32_t *)(void *)(record + 0x0cu);
    if (device == 0) {
        if (gx8002_image_b_spi_device_state_20017670[0] != 0u)
            return -12;
        device = gx8002_image_b_spi_device_state_20017670;
    }
    uint32_t requested = *(uint32_t *)(void *)(record + 0x04u);
    if (requested == 0u) {
        requested = UINT32_C(10000000);
        *(uint32_t *)(void *)(record + 0x04u) = requested;
    }
    uint32_t frequency = gx8002_image_b_clock_frequency_10003cf0(14u);
    uint32_t divider = (frequency / requested) & ~1u;
    uint32_t product = divider * requested;
    device[0] = (uint32_t)(uintptr_t)record;
    uint32_t mode = (((uint32_t)record[0x10u] << 22) &
                     UINT32_C(0x00c00000)) |
                    (((uint32_t)*(uint16_t *)(void *)(record + 0x0au) << 8)
                     & UINT32_C(0x00000300)) |
                    UINT32_C(0x80000000);
    device[1] = mode;
    if (frequency != product)
        divider += 2u;
    device[2] = divider;
    device[3] = 2u;
    *(uint32_t *)(void *)(record + 0x0cu) = (uint32_t)(uintptr_t)device;
    return 0;
}
