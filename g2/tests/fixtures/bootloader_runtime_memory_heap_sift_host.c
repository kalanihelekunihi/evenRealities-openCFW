#include <stddef.h>

void open_cfw_mhs_host_swap(void *left_pointer, void *right_pointer, size_t size)
{
    unsigned char *left = left_pointer;
    unsigned char *right = right_pointer;
    while (size-- != 0U) {
        unsigned char value = *left;
        *left++ = *right;
        *right++ = value;
    }
}

#include "../../components/bootloader/core_overlay/runtime_memory_heap_sift_4239c2.c"
