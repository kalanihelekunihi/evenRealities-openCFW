/* Native image-B callback 0x10006e64..0x10006eb0. The product callback
 * table stores this entry as its second operation. Status polling and the
 * 64 KiB transaction boundary follow the original instructions; the live
 * flash descriptor remains initialized product data at 0x20016d60. */
#include <stdint.h>

extern uint32_t gx8002_image_b_flash_read_10006c30(
    uint32_t command, uint8_t *destination, uint32_t length);
extern volatile uint32_t gx8002_image_b_flash_descriptor_20016d60[];

typedef uint32_t (*image_b_flash_writer)(uint32_t, const uint8_t *, uint32_t);

uint32_t gx8002_image_b_flash_chunked_write_10006e64(
    uint32_t address, const uint8_t *source, uint32_t length)
{
    uint8_t status;
    do {
        (void)gx8002_image_b_flash_read_10006c30(5u, &status, 1u);
    } while ((status & 1u) != 0u);

    while (length != 0u) {
        uint32_t chunk = length < UINT32_C(0x10000) ? length : UINT32_C(0x10000);
        image_b_flash_writer write = (image_b_flash_writer)(uintptr_t)
            gx8002_image_b_flash_descriptor_20016d60[7];
        (void)write(address, source, chunk);
        address += chunk;
        source += chunk;
        length -= chunk;
    }
    return 0u;
}
