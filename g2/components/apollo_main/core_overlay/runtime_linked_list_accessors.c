/*
 * SPDX-License-Identifier: MIT
 *
 * Bounded source replacements for the G2 2.2.6.10 LVGL linked-list leaf
 * cluster at 0x00482CD8...0x00482DAD. Every public function remains a
 * distinct, noinline symbol so its stock entry can be redirected separately.
 */

typedef unsigned int open_cfw_runtime_linked_list_accessor_word;
typedef unsigned int open_cfw_runtime_linked_list_accessor_pointer;

struct open_cfw_runtime_linked_list_accessor {
    open_cfw_runtime_linked_list_accessor_word node_size;
    open_cfw_runtime_linked_list_accessor_pointer head;
    open_cfw_runtime_linked_list_accessor_pointer tail;
};

_Static_assert(
    sizeof(open_cfw_runtime_linked_list_accessor_word) == 4U,
    "linked-list accessor word width changed"
);
_Static_assert(
    sizeof(open_cfw_runtime_linked_list_accessor_pointer) == 4U,
    "linked-list accessor pointer width changed"
);
_Static_assert(
    sizeof(struct open_cfw_runtime_linked_list_accessor) == 12U,
    "linked-list accessor descriptor size changed"
);
_Static_assert(
    __builtin_offsetof(
        struct open_cfw_runtime_linked_list_accessor,
        head
    ) == 4U,
    "linked-list accessor head offset changed"
);
_Static_assert(
    __builtin_offsetof(
        struct open_cfw_runtime_linked_list_accessor,
        tail
    ) == 8U,
    "linked-list accessor tail offset changed"
);

#ifndef OPEN_CFW_RUNTIME_LINKED_LIST_POINTER_TO_BYTES
#define OPEN_CFW_RUNTIME_LINKED_LIST_POINTER_TO_BYTES(value) \
    ((const unsigned char *)(__UINTPTR_TYPE__)(value))
#endif

#ifndef OPEN_CFW_RUNTIME_LINKED_LIST_CLEAR_CUSTOM
typedef void (*open_cfw_runtime_linked_list_clear_custom_fn)(
    struct open_cfw_runtime_linked_list_accessor *,
    void *
);
#define OPEN_CFW_RUNTIME_LINKED_LIST_CLEAR_CUSTOM(list, cleanup) \
    (((open_cfw_runtime_linked_list_clear_custom_fn) \
        (__UINTPTR_TYPE__)0x00482C9BU)((list), (cleanup)))
#endif

__attribute__((used, noinline))
open_cfw_runtime_linked_list_accessor_pointer
open_cfw_runtime_linked_list_get_head(
    const struct open_cfw_runtime_linked_list_accessor *list
)
{
    if (list == (const struct open_cfw_runtime_linked_list_accessor *)0) {
        return 0U;
    }
    return list->head;
}

__attribute__((used, noinline))
open_cfw_runtime_linked_list_accessor_pointer
open_cfw_runtime_linked_list_get_tail(
    const struct open_cfw_runtime_linked_list_accessor *list
)
{
    if (list == (const struct open_cfw_runtime_linked_list_accessor *)0) {
        return 0U;
    }
    return list->tail;
}

__attribute__((used, noinline))
open_cfw_runtime_linked_list_accessor_pointer
open_cfw_runtime_linked_list_get_next(
    const struct open_cfw_runtime_linked_list_accessor *list,
    open_cfw_runtime_linked_list_accessor_pointer node
)
{
    const unsigned char *node_bytes =
        OPEN_CFW_RUNTIME_LINKED_LIST_POINTER_TO_BYTES(node);

    return *(const open_cfw_runtime_linked_list_accessor_pointer *)(
        const void *
    )(node_bytes + list->node_size + 4U);
}

__attribute__((used, noinline))
open_cfw_runtime_linked_list_accessor_pointer
open_cfw_runtime_linked_list_get_previous(
    const struct open_cfw_runtime_linked_list_accessor *list,
    open_cfw_runtime_linked_list_accessor_pointer node
)
{
    const unsigned char *node_bytes =
        OPEN_CFW_RUNTIME_LINKED_LIST_POINTER_TO_BYTES(node);

    return *(const open_cfw_runtime_linked_list_accessor_pointer *)(
        const void *
    )(node_bytes + list->node_size);
}

__attribute__((used, noinline))
open_cfw_runtime_linked_list_accessor_word
open_cfw_runtime_linked_list_get_length(
    const struct open_cfw_runtime_linked_list_accessor *list
)
{
    open_cfw_runtime_linked_list_accessor_pointer node;
    open_cfw_runtime_linked_list_accessor_word length = 0U;

    node = open_cfw_runtime_linked_list_get_head(list);
    while (node != 0U) {
        length += 1U;
        node = open_cfw_runtime_linked_list_get_next(list, node);
    }
    return length;
}

__attribute__((used, noinline))
unsigned char open_cfw_runtime_linked_list_is_empty(
    const struct open_cfw_runtime_linked_list_accessor *list
)
{
    if (list == (const struct open_cfw_runtime_linked_list_accessor *)0) {
        return 1U;
    }
    if (list->head == 0U && list->tail == 0U) {
        return 1U;
    }
    return 0U;
}

__attribute__((used, noinline))
void open_cfw_runtime_linked_list_clear(
    struct open_cfw_runtime_linked_list_accessor *list
)
{
    OPEN_CFW_RUNTIME_LINKED_LIST_CLEAR_CUSTOM(list, (void *)0);
}

#undef OPEN_CFW_RUNTIME_LINKED_LIST_CLEAR_CUSTOM
#undef OPEN_CFW_RUNTIME_LINKED_LIST_POINTER_TO_BYTES
