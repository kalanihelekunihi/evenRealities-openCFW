/*
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * Host adapter for the source-owned G2 LVGL linked-list accessor cluster.
 */

unsigned char open_cfw_test_runtime_linked_list_storage[1024];
unsigned int open_cfw_test_runtime_linked_list_pointer_resolutions;
unsigned int open_cfw_test_runtime_linked_list_clear_calls;
void *open_cfw_test_runtime_linked_list_clear_list;
unsigned int open_cfw_test_runtime_linked_list_clear_cleanup;

static const unsigned char *
open_cfw_test_runtime_linked_list_resolve_pointer(unsigned int value)
{
    open_cfw_test_runtime_linked_list_pointer_resolutions += 1U;
    return open_cfw_test_runtime_linked_list_storage + value;
}

static void open_cfw_test_runtime_linked_list_clear_custom(
    void *list,
    unsigned int cleanup
)
{
    open_cfw_test_runtime_linked_list_clear_calls += 1U;
    open_cfw_test_runtime_linked_list_clear_list = list;
    open_cfw_test_runtime_linked_list_clear_cleanup = cleanup;
}

#define OPEN_CFW_RUNTIME_LINKED_LIST_POINTER_TO_BYTES(value) \
    open_cfw_test_runtime_linked_list_resolve_pointer(value)
#define OPEN_CFW_RUNTIME_LINKED_LIST_CLEAR_CUSTOM(list, cleanup) \
    open_cfw_test_runtime_linked_list_clear_custom( \
        (void *)(list), \
        (unsigned int)(__UINTPTR_TYPE__)(cleanup) \
    )

#include "../../components/apollo_main/core_overlay/runtime_linked_list_accessors.c"

void open_cfw_test_runtime_linked_list_reset(void)
{
    unsigned int index;

    open_cfw_test_runtime_linked_list_pointer_resolutions = 0U;
    open_cfw_test_runtime_linked_list_clear_calls = 0U;
    open_cfw_test_runtime_linked_list_clear_list = (void *)0;
    open_cfw_test_runtime_linked_list_clear_cleanup = 0xffffffffU;
    for (index = 0U; index < 1024U; index += 1U) {
        open_cfw_test_runtime_linked_list_storage[index] = 0xa5U;
    }
}
