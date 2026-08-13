/*
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * Host substitutions for the source-owned G2 linked-list insertion cluster.
 */

static unsigned int open_cfw_test_runtime_linked_list_insert_allocate(
    unsigned int size
);
static unsigned int open_cfw_test_runtime_linked_list_insert_get_head(
    const void *list
);
static unsigned int open_cfw_test_runtime_linked_list_insert_get_previous(
    const void *list,
    unsigned int node
);
static void open_cfw_test_runtime_linked_list_insert_set_previous(
    const void *list,
    unsigned int node,
    unsigned int previous
);
static void open_cfw_test_runtime_linked_list_insert_set_next(
    const void *list,
    unsigned int node,
    unsigned int next
);
static unsigned int open_cfw_test_runtime_linked_list_insert_head_call(
    void *list
);

#define OPEN_CFW_RUNTIME_LINKED_LIST_INSERT_ALLOCATE(size) \
    open_cfw_test_runtime_linked_list_insert_allocate((size))
#define OPEN_CFW_RUNTIME_LINKED_LIST_INSERT_GET_HEAD(list) \
    open_cfw_test_runtime_linked_list_insert_get_head((list))
#define OPEN_CFW_RUNTIME_LINKED_LIST_INSERT_GET_PREVIOUS(list, node) \
    open_cfw_test_runtime_linked_list_insert_get_previous((list), (node))
#define OPEN_CFW_RUNTIME_LINKED_LIST_INSERT_SET_PREVIOUS( \
    list, node, previous \
) \
    open_cfw_test_runtime_linked_list_insert_set_previous( \
        (list), (node), (previous) \
    )
#define OPEN_CFW_RUNTIME_LINKED_LIST_INSERT_SET_NEXT(list, node, next) \
    open_cfw_test_runtime_linked_list_insert_set_next( \
        (list), (node), (next) \
    )
#define OPEN_CFW_RUNTIME_LINKED_LIST_INSERT_HEAD(list) \
    open_cfw_test_runtime_linked_list_insert_head_call((list))

#include "../../components/apollo_main/core_overlay/runtime_linked_list_insertions.c"

enum {
    OPEN_CFW_TEST_RUNTIME_LINKED_LIST_INSERT_STORAGE_SIZE = 4096U,
    OPEN_CFW_TEST_RUNTIME_LINKED_LIST_INSERT_EVENT_CAPACITY = 32U,
    OPEN_CFW_TEST_RUNTIME_LINKED_LIST_INSERT_EVENT_ALLOCATE = 1U,
    OPEN_CFW_TEST_RUNTIME_LINKED_LIST_INSERT_EVENT_GET_HEAD = 2U,
    OPEN_CFW_TEST_RUNTIME_LINKED_LIST_INSERT_EVENT_GET_PREVIOUS = 3U,
    OPEN_CFW_TEST_RUNTIME_LINKED_LIST_INSERT_EVENT_SET_PREVIOUS = 4U,
    OPEN_CFW_TEST_RUNTIME_LINKED_LIST_INSERT_EVENT_SET_NEXT = 5U,
    OPEN_CFW_TEST_RUNTIME_LINKED_LIST_INSERT_EVENT_INSERT_HEAD = 6U
};

unsigned char open_cfw_test_runtime_linked_list_insert_storage[
    OPEN_CFW_TEST_RUNTIME_LINKED_LIST_INSERT_STORAGE_SIZE
];
struct open_cfw_runtime_linked_list_insert_descriptor
    open_cfw_test_runtime_linked_list_insert_descriptor;

unsigned int open_cfw_test_runtime_linked_list_insert_allocation_result;
unsigned int open_cfw_test_runtime_linked_list_insert_allocation_calls;
unsigned int open_cfw_test_runtime_linked_list_insert_allocation_size;
unsigned int open_cfw_test_runtime_linked_list_insert_event_count;
unsigned int open_cfw_test_runtime_linked_list_insert_event_kind[
    OPEN_CFW_TEST_RUNTIME_LINKED_LIST_INSERT_EVENT_CAPACITY
];
unsigned int open_cfw_test_runtime_linked_list_insert_event_node[
    OPEN_CFW_TEST_RUNTIME_LINKED_LIST_INSERT_EVENT_CAPACITY
];
unsigned int open_cfw_test_runtime_linked_list_insert_event_link[
    OPEN_CFW_TEST_RUNTIME_LINKED_LIST_INSERT_EVENT_CAPACITY
];
unsigned int open_cfw_test_runtime_linked_list_insert_event_head[
    OPEN_CFW_TEST_RUNTIME_LINKED_LIST_INSERT_EVENT_CAPACITY
];
unsigned int open_cfw_test_runtime_linked_list_insert_event_tail[
    OPEN_CFW_TEST_RUNTIME_LINKED_LIST_INSERT_EVENT_CAPACITY
];

static void open_cfw_test_runtime_linked_list_insert_record(
    unsigned int kind,
    unsigned int node,
    unsigned int link
)
{
    unsigned int index =
        open_cfw_test_runtime_linked_list_insert_event_count;

    if (
        index
        < OPEN_CFW_TEST_RUNTIME_LINKED_LIST_INSERT_EVENT_CAPACITY
    ) {
        open_cfw_test_runtime_linked_list_insert_event_kind[index] = kind;
        open_cfw_test_runtime_linked_list_insert_event_node[index] = node;
        open_cfw_test_runtime_linked_list_insert_event_link[index] = link;
        open_cfw_test_runtime_linked_list_insert_event_head[index] =
            open_cfw_test_runtime_linked_list_insert_descriptor.head;
        open_cfw_test_runtime_linked_list_insert_event_tail[index] =
            open_cfw_test_runtime_linked_list_insert_descriptor.tail;
    }
    open_cfw_test_runtime_linked_list_insert_event_count = index + 1U;
}

static unsigned int open_cfw_test_runtime_linked_list_insert_load_word(
    unsigned int offset
)
{
    return (
        (unsigned int)
            open_cfw_test_runtime_linked_list_insert_storage[offset]
        | (
            (unsigned int)
                open_cfw_test_runtime_linked_list_insert_storage[
                    offset + 1U
                ]
            << 8U
        )
        | (
            (unsigned int)
                open_cfw_test_runtime_linked_list_insert_storage[
                    offset + 2U
                ]
            << 16U
        )
        | (
            (unsigned int)
                open_cfw_test_runtime_linked_list_insert_storage[
                    offset + 3U
                ]
            << 24U
        )
    );
}

static void open_cfw_test_runtime_linked_list_insert_store_word(
    unsigned int offset,
    unsigned int value
)
{
    open_cfw_test_runtime_linked_list_insert_storage[offset] =
        (unsigned char)value;
    open_cfw_test_runtime_linked_list_insert_storage[offset + 1U] =
        (unsigned char)(value >> 8U);
    open_cfw_test_runtime_linked_list_insert_storage[offset + 2U] =
        (unsigned char)(value >> 16U);
    open_cfw_test_runtime_linked_list_insert_storage[offset + 3U] =
        (unsigned char)(value >> 24U);
}

static unsigned int open_cfw_test_runtime_linked_list_insert_allocate(
    unsigned int size
)
{
    open_cfw_test_runtime_linked_list_insert_allocation_calls += 1U;
    open_cfw_test_runtime_linked_list_insert_allocation_size = size;
    open_cfw_test_runtime_linked_list_insert_record(
        OPEN_CFW_TEST_RUNTIME_LINKED_LIST_INSERT_EVENT_ALLOCATE,
        size,
        open_cfw_test_runtime_linked_list_insert_allocation_result
    );
    return open_cfw_test_runtime_linked_list_insert_allocation_result;
}

static unsigned int open_cfw_test_runtime_linked_list_insert_get_head(
    const void *list_pointer
)
{
    const struct open_cfw_runtime_linked_list_insert_descriptor *list =
        (const struct open_cfw_runtime_linked_list_insert_descriptor *)
            list_pointer;

    open_cfw_test_runtime_linked_list_insert_record(
        OPEN_CFW_TEST_RUNTIME_LINKED_LIST_INSERT_EVENT_GET_HEAD,
        0U,
        list->head
    );
    return list->head;
}

static unsigned int open_cfw_test_runtime_linked_list_insert_get_previous(
    const void *list_pointer,
    unsigned int node
)
{
    const struct open_cfw_runtime_linked_list_insert_descriptor *list =
        (const struct open_cfw_runtime_linked_list_insert_descriptor *)
            list_pointer;
    unsigned int previous =
        open_cfw_test_runtime_linked_list_insert_load_word(
            node + list->node_size
        );

    open_cfw_test_runtime_linked_list_insert_record(
        OPEN_CFW_TEST_RUNTIME_LINKED_LIST_INSERT_EVENT_GET_PREVIOUS,
        node,
        previous
    );
    return previous;
}

static void open_cfw_test_runtime_linked_list_insert_set_previous(
    const void *list_pointer,
    unsigned int node,
    unsigned int previous
)
{
    const struct open_cfw_runtime_linked_list_insert_descriptor *list =
        (const struct open_cfw_runtime_linked_list_insert_descriptor *)
            list_pointer;

    open_cfw_test_runtime_linked_list_insert_record(
        OPEN_CFW_TEST_RUNTIME_LINKED_LIST_INSERT_EVENT_SET_PREVIOUS,
        node,
        previous
    );
    if (node != 0U) {
        open_cfw_test_runtime_linked_list_insert_store_word(
            node + list->node_size,
            previous
        );
    }
}

static void open_cfw_test_runtime_linked_list_insert_set_next(
    const void *list_pointer,
    unsigned int node,
    unsigned int next
)
{
    const struct open_cfw_runtime_linked_list_insert_descriptor *list =
        (const struct open_cfw_runtime_linked_list_insert_descriptor *)
            list_pointer;

    open_cfw_test_runtime_linked_list_insert_record(
        OPEN_CFW_TEST_RUNTIME_LINKED_LIST_INSERT_EVENT_SET_NEXT,
        node,
        next
    );
    if (node != 0U) {
        open_cfw_test_runtime_linked_list_insert_store_word(
            node + list->node_size + 4U,
            next
        );
    }
}

static unsigned int open_cfw_test_runtime_linked_list_insert_head_call(
    void *list_pointer
)
{
    open_cfw_test_runtime_linked_list_insert_record(
        OPEN_CFW_TEST_RUNTIME_LINKED_LIST_INSERT_EVENT_INSERT_HEAD,
        0U,
        0U
    );
    return open_cfw_runtime_linked_list_insert_head(
        (struct open_cfw_runtime_linked_list_insert_descriptor *)
            list_pointer
    );
}

void open_cfw_test_runtime_linked_list_insert_reset(
    unsigned int node_size,
    unsigned int head,
    unsigned int tail,
    unsigned int allocation_result
)
{
    unsigned int index;

    for (
        index = 0U;
        index < OPEN_CFW_TEST_RUNTIME_LINKED_LIST_INSERT_STORAGE_SIZE;
        index += 1U
    ) {
        open_cfw_test_runtime_linked_list_insert_storage[index] = 0xCCU;
    }
    open_cfw_test_runtime_linked_list_insert_descriptor.node_size =
        node_size;
    open_cfw_test_runtime_linked_list_insert_descriptor.head = head;
    open_cfw_test_runtime_linked_list_insert_descriptor.tail = tail;
    open_cfw_test_runtime_linked_list_insert_allocation_result =
        allocation_result;
    open_cfw_test_runtime_linked_list_insert_allocation_calls = 0U;
    open_cfw_test_runtime_linked_list_insert_allocation_size = 0U;
    open_cfw_test_runtime_linked_list_insert_event_count = 0U;
    for (
        index = 0U;
        index < OPEN_CFW_TEST_RUNTIME_LINKED_LIST_INSERT_EVENT_CAPACITY;
        index += 1U
    ) {
        open_cfw_test_runtime_linked_list_insert_event_kind[index] = 0U;
        open_cfw_test_runtime_linked_list_insert_event_node[index] = 0U;
        open_cfw_test_runtime_linked_list_insert_event_link[index] = 0U;
        open_cfw_test_runtime_linked_list_insert_event_head[index] = 0U;
        open_cfw_test_runtime_linked_list_insert_event_tail[index] = 0U;
    }
}

void open_cfw_test_runtime_linked_list_insert_set_links(
    unsigned int node,
    unsigned int previous,
    unsigned int next
)
{
    unsigned int node_size =
        open_cfw_test_runtime_linked_list_insert_descriptor.node_size;

    open_cfw_test_runtime_linked_list_insert_store_word(
        node + node_size,
        previous
    );
    open_cfw_test_runtime_linked_list_insert_store_word(
        node + node_size + 4U,
        next
    );
}

unsigned int open_cfw_test_runtime_linked_list_insert_previous(
    unsigned int node
)
{
    return open_cfw_test_runtime_linked_list_insert_load_word(
        node
        + open_cfw_test_runtime_linked_list_insert_descriptor.node_size
    );
}

unsigned int open_cfw_test_runtime_linked_list_insert_next(
    unsigned int node
)
{
    return open_cfw_test_runtime_linked_list_insert_load_word(
        node
        + open_cfw_test_runtime_linked_list_insert_descriptor.node_size
        + 4U
    );
}

unsigned int open_cfw_test_runtime_linked_list_insert_execute_head(void)
{
    return open_cfw_runtime_linked_list_insert_head(
        &open_cfw_test_runtime_linked_list_insert_descriptor
    );
}

unsigned int open_cfw_test_runtime_linked_list_insert_execute_before(
    unsigned int active
)
{
    return open_cfw_runtime_linked_list_insert_before(
        &open_cfw_test_runtime_linked_list_insert_descriptor,
        active
    );
}

unsigned int open_cfw_test_runtime_linked_list_insert_execute_tail(void)
{
    return open_cfw_runtime_linked_list_insert_tail(
        &open_cfw_test_runtime_linked_list_insert_descriptor
    );
}

unsigned int
open_cfw_test_runtime_linked_list_insert_execute_before_null_list(
    unsigned int active
)
{
    return open_cfw_runtime_linked_list_insert_before(
        (struct open_cfw_runtime_linked_list_insert_descriptor *)0,
        active
    );
}

#ifdef OPEN_CFW_TEST_RUNTIME_LINKED_LIST_INSERT_NULL_PROBE
int main(int argument_count, char **arguments)
{
    if (argument_count < 2) {
        return 2;
    }
    if (arguments[1][0] == 'h') {
        (void)open_cfw_runtime_linked_list_insert_head(
            (struct open_cfw_runtime_linked_list_insert_descriptor *)0
        );
    }
    else {
        (void)open_cfw_runtime_linked_list_insert_tail(
            (struct open_cfw_runtime_linked_list_insert_descriptor *)0
        );
    }
    return 0;
}
#endif
