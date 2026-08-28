/*
 * SPDX-License-Identifier: MIT
 *
 * Host substitutions for the source-owned G2 linked-list removal routine.
 */

#include <setjmp.h>

static unsigned int open_cfw_test_runtime_linked_list_remove_get_head(
    const void *list
);
static unsigned int open_cfw_test_runtime_linked_list_remove_get_tail(
    const void *list
);
static unsigned int open_cfw_test_runtime_linked_list_remove_get_next(
    const void *list,
    unsigned int node
);
static unsigned int open_cfw_test_runtime_linked_list_remove_get_previous(
    const void *list,
    unsigned int node
);
static void open_cfw_test_runtime_linked_list_remove_set_previous(
    void *list,
    unsigned int node,
    unsigned int previous
);
static void open_cfw_test_runtime_linked_list_remove_set_next(
    void *list,
    unsigned int node,
    unsigned int next
);

#define OPEN_CFW_RUNTIME_LINKED_LIST_REMOVE_GET_HEAD(list) \
    open_cfw_test_runtime_linked_list_remove_get_head((list))
#define OPEN_CFW_RUNTIME_LINKED_LIST_REMOVE_GET_TAIL(list) \
    open_cfw_test_runtime_linked_list_remove_get_tail((list))
#define OPEN_CFW_RUNTIME_LINKED_LIST_REMOVE_GET_NEXT(list, node) \
    open_cfw_test_runtime_linked_list_remove_get_next((list), (node))
#define OPEN_CFW_RUNTIME_LINKED_LIST_REMOVE_GET_PREVIOUS(list, node) \
    open_cfw_test_runtime_linked_list_remove_get_previous((list), (node))
#define OPEN_CFW_RUNTIME_LINKED_LIST_REMOVE_SET_PREVIOUS( \
    list, node, previous \
) \
    open_cfw_test_runtime_linked_list_remove_set_previous( \
        (list), (node), (previous) \
    )
#define OPEN_CFW_RUNTIME_LINKED_LIST_REMOVE_SET_NEXT(list, node, next) \
    open_cfw_test_runtime_linked_list_remove_set_next( \
        (list), (node), (next) \
    )

#include "../../components/apollo_main/core_overlay/runtime_linked_list_remove.c"

enum {
    OPEN_CFW_TEST_RUNTIME_LINKED_LIST_REMOVE_STORAGE_SIZE = 4096U,
    OPEN_CFW_TEST_RUNTIME_LINKED_LIST_REMOVE_NODE_SIZE = 16U,
    OPEN_CFW_TEST_RUNTIME_LINKED_LIST_REMOVE_NODE_BASE = 128U,
    OPEN_CFW_TEST_RUNTIME_LINKED_LIST_REMOVE_NODE_STRIDE = 64U,
    OPEN_CFW_TEST_RUNTIME_LINKED_LIST_REMOVE_MAX_EVENTS = 16U,
    OPEN_CFW_TEST_RUNTIME_LINKED_LIST_REMOVE_EVENT_GET_HEAD = 1U,
    OPEN_CFW_TEST_RUNTIME_LINKED_LIST_REMOVE_EVENT_GET_TAIL = 2U,
    OPEN_CFW_TEST_RUNTIME_LINKED_LIST_REMOVE_EVENT_GET_PREVIOUS = 3U,
    OPEN_CFW_TEST_RUNTIME_LINKED_LIST_REMOVE_EVENT_GET_NEXT = 4U,
    OPEN_CFW_TEST_RUNTIME_LINKED_LIST_REMOVE_EVENT_SET_PREVIOUS = 5U,
    OPEN_CFW_TEST_RUNTIME_LINKED_LIST_REMOVE_EVENT_SET_NEXT = 6U,
    OPEN_CFW_TEST_RUNTIME_LINKED_LIST_REMOVE_EVENT_FAULT = 7U
};

unsigned char open_cfw_test_runtime_linked_list_remove_storage[
    OPEN_CFW_TEST_RUNTIME_LINKED_LIST_REMOVE_STORAGE_SIZE
];
struct open_cfw_runtime_linked_list_remove_descriptor
    open_cfw_test_runtime_linked_list_remove_descriptor;
unsigned int open_cfw_test_runtime_linked_list_remove_event_count;
unsigned int open_cfw_test_runtime_linked_list_remove_event_kind[
    OPEN_CFW_TEST_RUNTIME_LINKED_LIST_REMOVE_MAX_EVENTS
];
unsigned int open_cfw_test_runtime_linked_list_remove_event_node[
    OPEN_CFW_TEST_RUNTIME_LINKED_LIST_REMOVE_MAX_EVENTS
];
unsigned int open_cfw_test_runtime_linked_list_remove_event_link[
    OPEN_CFW_TEST_RUNTIME_LINKED_LIST_REMOVE_MAX_EVENTS
];
unsigned int open_cfw_test_runtime_linked_list_remove_event_head[
    OPEN_CFW_TEST_RUNTIME_LINKED_LIST_REMOVE_MAX_EVENTS
];
unsigned int open_cfw_test_runtime_linked_list_remove_event_tail[
    OPEN_CFW_TEST_RUNTIME_LINKED_LIST_REMOVE_MAX_EVENTS
];

static jmp_buf open_cfw_test_runtime_linked_list_remove_fault_target;
static int open_cfw_test_runtime_linked_list_remove_fault_armed;

static unsigned int open_cfw_test_runtime_linked_list_remove_node(
    unsigned int index
)
{
    return (
        OPEN_CFW_TEST_RUNTIME_LINKED_LIST_REMOVE_NODE_BASE
        + index * OPEN_CFW_TEST_RUNTIME_LINKED_LIST_REMOVE_NODE_STRIDE
    );
}

static unsigned int open_cfw_test_runtime_linked_list_remove_load_word(
    unsigned int offset
)
{
    return (
        (unsigned int)
        open_cfw_test_runtime_linked_list_remove_storage[offset]
        | (
            (unsigned int)
            open_cfw_test_runtime_linked_list_remove_storage[offset + 1U]
            << 8U
        )
        | (
            (unsigned int)
            open_cfw_test_runtime_linked_list_remove_storage[offset + 2U]
            << 16U
        )
        | (
            (unsigned int)
            open_cfw_test_runtime_linked_list_remove_storage[offset + 3U]
            << 24U
        )
    );
}

static void open_cfw_test_runtime_linked_list_remove_store_word(
    unsigned int offset,
    unsigned int value
)
{
    open_cfw_test_runtime_linked_list_remove_storage[offset] =
        (unsigned char)value;
    open_cfw_test_runtime_linked_list_remove_storage[offset + 1U] =
        (unsigned char)(value >> 8U);
    open_cfw_test_runtime_linked_list_remove_storage[offset + 2U] =
        (unsigned char)(value >> 16U);
    open_cfw_test_runtime_linked_list_remove_storage[offset + 3U] =
        (unsigned char)(value >> 24U);
}

static unsigned int open_cfw_test_runtime_linked_list_remove_previous(
    unsigned int node
)
{
    return open_cfw_test_runtime_linked_list_remove_load_word(
        node + OPEN_CFW_TEST_RUNTIME_LINKED_LIST_REMOVE_NODE_SIZE
    );
}

static unsigned int open_cfw_test_runtime_linked_list_remove_next(
    unsigned int node
)
{
    return open_cfw_test_runtime_linked_list_remove_load_word(
        node + OPEN_CFW_TEST_RUNTIME_LINKED_LIST_REMOVE_NODE_SIZE + 4U
    );
}

static void open_cfw_test_runtime_linked_list_remove_record(
    unsigned int kind,
    unsigned int node,
    unsigned int link
)
{
    unsigned int index =
        open_cfw_test_runtime_linked_list_remove_event_count;

    if (index < OPEN_CFW_TEST_RUNTIME_LINKED_LIST_REMOVE_MAX_EVENTS) {
        open_cfw_test_runtime_linked_list_remove_event_kind[index] = kind;
        open_cfw_test_runtime_linked_list_remove_event_node[index] = node;
        open_cfw_test_runtime_linked_list_remove_event_link[index] = link;
        open_cfw_test_runtime_linked_list_remove_event_head[index] =
            open_cfw_test_runtime_linked_list_remove_descriptor.head;
        open_cfw_test_runtime_linked_list_remove_event_tail[index] =
            open_cfw_test_runtime_linked_list_remove_descriptor.tail;
    }
    open_cfw_test_runtime_linked_list_remove_event_count = index + 1U;
}

static void open_cfw_test_runtime_linked_list_remove_fault(
    unsigned int kind
)
{
    open_cfw_test_runtime_linked_list_remove_record(
        OPEN_CFW_TEST_RUNTIME_LINKED_LIST_REMOVE_EVENT_FAULT,
        0U,
        kind
    );
    if (open_cfw_test_runtime_linked_list_remove_fault_armed != 0) {
        longjmp(open_cfw_test_runtime_linked_list_remove_fault_target, 1);
    }
}

static unsigned int open_cfw_test_runtime_linked_list_remove_get_head(
    const void *list_pointer
)
{
    const struct open_cfw_runtime_linked_list_remove_descriptor *list =
        (const struct open_cfw_runtime_linked_list_remove_descriptor *)
        list_pointer;

    open_cfw_test_runtime_linked_list_remove_record(
        OPEN_CFW_TEST_RUNTIME_LINKED_LIST_REMOVE_EVENT_GET_HEAD,
        0U,
        list->head
    );
    return list->head;
}

static unsigned int open_cfw_test_runtime_linked_list_remove_get_tail(
    const void *list_pointer
)
{
    const struct open_cfw_runtime_linked_list_remove_descriptor *list =
        (const struct open_cfw_runtime_linked_list_remove_descriptor *)
        list_pointer;

    open_cfw_test_runtime_linked_list_remove_record(
        OPEN_CFW_TEST_RUNTIME_LINKED_LIST_REMOVE_EVENT_GET_TAIL,
        0U,
        list->tail
    );
    return list->tail;
}

static unsigned int open_cfw_test_runtime_linked_list_remove_get_next(
    const void *list_pointer,
    unsigned int node
)
{
    unsigned int next;

    (void)list_pointer;
    if (node == 0U) {
        open_cfw_test_runtime_linked_list_remove_fault(
            OPEN_CFW_TEST_RUNTIME_LINKED_LIST_REMOVE_EVENT_GET_NEXT
        );
        return 0U;
    }
    next = open_cfw_test_runtime_linked_list_remove_next(node);
    open_cfw_test_runtime_linked_list_remove_record(
        OPEN_CFW_TEST_RUNTIME_LINKED_LIST_REMOVE_EVENT_GET_NEXT,
        node,
        next
    );
    return next;
}

static unsigned int open_cfw_test_runtime_linked_list_remove_get_previous(
    const void *list_pointer,
    unsigned int node
)
{
    unsigned int previous;

    (void)list_pointer;
    if (node == 0U) {
        open_cfw_test_runtime_linked_list_remove_fault(
            OPEN_CFW_TEST_RUNTIME_LINKED_LIST_REMOVE_EVENT_GET_PREVIOUS
        );
        return 0U;
    }
    previous = open_cfw_test_runtime_linked_list_remove_previous(node);
    open_cfw_test_runtime_linked_list_remove_record(
        OPEN_CFW_TEST_RUNTIME_LINKED_LIST_REMOVE_EVENT_GET_PREVIOUS,
        node,
        previous
    );
    return previous;
}

static void open_cfw_test_runtime_linked_list_remove_set_previous(
    void *list_pointer,
    unsigned int node,
    unsigned int previous
)
{
    (void)list_pointer;
    open_cfw_test_runtime_linked_list_remove_record(
        OPEN_CFW_TEST_RUNTIME_LINKED_LIST_REMOVE_EVENT_SET_PREVIOUS,
        node,
        previous
    );
    if (node != 0U) {
        open_cfw_test_runtime_linked_list_remove_store_word(
            node + OPEN_CFW_TEST_RUNTIME_LINKED_LIST_REMOVE_NODE_SIZE,
            previous
        );
    }
}

static void open_cfw_test_runtime_linked_list_remove_set_next(
    void *list_pointer,
    unsigned int node,
    unsigned int next
)
{
    (void)list_pointer;
    open_cfw_test_runtime_linked_list_remove_record(
        OPEN_CFW_TEST_RUNTIME_LINKED_LIST_REMOVE_EVENT_SET_NEXT,
        node,
        next
    );
    if (node != 0U) {
        open_cfw_test_runtime_linked_list_remove_store_word(
            node + OPEN_CFW_TEST_RUNTIME_LINKED_LIST_REMOVE_NODE_SIZE + 4U,
            next
        );
    }
}

void open_cfw_test_runtime_linked_list_remove_reset(unsigned int count)
{
    unsigned int index;

    for (
        index = 0U;
        index < OPEN_CFW_TEST_RUNTIME_LINKED_LIST_REMOVE_STORAGE_SIZE;
        index += 1U
    ) {
        open_cfw_test_runtime_linked_list_remove_storage[index] = 0xCCU;
    }
    for (
        index = 0U;
        index < OPEN_CFW_TEST_RUNTIME_LINKED_LIST_REMOVE_MAX_EVENTS;
        index += 1U
    ) {
        open_cfw_test_runtime_linked_list_remove_event_kind[index] = 0U;
        open_cfw_test_runtime_linked_list_remove_event_node[index] = 0U;
        open_cfw_test_runtime_linked_list_remove_event_link[index] = 0U;
        open_cfw_test_runtime_linked_list_remove_event_head[index] = 0U;
        open_cfw_test_runtime_linked_list_remove_event_tail[index] = 0U;
    }

    open_cfw_test_runtime_linked_list_remove_descriptor.node_size =
        OPEN_CFW_TEST_RUNTIME_LINKED_LIST_REMOVE_NODE_SIZE;
    open_cfw_test_runtime_linked_list_remove_descriptor.head =
        count == 0U
        ? 0U
        : open_cfw_test_runtime_linked_list_remove_node(0U);
    open_cfw_test_runtime_linked_list_remove_descriptor.tail =
        count == 0U
        ? 0U
        : open_cfw_test_runtime_linked_list_remove_node(count - 1U);
    open_cfw_test_runtime_linked_list_remove_event_count = 0U;
    open_cfw_test_runtime_linked_list_remove_fault_armed = 0;

    for (index = 0U; index < count; index += 1U) {
        unsigned int node =
            open_cfw_test_runtime_linked_list_remove_node(index);
        unsigned int previous =
            index == 0U
            ? 0U
            : open_cfw_test_runtime_linked_list_remove_node(index - 1U);
        unsigned int next =
            index + 1U == count
            ? 0U
            : open_cfw_test_runtime_linked_list_remove_node(index + 1U);

        open_cfw_test_runtime_linked_list_remove_store_word(
            node + OPEN_CFW_TEST_RUNTIME_LINKED_LIST_REMOVE_NODE_SIZE,
            previous
        );
        open_cfw_test_runtime_linked_list_remove_store_word(
            node + OPEN_CFW_TEST_RUNTIME_LINKED_LIST_REMOVE_NODE_SIZE + 4U,
            next
        );
    }
}

unsigned int open_cfw_test_runtime_linked_list_remove_node_at(
    unsigned int index
)
{
    return open_cfw_test_runtime_linked_list_remove_node(index);
}

unsigned int open_cfw_test_runtime_linked_list_remove_previous_at(
    unsigned int node
)
{
    return open_cfw_test_runtime_linked_list_remove_previous(node);
}

unsigned int open_cfw_test_runtime_linked_list_remove_next_at(
    unsigned int node
)
{
    return open_cfw_test_runtime_linked_list_remove_next(node);
}

void open_cfw_test_runtime_linked_list_remove_set_links(
    unsigned int node,
    unsigned int previous,
    unsigned int next
)
{
    open_cfw_test_runtime_linked_list_remove_store_word(
        node + OPEN_CFW_TEST_RUNTIME_LINKED_LIST_REMOVE_NODE_SIZE,
        previous
    );
    open_cfw_test_runtime_linked_list_remove_store_word(
        node + OPEN_CFW_TEST_RUNTIME_LINKED_LIST_REMOVE_NODE_SIZE + 4U,
        next
    );
}

void open_cfw_test_runtime_linked_list_remove_set_descriptor(
    unsigned int head,
    unsigned int tail
)
{
    open_cfw_test_runtime_linked_list_remove_descriptor.head = head;
    open_cfw_test_runtime_linked_list_remove_descriptor.tail = tail;
}

unsigned int open_cfw_test_runtime_linked_list_remove_execute(
    unsigned int node
)
{
    int faulted;

    open_cfw_test_runtime_linked_list_remove_fault_armed = 1;
    faulted = setjmp(open_cfw_test_runtime_linked_list_remove_fault_target);
    if (faulted == 0) {
        open_cfw_runtime_linked_list_remove(
            &open_cfw_test_runtime_linked_list_remove_descriptor,
            node
        );
    }
    open_cfw_test_runtime_linked_list_remove_fault_armed = 0;
    return faulted == 0 ? 0U : 1U;
}

unsigned int open_cfw_test_runtime_linked_list_remove_execute_null_list(
    unsigned int node
)
{
    open_cfw_runtime_linked_list_remove(
        (struct open_cfw_runtime_linked_list_remove_descriptor *)0,
        node
    );
    return 0U;
}
