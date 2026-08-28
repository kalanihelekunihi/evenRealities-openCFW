/*
 * SPDX-License-Identifier: MIT
 *
 * Host trace adapter for the source-owned linked-list custom-clear routine.
 */

enum {
    OPEN_CFW_TEST_CLEAR_CUSTOM_EVENT_HEAD = 1,
    OPEN_CFW_TEST_CLEAR_CUSTOM_EVENT_NEXT = 2,
    OPEN_CFW_TEST_CLEAR_CUSTOM_EVENT_CALLBACK = 3,
    OPEN_CFW_TEST_CLEAR_CUSTOM_EVENT_REMOVE = 4,
    OPEN_CFW_TEST_CLEAR_CUSTOM_EVENT_FREE = 5
};

unsigned char open_cfw_test_clear_custom_storage[1024];
unsigned int open_cfw_test_clear_custom_event_codes[64];
unsigned int open_cfw_test_clear_custom_event_nodes[64];
unsigned int open_cfw_test_clear_custom_event_count;
unsigned int open_cfw_test_clear_custom_callback_handle;
unsigned int open_cfw_test_clear_custom_callback_mutates_next;

static unsigned int open_cfw_test_clear_custom_node_size;

static void open_cfw_test_clear_custom_record(
    unsigned int code,
    unsigned int node
)
{
    unsigned int index = open_cfw_test_clear_custom_event_count;

    if (index < 64U) {
        open_cfw_test_clear_custom_event_codes[index] = code;
        open_cfw_test_clear_custom_event_nodes[index] = node;
    }
    open_cfw_test_clear_custom_event_count = index + 1U;
}

static unsigned int open_cfw_test_clear_custom_load_word(
    unsigned int offset
)
{
    unsigned int value;
    unsigned int byte;

    value = 0U;
    for (byte = 0U; byte < 4U; byte += 1U) {
        value |=
            (unsigned int)open_cfw_test_clear_custom_storage[
                offset + byte
            ] << (byte * 8U);
    }
    return value;
}

static void open_cfw_test_clear_custom_store_word(
    unsigned int offset,
    unsigned int value
)
{
    unsigned int byte;

    for (byte = 0U; byte < 4U; byte += 1U) {
        open_cfw_test_clear_custom_storage[offset + byte] =
            (unsigned char)(value >> (byte * 8U));
    }
}

static unsigned int open_cfw_test_clear_custom_get_head(
    const void *list
)
{
    const unsigned int *words = (const unsigned int *)list;

    open_cfw_test_clear_custom_record(
        OPEN_CFW_TEST_CLEAR_CUSTOM_EVENT_HEAD,
        0U
    );
    if (list == (const void *)0) {
        return 0U;
    }
    open_cfw_test_clear_custom_node_size = words[0];
    return words[1];
}

static unsigned int open_cfw_test_clear_custom_get_next(
    const void *list,
    unsigned int node
)
{
    const unsigned int *words = (const unsigned int *)list;

    open_cfw_test_clear_custom_record(
        OPEN_CFW_TEST_CLEAR_CUSTOM_EVENT_NEXT,
        node
    );
    return open_cfw_test_clear_custom_load_word(
        node + words[0] + 4U
    );
}

static void open_cfw_test_clear_custom_remove(
    void *list,
    unsigned int node
)
{
    (void)list;
    open_cfw_test_clear_custom_record(
        OPEN_CFW_TEST_CLEAR_CUSTOM_EVENT_REMOVE,
        node
    );
}

static void open_cfw_test_clear_custom_free(unsigned int node)
{
    open_cfw_test_clear_custom_record(
        OPEN_CFW_TEST_CLEAR_CUSTOM_EVENT_FREE,
        node
    );
}

static void open_cfw_test_clear_custom_call_cleanup(
    unsigned int cleanup,
    unsigned int node
)
{
    open_cfw_test_clear_custom_callback_handle = cleanup;
    open_cfw_test_clear_custom_record(
        OPEN_CFW_TEST_CLEAR_CUSTOM_EVENT_CALLBACK,
        node
    );
    if (open_cfw_test_clear_custom_callback_mutates_next != 0U) {
        open_cfw_test_clear_custom_store_word(
            node + open_cfw_test_clear_custom_node_size + 4U,
            0U
        );
    }
}

#define OPEN_CFW_RUNTIME_LINKED_LIST_CLEAR_CUSTOM_GET_HEAD(list) \
    open_cfw_test_clear_custom_get_head((const void *)(list))
#define OPEN_CFW_RUNTIME_LINKED_LIST_CLEAR_CUSTOM_GET_NEXT(list, node) \
    open_cfw_test_clear_custom_get_next((const void *)(list), (node))
#define OPEN_CFW_RUNTIME_LINKED_LIST_CLEAR_CUSTOM_REMOVE(list, node) \
    open_cfw_test_clear_custom_remove((void *)(list), (node))
#define OPEN_CFW_RUNTIME_LINKED_LIST_CLEAR_CUSTOM_FREE(node) \
    open_cfw_test_clear_custom_free((node))
#define OPEN_CFW_RUNTIME_LINKED_LIST_CLEAR_CUSTOM_CALL_CLEANUP( \
    cleanup, \
    node \
) \
    open_cfw_test_clear_custom_call_cleanup((cleanup), (node))

#include "../../components/apollo_main/core_overlay/runtime_linked_list_clear_custom.c"

void open_cfw_test_clear_custom_reset(void)
{
    unsigned int index;

    open_cfw_test_clear_custom_event_count = 0U;
    open_cfw_test_clear_custom_callback_handle = 0U;
    open_cfw_test_clear_custom_callback_mutates_next = 0U;
    open_cfw_test_clear_custom_node_size = 0U;
    for (index = 0U; index < 64U; index += 1U) {
        open_cfw_test_clear_custom_event_codes[index] = 0U;
        open_cfw_test_clear_custom_event_nodes[index] = 0U;
    }
    for (index = 0U; index < 1024U; index += 1U) {
        open_cfw_test_clear_custom_storage[index] = 0xa5U;
    }
}
