#include "../../components/bootloader/core_overlay/runtime_crc32.c"

uint32_t open_cfw_bootloader_crc32_fixture(
    uint32_t crc,
    const uint8_t *data,
    uint32_t size
)
{
    return open_cfw_bootloader_crc32(crc, data, size);
}
