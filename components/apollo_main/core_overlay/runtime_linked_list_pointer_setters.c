/*
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * Bounded source replacements for the G2 2.2.6.10 LVGL linked-list
 * previous/next pointer setters at 0x00482DAE...0x00482DD7.
 * Both functions remain distinct noinline symbols for independent patches.
 */

typedef unsigned int open_cfw_runtime_linked_list_setter_word;
typedef unsigned int open_cfw_runtime_linked_list_setter_pointer;

struct open_cfw_runtime_linked_list_setter {
    open_cfw_runtime_linked_list_setter_word node_size;
    open_cfw_runtime_linked_list_setter_pointer head;
    open_cfw_runtime_linked_list_setter_pointer tail;
};

_Static_assert(
    sizeof(open_cfw_runtime_linked_list_setter_word) == 4U,
    "linked-list setter word width changed"
);
_Static_assert(
    sizeof(open_cfw_runtime_linked_list_setter_pointer) == 4U,
    "linked-list setter pointer width changed"
);
_Static_assert(
    sizeof(struct open_cfw_runtime_linked_list_setter) == 12U,
    "linked-list setter descriptor size changed"
);

#ifndef OPEN_CFW_RUNTIME_LINKED_LIST_SETTER_POINTER_TO_BYTES
#define OPEN_CFW_RUNTIME_LINKED_LIST_SETTER_POINTER_TO_BYTES(value) \
    ((unsigned char *)(__UINTPTR_TYPE__)(value))
#endif

__attribute__((used, noinline))
void open_cfw_runtime_linked_list_set_previous(
    const struct open_cfw_runtime_linked_list_setter *list,
    open_cfw_runtime_linked_list_setter_pointer node,
    open_cfw_runtime_linked_list_setter_pointer previous
)
{
    unsigned char *node_bytes;

    if (node == 0U) {
        return;
    }
    node_bytes =
        OPEN_CFW_RUNTIME_LINKED_LIST_SETTER_POINTER_TO_BYTES(node);
    *(open_cfw_runtime_linked_list_setter_pointer *)(void *)(
        node_bytes + list->node_size
    ) = previous;
}

__attribute__((used, noinline))
void open_cfw_runtime_linked_list_set_next(
    const struct open_cfw_runtime_linked_list_setter *list,
    open_cfw_runtime_linked_list_setter_pointer node,
    open_cfw_runtime_linked_list_setter_pointer next
)
{
    unsigned char *node_bytes;

    if (node == 0U) {
        return;
    }
    node_bytes =
        OPEN_CFW_RUNTIME_LINKED_LIST_SETTER_POINTER_TO_BYTES(node);
    *(open_cfw_runtime_linked_list_setter_pointer *)(void *)(
        node_bytes + list->node_size + 4U
    ) = next;
}

#undef OPEN_CFW_RUNTIME_LINKED_LIST_SETTER_POINTER_TO_BYTES
