/* SPDX-License-Identifier: MIT */

#include <assert.h>
#include <stddef.h>
#include <stdint.h>

void *open_cfw_bootloader_memset_wrapper_426c10(
    void *destination,
    int value,
    size_t count
);

static void *observed_destination;
static size_t observed_count;
static int observed_value;

void open_cfw_bootloader_retained_memset_41560c(
    void *destination,
    size_t count,
    int value
)
{
    unsigned char *output = destination;
    observed_destination = destination;
    observed_count = count;
    observed_value = value;
    while (count != 0U) {
        *output++ = (unsigned char)value;
        --count;
    }
}

int main(void)
{
    unsigned char bytes[7] = {0x11U, 0x22U, 0x33U, 0x44U, 0x55U, 0x66U, 0x77U};
    void *returned = open_cfw_bootloader_memset_wrapper_426c10(bytes + 1, 0x1A5, 4U);

    assert(returned == bytes + 1);
    assert(observed_destination == bytes + 1);
    assert(observed_count == 4U);
    assert(observed_value == 0x1A5);
    assert(bytes[0] == 0x11U && bytes[5] == 0x66U && bytes[6] == 0x77U);
    for (size_t index = 1U; index != 5U; ++index) {
        assert(bytes[index] == 0xA5U);
    }

    returned = open_cfw_bootloader_memset_wrapper_426c10(bytes, 0, 0U);
    assert(returned == bytes);
    assert(observed_count == 0U);
    return 0;
}
