#include <stdint.h>

static volatile uint32_t open_cfw_bootloader_range_error_fixture_word;
static volatile uint32_t open_cfw_bootloader_range_error_fixture_guard;

#define OPEN_CFW_BOOTLOADER_RANGE_ERROR_4275D2_TARGET \
    (&open_cfw_bootloader_range_error_fixture_word)
#include "../../components/bootloader/core_overlay/runtime_double_range_error_4275d2.c"

uint32_t open_cfw_bootloader_double_range_error_4275d2_fixture(void)
{
    open_cfw_bootloader_range_error_fixture_word = UINT32_C(0xA5A5A5A5);
    open_cfw_bootloader_range_error_fixture_guard = UINT32_C(0x5A5A5A5A);
    open_cfw_bootloader_double_range_error_4275d2();
    if (open_cfw_bootloader_range_error_fixture_guard != UINT32_C(0x5A5A5A5A)) {
        return UINT32_C(0xDEADBEEF);
    }
    return open_cfw_bootloader_range_error_fixture_word;
}
