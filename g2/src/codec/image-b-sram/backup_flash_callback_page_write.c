/* Native image-B 0x10007884..0x100079e0: bounded flash page writer.
 * The existing 0x10007790 command-frame provider owns controller MMIO.
 * This body keeps the 256-byte boundary and post-frame status reads. */
#include <stdint.h>

extern volatile uint32_t gx8002_image_b_flash_descriptor_20016d60[8];
extern uint32_t gx8002_image_b_flash_read_10006c30(
    uint32_t, uint8_t *, uint32_t);
extern uint32_t gx8002_image_b_flash_write_10006cb0(
    uint32_t, const uint8_t *, uint32_t);
extern void gx8002_image_b_flash_command_frame_10007790(
    uint32_t, const uint8_t *, uint32_t);

static void wait_ready(void)
{
    uint8_t status;
    do {
        (void)gx8002_image_b_flash_read_10006c30(5u, &status, 1u);
    } while ((status & 1u) != 0u);
}

static void prepare_address(uint32_t address)
{
    volatile uint8_t *descriptor =
        (volatile uint8_t *)(void *)gx8002_image_b_flash_descriptor_20016d60;
    uint32_t shift = (gx8002_image_b_flash_descriptor_20016d60[2] +
                      UINT32_C(0x1fffffff)) << 3;
    descriptor[0x10u] = 66u;
    descriptor[0x11u] = (uint8_t)(address >> (shift & 31u));
    descriptor[0x12u] = (uint8_t)(address >> ((shift - 8u) & 31u));
    descriptor[0x13u] = (uint8_t)(address >> ((shift - 16u) & 31u));
    descriptor[0x14u] = (uint8_t)(address >> ((shift - 24u) & 31u));
}

uint32_t gx8002_image_b_flash_callback_10007884(
    uint32_t offset, const uint8_t *source, uint32_t length)
{
    volatile uint8_t *profile = (volatile uint8_t *)(uintptr_t)
        gx8002_image_b_flash_descriptor_20016d60[3];
    volatile uint32_t *configuration = (volatile uint32_t *)(uintptr_t)
        *(volatile uint32_t *)(void *)(profile + 0x14u);
    uint32_t index = configuration[4] & 7u;
    if (length == 0u || offset + length > configuration[2])
        return UINT32_MAX;
    uint32_t address = configuration[0] + offset + index * configuration[1];
    uint32_t id = (uint32_t)profile[6] | ((uint32_t)profile[7] << 8);
    if (id != 94u && id != 133u) return UINT32_MAX;

    uint32_t transferred = 0u;
    while (transferred < length) {
        uint32_t current = address + transferred;
        uint32_t page_available = 256u - (current & 255u);
        uint32_t remaining = length - transferred;
        uint32_t chunk = remaining < page_available ? remaining : page_available;
        wait_ready();
        (void)gx8002_image_b_flash_write_10006cb0(6u, (const uint8_t *)0, 0u);
        prepare_address(current);
        gx8002_image_b_flash_command_frame_10007790(
            gx8002_image_b_flash_descriptor_20016d60[2] + 1u,
            source + transferred, chunk);
        transferred += chunk;
    }
    wait_ready();
    return transferred;
}
