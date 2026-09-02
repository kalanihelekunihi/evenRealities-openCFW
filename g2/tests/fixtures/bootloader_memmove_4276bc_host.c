#include <stddef.h>
#include <stdint.h>

#include "../../components/bootloader/core_overlay/runtime_memmove_4276bc.c"

void *open_cfw_test_memmove_4276bc(void *destination, const void *source,
                                    size_t byte_count)
{
    return open_cfw_bootloader_memmove_4276bc(destination, source, byte_count);
}
