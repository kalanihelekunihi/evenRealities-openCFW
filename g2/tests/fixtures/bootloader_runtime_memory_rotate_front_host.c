#include <stddef.h>
#include <string.h>

void *open_cfw_mrf_host_memcpy(void *destination, const void *source, size_t size)
{
    return memcpy(destination, source, size);
}

void *open_cfw_mrf_host_memmove(void *destination, const void *source, size_t size)
{
    return memmove(destination, source, size);
}

#include "../../components/bootloader/core_overlay/runtime_memory_rotate_front_423928.c"
