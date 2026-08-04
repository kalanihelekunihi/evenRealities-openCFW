/*
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * Host substitutions for the source-owned G2 linked-list move-before
 * routine.
 */

static unsigned int open_cfw_test_runtime_linked_list_move_get_tail(
    const void *list
);
static unsigned int open_cfw_test_runtime_linked_list_move_get_previous(
    const void *list,
    unsigned int node
);
static void open_cfw_test_runtime_linked_list_move_remove(
    void *list,
    unsigned int node
);
static void open_cfw_test_runtime_linked_list_move_set_previous(
    void *list,
    unsigned int node,
    unsigned int previous
);
static void open_cfw_test_runtime_linked_list_move_set_next(
    void *list,
    unsigned int node,
    unsigned int next
);

#define OPEN_CFW_RUNTIME_LINKED_LIST_MOVE_GET_TAIL(list) \
    open_cfw_test_runtime_linked_list_move_get_tail((list))
#define OPEN_CFW_RUNTIME_LINKED_LIST_MOVE_GET_PREVIOUS(list, node) \
    open_cfw_test_runtime_linked_list_move_get_previous((list), (node))
#define OPEN_CFW_RUNTIME_LINKED_LIST_MOVE_REMOVE(list, node) \
    open_cfw_test_runtime_linked_list_move_remove((list), (node))
#define OPEN_CFW_RUNTIME_LINKED_LIST_MOVE_SET_PREVIOUS( \
    list, node, previous \
) \
    open_cfw_test_runtime_linked_list_move_set_previous( \
        (list), (node), (previous) \
    )
#define OPEN_CFW_RUNTIME_LINKED_LIST_MOVE_SET_NEXT(list, node, next) \
    open_cfw_test_runtime_linked_list_move_set_next( \
        (list), (node), (next) \
    )

#include "../../components/apollo_main/core_overlay/runtime_linked_list_move_before.c"

enum {
    OPEN_CFW_TEST_RUNTIME_LINKED_LIST_MOVE_STORAGE_SIZE = 4096U,
    OPEN_CFW_TEST_RUNTIME_LINKED_LIST_MOVE_NODE_SIZE = 16U,
    OPEN_CFW_TEST_RUNTIME_LINKED_LIST_MOVE_NODE_BASE = 128U,
    OPEN_CFW_TEST_RUNTIME_LINKED_LIST_MOVE_NODE_STRIDE = 64U,
    OPEN_CFW_TEST_RUNTIME_LINKED_LIST_MOVE_MAX_EVENTS = 16U,
    OPEN_CFW_TEST_RUNTIME_LINKED_LIST_MOVE_EVENT_GET_TAIL = 1U,
    OPEN_CFW_TEST_RUNTIME_LINKED_LIST_MOVE_EVENT_GET_PREVIOUS = 2U,
    OPEN_CFW_TEST_RUNTIME_LINKED_LIST_MOVE_EVENT_REMOVE = 3U,
    OPEN_CFW_TEST_RUNTIME_LINKED_LIST_MOVE_EVENT_SET_PREVIOUS = 4U,
    OPEN_CFW_TEST_RUNTIME_LINKED_LIST_MOVE_EVENT_SET_NEXT = 5U
};

unsigned char open_cfw_test_runtime_linked_list_move_storage[
    OPEN_CFW_TEST_RUNTIME_LINKED_LIST_MOVE_STORAGE_SIZE
];
struct open_cfw_runtime_linked_list_move_descriptor
    open_cfw_test_runtime_linked_list_move_descriptor;
unsigned int open_cfw_test_runtime_linked_list_move_event_count;
unsigned int open_cfw_test_runtime_linked_list_move_event_kind[
    OPEN_CFW_TEST_RUNTIME_LINKED_LIST_MOVE_MAX_EVENTS
];
unsigned int open_cfw_test_runtime_linked_list_move_event_node[
    OPEN_CFW_TEST_RUNTIME_LINKED_LIST_MOVE_MAX_EVENTS
];
unsigned int open_cfw_test_runtime_linked_list_move_event_link[
    OPEN_CFW_TEST_RUNTIME_LINKED_LIST_MOVE_MAX_EVENTS
];
unsigned int open_cfw_test_runtime_linked_list_move_event_head[
    OPEN_CFW_TEST_RUNTIME_LINKED_LIST_MOVE_MAX_EVENTS
];
unsigned int open_cfw_test_runtime_linked_list_move_event_tail[
    OPEN_CFW_TEST_RUNTIME_LINKED_LIST_MOVE_MAX_EVENTS
];

static unsigned int open_cfw_test_runtime_linked_list_move_node(
    unsigned int index
)
{
    return (
        OPEN_CFW_TEST_RUNTIME_LINKED_LIST_MOVE_NODE_BASE
        + index * OPEN_CFW_TEST_RUNTIME_LINKED_LIST_MOVE_NODE_STRIDE
    );
}

static unsigned int open_cfw_test_runtime_linked_list_move_load_word(
    unsigned int offset
)
{
    return (
        (unsigned int)open_cfw_test_runtime_linked_list_move_storage[offset]
        | (
            (unsigned int)
            open_cfw_test_runtime_linked_list_move_storage[offset + 1U]
            << 8U
        )
        | (
            (unsigned int)
            open_cfw_test_runtime_linked_list_move_storage[offset + 2U]
            << 16U
        )
        | (
            (unsigned int)
            open_cfw_test_runtime_linked_list_move_storage[offset + 3U]
            << 24U
        )
    );
}

static void open_cfw_test_runtime_linked_list_move_store_word(
    unsigned int offset,
    unsigned int value
)
{
    open_cfw_test_runtime_linked_list_move_storage[offset] =
        (unsigned char)value;
    open_cfw_test_runtime_linked_list_move_storage[offset + 1U] =
        (unsigned char)(value >> 8U);
    open_cfw_test_runtime_linked_list_move_storage[offset + 2U] =
        (unsigned char)(value >> 16U);
    open_cfw_test_runtime_linked_list_move_storage[offset + 3U] =
        (unsigned char)(value >> 24U);
}

static unsigned int open_cfw_test_runtime_linked_list_move_previous(
    unsigned int node
)
{
    return open_cfw_test_runtime_linked_list_move_load_word(
        node + OPEN_CFW_TEST_RUNTIME_LINKED_LIST_MOVE_NODE_SIZE
    );
}

static unsigned int open_cfw_test_runtime_linked_list_move_next(
    unsigned int node
)
{
    return open_cfw_test_runtime_linked_list_move_load_word(
        node + OPEN_CFW_TEST_RUNTIME_LINKED_LIST_MOVE_NODE_SIZE + 4U
    );
}

static void open_cfw_test_runtime_linked_list_move_record(
    unsigned int kind,
    unsigned int node,
    unsigned int link
)
{
    unsigned int index =
        open_cfw_test_runtime_linked_list_move_event_count;

    if (index < OPEN_CFW_TEST_RUNTIME_LINKED_LIST_MOVE_MAX_EVENTS) {
        open_cfw_test_runtime_linked_list_move_event_kind[index] = kind;
        open_cfw_test_runtime_linked_list_move_event_node[index] = node;
        open_cfw_test_runtime_linked_list_move_event_link[index] = link;
        open_cfw_test_runtime_linked_list_move_event_head[index] =
            open_cfw_test_runtime_linked_list_move_descriptor.head;
        open_cfw_test_runtime_linked_list_move_event_tail[index] =
            open_cfw_test_runtime_linked_list_move_descriptor.tail;
    }
    open_cfw_test_runtime_linked_list_move_event_count = index + 1U;
}

static unsigned int open_cfw_test_runtime_linked_list_move_get_tail(
    const void *list_pointer
)
{
    const struct open_cfw_runtime_linked_list_move_descriptor *list =
        (const struct open_cfw_runtime_linked_list_move_descriptor *)
        list_pointer;

    open_cfw_test_runtime_linked_list_move_record(
        OPEN_CFW_TEST_RUNTIME_LINKED_LIST_MOVE_EVENT_GET_TAIL,
        0U,
        list->tail
    );
    return list->tail;
}

static unsigned int open_cfw_test_runtime_linked_list_move_get_previous(
    const void *list_pointer,
    unsigned int node
)
{
    unsigned int previous;

    (void)list_pointer;
    previous = open_cfw_test_runtime_linked_list_move_previous(node);
    open_cfw_test_runtime_linked_list_move_record(
        OPEN_CFW_TEST_RUNTIME_LINKED_LIST_MOVE_EVENT_GET_PREVIOUS,
        node,
        previous
    );
    return previous;
}

static void open_cfw_test_runtime_linked_list_move_remove(
    void *list_pointer,
    unsigned int node
)
{
    struct open_cfw_runtime_linked_list_move_descriptor *list =
        (struct open_cfw_runtime_linked_list_move_descriptor *)list_pointer;
    unsigned int previous =
        open_cfw_test_runtime_linked_list_move_previous(node);
    unsigned int next = open_cfw_test_runtime_linked_list_move_next(node);

    open_cfw_test_runtime_linked_list_move_record(
        OPEN_CFW_TEST_RUNTIME_LINKED_LIST_MOVE_EVENT_REMOVE,
        node,
        0U
    );
    if (list->head == node) {
        list->head = next;
        if (next == 0U) {
            list->tail = 0U;
        } else {
            open_cfw_test_runtime_linked_list_move_store_word(
                next + OPEN_CFW_TEST_RUNTIME_LINKED_LIST_MOVE_NODE_SIZE,
                0U
            );
        }
        return;
    }
    if (list->tail == node) {
        list->tail = previous;
        if (previous == 0U) {
            list->head = 0U;
        } else {
            open_cfw_test_runtime_linked_list_move_store_word(
                previous
                + OPEN_CFW_TEST_RUNTIME_LINKED_LIST_MOVE_NODE_SIZE
                + 4U,
                0U
            );
        }
        return;
    }

    if (previous != 0U) {
        open_cfw_test_runtime_linked_list_move_store_word(
            previous
            + OPEN_CFW_TEST_RUNTIME_LINKED_LIST_MOVE_NODE_SIZE
            + 4U,
            next
        );
    }
    if (next != 0U) {
        open_cfw_test_runtime_linked_list_move_store_word(
            next + OPEN_CFW_TEST_RUNTIME_LINKED_LIST_MOVE_NODE_SIZE,
            previous
        );
    }
}

static void open_cfw_test_runtime_linked_list_move_set_previous(
    void *list_pointer,
    unsigned int node,
    unsigned int previous
)
{
    (void)list_pointer;
    open_cfw_test_runtime_linked_list_move_record(
        OPEN_CFW_TEST_RUNTIME_LINKED_LIST_MOVE_EVENT_SET_PREVIOUS,
        node,
        previous
    );
    if (node != 0U) {
        open_cfw_test_runtime_linked_list_move_store_word(
            node + OPEN_CFW_TEST_RUNTIME_LINKED_LIST_MOVE_NODE_SIZE,
            previous
        );
    }
}

static void open_cfw_test_runtime_linked_list_move_set_next(
    void *list_pointer,
    unsigned int node,
    unsigned int next
)
{
    (void)list_pointer;
    open_cfw_test_runtime_linked_list_move_record(
        OPEN_CFW_TEST_RUNTIME_LINKED_LIST_MOVE_EVENT_SET_NEXT,
        node,
        next
    );
    if (node != 0U) {
        open_cfw_test_runtime_linked_list_move_store_word(
            node + OPEN_CFW_TEST_RUNTIME_LINKED_LIST_MOVE_NODE_SIZE + 4U,
            next
        );
    }
}

void open_cfw_test_runtime_linked_list_move_reset(unsigned int count)
{
    unsigned int index;

    for (
        index = 0U;
        index < OPEN_CFW_TEST_RUNTIME_LINKED_LIST_MOVE_STORAGE_SIZE;
        index += 1U
    ) {
        open_cfw_test_runtime_linked_list_move_storage[index] = 0xCCU;
    }
    for (
        index = 0U;
        index < OPEN_CFW_TEST_RUNTIME_LINKED_LIST_MOVE_MAX_EVENTS;
        index += 1U
    ) {
        open_cfw_test_runtime_linked_list_move_event_kind[index] = 0U;
        open_cfw_test_runtime_linked_list_move_event_node[index] = 0U;
        open_cfw_test_runtime_linked_list_move_event_link[index] = 0U;
        open_cfw_test_runtime_linked_list_move_event_head[index] = 0U;
        open_cfw_test_runtime_linked_list_move_event_tail[index] = 0U;
    }

    open_cfw_test_runtime_linked_list_move_descriptor.node_size =
        OPEN_CFW_TEST_RUNTIME_LINKED_LIST_MOVE_NODE_SIZE;
    open_cfw_test_runtime_linked_list_move_descriptor.head =
        count == 0U
        ? 0U
        : open_cfw_test_runtime_linked_list_move_node(0U);
    open_cfw_test_runtime_linked_list_move_descriptor.tail =
        count == 0U
        ? 0U
        : open_cfw_test_runtime_linked_list_move_node(count - 1U);
    open_cfw_test_runtime_linked_list_move_event_count = 0U;

    for (index = 0U; index < count; index += 1U) {
        unsigned int node =
            open_cfw_test_runtime_linked_list_move_node(index);
        unsigned int previous =
            index == 0U
            ? 0U
            : open_cfw_test_runtime_linked_list_move_node(index - 1U);
        unsigned int next =
            index + 1U == count
            ? 0U
            : open_cfw_test_runtime_linked_list_move_node(index + 1U);

        open_cfw_test_runtime_linked_list_move_store_word(
            node + OPEN_CFW_TEST_RUNTIME_LINKED_LIST_MOVE_NODE_SIZE,
            previous
        );
        open_cfw_test_runtime_linked_list_move_store_word(
            node + OPEN_CFW_TEST_RUNTIME_LINKED_LIST_MOVE_NODE_SIZE + 4U,
            next
        );
    }
}

unsigned int open_cfw_test_runtime_linked_list_move_node_at(
    unsigned int index
)
{
    return open_cfw_test_runtime_linked_list_move_node(index);
}

unsigned int open_cfw_test_runtime_linked_list_move_previous_at(
    unsigned int node
)
{
    return open_cfw_test_runtime_linked_list_move_previous(node);
}

unsigned int open_cfw_test_runtime_linked_list_move_next_at(
    unsigned int node
)
{
    return open_cfw_test_runtime_linked_list_move_next(node);
}

void open_cfw_test_runtime_linked_list_move_set_links(
    unsigned int node,
    unsigned int previous,
    unsigned int next
)
{
    open_cfw_test_runtime_linked_list_move_store_word(
        node + OPEN_CFW_TEST_RUNTIME_LINKED_LIST_MOVE_NODE_SIZE,
        previous
    );
    open_cfw_test_runtime_linked_list_move_store_word(
        node + OPEN_CFW_TEST_RUNTIME_LINKED_LIST_MOVE_NODE_SIZE + 4U,
        next
    );
}

void open_cfw_test_runtime_linked_list_move_execute(
    unsigned int moving,
    unsigned int before
)
{
    open_cfw_runtime_linked_list_move_before(
        &open_cfw_test_runtime_linked_list_move_descriptor,
        moving,
        before
    );
}

void open_cfw_test_runtime_linked_list_move_execute_null_list(
    unsigned int moving,
    unsigned int before
)
{
    open_cfw_runtime_linked_list_move_before(
        (struct open_cfw_runtime_linked_list_move_descriptor *)0,
        moving,
        before
    );
}
