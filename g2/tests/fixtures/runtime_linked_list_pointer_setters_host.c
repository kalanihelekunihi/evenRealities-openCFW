/*
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * Host adapter for the source-owned G2 LVGL linked-list pointer setters.
 */

unsigned char open_cfw_test_runtime_linked_list_setter_storage[1024];
unsigned int open_cfw_test_runtime_linked_list_setter_resolutions;

static unsigned char *
open_cfw_test_runtime_linked_list_setter_resolve(unsigned int value)
{
    open_cfw_test_runtime_linked_list_setter_resolutions += 1U;
    return open_cfw_test_runtime_linked_list_setter_storage + value;
}

#define OPEN_CFW_RUNTIME_LINKED_LIST_SETTER_POINTER_TO_BYTES(value) \
    open_cfw_test_runtime_linked_list_setter_resolve(value)

#include "../../components/apollo_main/core_overlay/runtime_linked_list_pointer_setters.c"

void open_cfw_test_runtime_linked_list_setter_reset(void)
{
    unsigned int index;

    open_cfw_test_runtime_linked_list_setter_resolutions = 0U;
    for (index = 0U; index < 1024U; index += 1U) {
        open_cfw_test_runtime_linked_list_setter_storage[index] = 0xa5U;
    }
}
