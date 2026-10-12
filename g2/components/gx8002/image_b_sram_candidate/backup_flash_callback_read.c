/* Native image-B 0x100079e8..0x10007bc8 flash callback read path.
 * Volatile register order follows the two-phase controller transaction:
 * command/address prefix, then up to 32 received bytes. No timeout was
 * present in the original. Device and SRAM alias validation remain open. */
#include <stdint.h>

extern volatile uint32_t gx8002_image_b_flash_descriptor_20016d60[8];
extern uint32_t gx8002_image_b_flash_read_10006c30(
    uint32_t, uint8_t *, uint32_t);

static volatile uint32_t *const flash =
    (volatile uint32_t *)(uintptr_t)UINT32_C(0xa2000000);
static volatile uint32_t *const clock_gate =
    (volatile uint32_t *)(uintptr_t)UINT32_C(0xa0300090);
static volatile uint32_t *const flash_aux =
    (volatile uint32_t *)(uintptr_t)UINT32_C(0xa2800074);

static void wait_status_ready(void)
{
    uint8_t status;
    do {
        (void)gx8002_image_b_flash_read_10006c30(5u, &status, 1u);
    } while ((status & 1u) != 0u);
}

static void set_read_address(uint32_t address)
{
    volatile uint8_t *descriptor =
        (volatile uint8_t *)(void *)gx8002_image_b_flash_descriptor_20016d60;
    uint32_t shift = (gx8002_image_b_flash_descriptor_20016d60[2] +
                      UINT32_C(0x1fffffff)) << 3;
    descriptor[0x10u] = 72u;
    descriptor[0x11u] = (uint8_t)(address >> (shift & 31u));
    descriptor[0x12u] = (uint8_t)(address >> ((shift - 8u) & 31u));
    descriptor[0x13u] = (uint8_t)(address >> ((shift - 16u) & 31u));
    descriptor[0x14u] = (uint8_t)(address >> ((shift - 24u) & 31u));
}

uint32_t gx8002_image_b_flash_callback_100079e8(
    uint32_t offset, uint8_t *destination, uint32_t length)
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

    wait_status_ready();
    set_read_address(address);
    uint32_t transferred = 0u;
    while (transferred < length) {
        uint32_t remaining = length - transferred;
        uint32_t chunk = remaining < 32u ? remaining : 32u;
        uint32_t prefix = gx8002_image_b_flash_descriptor_20016d60[2] + 2u;
        volatile uint8_t *prefix_bytes =
            (volatile uint8_t *)(void *)gx8002_image_b_flash_descriptor_20016d60
            + 0x10u;

        while ((flash[0x28u / 4u] & 1u) != 0u) { }
        flash[0x08u / 4u] = 0u;
        *clock_gate = 2u;
        flash[0x4cu / 4u] = 0u;
        flash[0x10u / 4u] = 0u;
        flash[0] = 0x407u;
        flash[0x04u / 4u] = prefix - 1u;
        flash[0x18u / 4u] = 0u;
        *flash_aux = 0u;
        flash[0x08u / 4u] = 1u;
        for (uint32_t i = 0u; i < prefix; ++i) {
            while ((flash[0x28u / 4u] & 2u) == 0u) { }
            flash[0x60u / 4u] = prefix_bytes[i];
        }
        flash[0x10u / 4u] = 1u;
        while (flash[0x20u / 4u] != 0u) { }
        while ((flash[0x28u / 4u] & 1u) != 0u) { }

        flash[0x08u / 4u] = 0u;
        flash[0x10u / 4u] = 0u;
        flash[0] = 0x807u;
        flash[0x04u / 4u] = chunk - 1u;
        flash[0x18u / 4u] = 0u;
        flash[0x54u / 4u] = 7u;
        flash[0x4cu / 4u] = 1u;
        flash[0x08u / 4u] = 1u;
        flash[0x10u / 4u] = 1u;
        flash[0x60u / 4u] = 0u;
        for (uint32_t i = 0u; i < chunk; ++i) {
            while ((flash[0x28u / 4u] & 8u) == 0u) { }
            destination[transferred + i] = (uint8_t)flash[0x60u / 4u];
        }
        while (flash[0x24u / 4u] != 0u) { }
        while ((flash[0x28u / 4u] & 1u) != 0u) { }
        flash[0x08u / 4u] = 0u;
        flash[0x4cu / 4u] = 0u;
        *clock_gate = 3u;
        *clock_gate = 1u;
        flash[0x08u / 4u] = 1u;

        transferred += chunk;
        address += chunk;
        set_read_address(address);
    }
    wait_status_ready();
    return transferred;
}
