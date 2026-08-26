#include <stdint.h>

static volatile uint32_t open_cfw_bootloader_store_fixture_word;

#define OPEN_CFW_BOOTLOADER_STORE_200270CC_TARGET \
    (&open_cfw_bootloader_store_fixture_word)
#include "../../components/bootloader/core_overlay/runtime_store_200270cc.c"

uint32_t open_cfw_bootloader_store_200270cc_fixture(uint32_t value)
{
    open_cfw_bootloader_store_fixture_word = UINT32_C(0xA5A5A5A5);
    open_cfw_bootloader_store_200270cc(value);
    return open_cfw_bootloader_store_fixture_word;
}
