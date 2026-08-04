/*
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * Bounded source replacement for the G2 2.2.6.10 LVGL linked-list
 * initializer at 0x00482B00...0x00482B11.
 *
 * The 32-bit target descriptor stores the rounded node payload size at
 * offset zero, its head pointer at +4, and its tail pointer at +8.
 */

typedef unsigned int open_cfw_runtime_linked_list_word;
typedef unsigned int open_cfw_runtime_linked_list_pointer;

struct open_cfw_runtime_linked_list {
    open_cfw_runtime_linked_list_word node_size;
    open_cfw_runtime_linked_list_pointer head;
    open_cfw_runtime_linked_list_pointer tail;
};

_Static_assert(
    sizeof(open_cfw_runtime_linked_list_word) == 4U,
    "linked-list word width changed"
);
_Static_assert(
    sizeof(open_cfw_runtime_linked_list_pointer) == 4U,
    "linked-list pointer width changed"
);
_Static_assert(
    sizeof(struct open_cfw_runtime_linked_list) == 12U,
    "linked-list descriptor size changed"
);
_Static_assert(
    __builtin_offsetof(struct open_cfw_runtime_linked_list, node_size)
        == 0U,
    "linked-list node-size offset changed"
);
_Static_assert(
    __builtin_offsetof(struct open_cfw_runtime_linked_list, head) == 4U,
    "linked-list head offset changed"
);
_Static_assert(
    __builtin_offsetof(struct open_cfw_runtime_linked_list, tail) == 8U,
    "linked-list tail offset changed"
);

__attribute__((used, noinline))
void open_cfw_runtime_linked_list_init(
    struct open_cfw_runtime_linked_list *list,
    open_cfw_runtime_linked_list_word node_size
)
{
    list->head = 0U;
    list->tail = 0U;
    list->node_size = (node_size + 3U) & ~3U;
}
