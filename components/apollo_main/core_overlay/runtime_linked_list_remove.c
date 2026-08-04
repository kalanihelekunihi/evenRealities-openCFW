/*
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * Bounded source replacement for the G2 2.2.6.10 LVGL linked-list removal
 * routine at 0x00482C0E...0x00482C99.
 *
 * The node payload is followed by its previous pointer and then its next
 * pointer. Removal updates the descriptor or neighboring links but does not
 * clear either link stored in the removed node. The routine intentionally
 * performs no membership or null-node validation.
 *
 * Machine ABI: r0 list and r1 node. There is no meaningful return value.
 * Stock leaves branch-dependent helper scratch values in r0, and all 18
 * direct callers discard or pass that value to a no-argument callee.
 */

typedef unsigned int open_cfw_runtime_linked_list_remove_word;
typedef unsigned int open_cfw_runtime_linked_list_remove_pointer;

struct open_cfw_runtime_linked_list_remove_descriptor {
    open_cfw_runtime_linked_list_remove_word node_size;
    open_cfw_runtime_linked_list_remove_pointer head;
    open_cfw_runtime_linked_list_remove_pointer tail;
};

_Static_assert(
    sizeof(struct open_cfw_runtime_linked_list_remove_descriptor) == 12U,
    "linked-list remove descriptor size changed"
);
_Static_assert(
    __builtin_offsetof(
        struct open_cfw_runtime_linked_list_remove_descriptor,
        head
    ) == 4U,
    "linked-list remove head offset changed"
);
_Static_assert(
    __builtin_offsetof(
        struct open_cfw_runtime_linked_list_remove_descriptor,
        tail
    ) == 8U,
    "linked-list remove tail offset changed"
);

#ifndef OPEN_CFW_RUNTIME_LINKED_LIST_REMOVE_GET_HEAD
typedef open_cfw_runtime_linked_list_remove_pointer
(*open_cfw_runtime_linked_list_remove_get_head_fn)(
    const struct open_cfw_runtime_linked_list_remove_descriptor *
);
#define OPEN_CFW_RUNTIME_LINKED_LIST_REMOVE_GET_HEAD(list) \
    (((open_cfw_runtime_linked_list_remove_get_head_fn) \
        (__UINTPTR_TYPE__)0x00482CD9U)((list)))
#endif

#ifndef OPEN_CFW_RUNTIME_LINKED_LIST_REMOVE_GET_TAIL
typedef open_cfw_runtime_linked_list_remove_pointer
(*open_cfw_runtime_linked_list_remove_get_tail_fn)(
    const struct open_cfw_runtime_linked_list_remove_descriptor *
);
#define OPEN_CFW_RUNTIME_LINKED_LIST_REMOVE_GET_TAIL(list) \
    (((open_cfw_runtime_linked_list_remove_get_tail_fn) \
        (__UINTPTR_TYPE__)0x00482CE5U)((list)))
#endif

#ifndef OPEN_CFW_RUNTIME_LINKED_LIST_REMOVE_GET_NEXT
typedef open_cfw_runtime_linked_list_remove_pointer
(*open_cfw_runtime_linked_list_remove_get_next_fn)(
    const struct open_cfw_runtime_linked_list_remove_descriptor *,
    open_cfw_runtime_linked_list_remove_pointer
);
#define OPEN_CFW_RUNTIME_LINKED_LIST_REMOVE_GET_NEXT(list, node) \
    (((open_cfw_runtime_linked_list_remove_get_next_fn) \
        (__UINTPTR_TYPE__)0x00482CF1U)((list), (node)))
#endif

#ifndef OPEN_CFW_RUNTIME_LINKED_LIST_REMOVE_GET_PREVIOUS
typedef open_cfw_runtime_linked_list_remove_pointer
(*open_cfw_runtime_linked_list_remove_get_previous_fn)(
    const struct open_cfw_runtime_linked_list_remove_descriptor *,
    open_cfw_runtime_linked_list_remove_pointer
);
#define OPEN_CFW_RUNTIME_LINKED_LIST_REMOVE_GET_PREVIOUS(list, node) \
    (((open_cfw_runtime_linked_list_remove_get_previous_fn) \
        (__UINTPTR_TYPE__)0x00482CFBU)((list), (node)))
#endif

#ifndef OPEN_CFW_RUNTIME_LINKED_LIST_REMOVE_SET_PREVIOUS
typedef void (*open_cfw_runtime_linked_list_remove_set_previous_fn)(
    struct open_cfw_runtime_linked_list_remove_descriptor *,
    open_cfw_runtime_linked_list_remove_pointer,
    open_cfw_runtime_linked_list_remove_pointer
);
#define OPEN_CFW_RUNTIME_LINKED_LIST_REMOVE_SET_PREVIOUS( \
    list, node, previous \
) \
    (((open_cfw_runtime_linked_list_remove_set_previous_fn) \
        (__UINTPTR_TYPE__)0x00482DAFU)((list), (node), (previous)))
#endif

#ifndef OPEN_CFW_RUNTIME_LINKED_LIST_REMOVE_SET_NEXT
typedef void (*open_cfw_runtime_linked_list_remove_set_next_fn)(
    struct open_cfw_runtime_linked_list_remove_descriptor *,
    open_cfw_runtime_linked_list_remove_pointer,
    open_cfw_runtime_linked_list_remove_pointer
);
#define OPEN_CFW_RUNTIME_LINKED_LIST_REMOVE_SET_NEXT(list, node, next) \
    (((open_cfw_runtime_linked_list_remove_set_next_fn) \
        (__UINTPTR_TYPE__)0x00482DC3U)((list), (node), (next)))
#endif

__attribute__((used, noinline))
void open_cfw_runtime_linked_list_remove(
    struct open_cfw_runtime_linked_list_remove_descriptor *list,
    open_cfw_runtime_linked_list_remove_pointer node
)
{
    open_cfw_runtime_linked_list_remove_pointer previous;
    open_cfw_runtime_linked_list_remove_pointer next;

    if (
        list
        == (struct open_cfw_runtime_linked_list_remove_descriptor *)0
    ) {
        return;
    }

    if (OPEN_CFW_RUNTIME_LINKED_LIST_REMOVE_GET_HEAD(list) == node) {
        list->head = OPEN_CFW_RUNTIME_LINKED_LIST_REMOVE_GET_NEXT(
            list,
            node
        );
        if (list->head == 0U) {
            list->tail = 0U;
        } else {
            OPEN_CFW_RUNTIME_LINKED_LIST_REMOVE_SET_PREVIOUS(
                list,
                list->head,
                0U
            );
        }
        return;
    }

    if (OPEN_CFW_RUNTIME_LINKED_LIST_REMOVE_GET_TAIL(list) == node) {
        list->tail = OPEN_CFW_RUNTIME_LINKED_LIST_REMOVE_GET_PREVIOUS(
            list,
            node
        );
        if (list->tail == 0U) {
            list->head = 0U;
        } else {
            OPEN_CFW_RUNTIME_LINKED_LIST_REMOVE_SET_NEXT(
                list,
                list->tail,
                0U
            );
        }
        return;
    }

    previous = OPEN_CFW_RUNTIME_LINKED_LIST_REMOVE_GET_PREVIOUS(
        list,
        node
    );
    next = OPEN_CFW_RUNTIME_LINKED_LIST_REMOVE_GET_NEXT(list, node);
    OPEN_CFW_RUNTIME_LINKED_LIST_REMOVE_SET_NEXT(list, previous, next);
    OPEN_CFW_RUNTIME_LINKED_LIST_REMOVE_SET_PREVIOUS(
        list,
        next,
        previous
    );
}

#undef OPEN_CFW_RUNTIME_LINKED_LIST_REMOVE_GET_HEAD
#undef OPEN_CFW_RUNTIME_LINKED_LIST_REMOVE_GET_TAIL
#undef OPEN_CFW_RUNTIME_LINKED_LIST_REMOVE_GET_NEXT
#undef OPEN_CFW_RUNTIME_LINKED_LIST_REMOVE_GET_PREVIOUS
#undef OPEN_CFW_RUNTIME_LINKED_LIST_REMOVE_SET_PREVIOUS
#undef OPEN_CFW_RUNTIME_LINKED_LIST_REMOVE_SET_NEXT
