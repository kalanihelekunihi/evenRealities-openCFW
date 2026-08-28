/*
 * SPDX-License-Identifier: MIT
 *
 * Bounded source replacement for the G2 2.2.6.10 LVGL linked-list
 * move-before routine at 0x00482D22...0x00482D87.
 *
 * A null before-node denotes the position after the current tail. Moving a
 * node before itself, immediately before its current successor, or after
 * itself when it is already the tail is a no-op. The retained unlink and
 * link helpers preserve the stock mutation order.
 *
 * Machine ABI: r0 list, r1 moving node, r2 before node. The routine has no
 * meaningful return value. Its stock epilogue incidentally restores incoming
 * r3 into r0, and the sole caller ignores r0.
 */

typedef unsigned int open_cfw_runtime_linked_list_move_word;
typedef unsigned int open_cfw_runtime_linked_list_move_pointer;

struct open_cfw_runtime_linked_list_move_descriptor {
    open_cfw_runtime_linked_list_move_word node_size;
    open_cfw_runtime_linked_list_move_pointer head;
    open_cfw_runtime_linked_list_move_pointer tail;
};

_Static_assert(
    sizeof(struct open_cfw_runtime_linked_list_move_descriptor) == 12U,
    "linked-list move descriptor size changed"
);
_Static_assert(
    __builtin_offsetof(
        struct open_cfw_runtime_linked_list_move_descriptor,
        head
    ) == 4U,
    "linked-list move head offset changed"
);
_Static_assert(
    __builtin_offsetof(
        struct open_cfw_runtime_linked_list_move_descriptor,
        tail
    ) == 8U,
    "linked-list move tail offset changed"
);

#ifndef OPEN_CFW_RUNTIME_LINKED_LIST_MOVE_GET_TAIL
typedef open_cfw_runtime_linked_list_move_pointer
(*open_cfw_runtime_linked_list_move_get_tail_fn)(
    const struct open_cfw_runtime_linked_list_move_descriptor *
);
#define OPEN_CFW_RUNTIME_LINKED_LIST_MOVE_GET_TAIL(list) \
    (((open_cfw_runtime_linked_list_move_get_tail_fn) \
        (__UINTPTR_TYPE__)0x00482CE5U)((list)))
#endif

#ifndef OPEN_CFW_RUNTIME_LINKED_LIST_MOVE_GET_PREVIOUS
typedef open_cfw_runtime_linked_list_move_pointer
(*open_cfw_runtime_linked_list_move_get_previous_fn)(
    const struct open_cfw_runtime_linked_list_move_descriptor *,
    open_cfw_runtime_linked_list_move_pointer
);
#define OPEN_CFW_RUNTIME_LINKED_LIST_MOVE_GET_PREVIOUS(list, node) \
    (((open_cfw_runtime_linked_list_move_get_previous_fn) \
        (__UINTPTR_TYPE__)0x00482CFBU)((list), (node)))
#endif

#ifndef OPEN_CFW_RUNTIME_LINKED_LIST_MOVE_REMOVE
typedef void (*open_cfw_runtime_linked_list_move_remove_fn)(
    struct open_cfw_runtime_linked_list_move_descriptor *,
    open_cfw_runtime_linked_list_move_pointer
);
#define OPEN_CFW_RUNTIME_LINKED_LIST_MOVE_REMOVE(list, node) \
    (((open_cfw_runtime_linked_list_move_remove_fn) \
        (__UINTPTR_TYPE__)0x00482C0FU)((list), (node)))
#endif

#ifndef OPEN_CFW_RUNTIME_LINKED_LIST_MOVE_SET_PREVIOUS
typedef void (*open_cfw_runtime_linked_list_move_set_previous_fn)(
    struct open_cfw_runtime_linked_list_move_descriptor *,
    open_cfw_runtime_linked_list_move_pointer,
    open_cfw_runtime_linked_list_move_pointer
);
#define OPEN_CFW_RUNTIME_LINKED_LIST_MOVE_SET_PREVIOUS( \
    list, node, previous \
) \
    (((open_cfw_runtime_linked_list_move_set_previous_fn) \
        (__UINTPTR_TYPE__)0x00482DAFU)((list), (node), (previous)))
#endif

#ifndef OPEN_CFW_RUNTIME_LINKED_LIST_MOVE_SET_NEXT
typedef void (*open_cfw_runtime_linked_list_move_set_next_fn)(
    struct open_cfw_runtime_linked_list_move_descriptor *,
    open_cfw_runtime_linked_list_move_pointer,
    open_cfw_runtime_linked_list_move_pointer
);
#define OPEN_CFW_RUNTIME_LINKED_LIST_MOVE_SET_NEXT(list, node, next) \
    (((open_cfw_runtime_linked_list_move_set_next_fn) \
        (__UINTPTR_TYPE__)0x00482DC3U)((list), (node), (next)))
#endif

__attribute__((used, noinline))
void open_cfw_runtime_linked_list_move_before(
    struct open_cfw_runtime_linked_list_move_descriptor *list,
    open_cfw_runtime_linked_list_move_pointer moving,
    open_cfw_runtime_linked_list_move_pointer before
)
{
    open_cfw_runtime_linked_list_move_pointer previous;

    if (moving == before) {
        return;
    }

    if (before != 0U) {
        previous = OPEN_CFW_RUNTIME_LINKED_LIST_MOVE_GET_PREVIOUS(
            list,
            before
        );
    } else {
        previous = OPEN_CFW_RUNTIME_LINKED_LIST_MOVE_GET_TAIL(list);
    }
    if (moving == previous) {
        return;
    }

    OPEN_CFW_RUNTIME_LINKED_LIST_MOVE_REMOVE(list, moving);
    OPEN_CFW_RUNTIME_LINKED_LIST_MOVE_SET_NEXT(list, previous, moving);
    OPEN_CFW_RUNTIME_LINKED_LIST_MOVE_SET_PREVIOUS(
        list,
        moving,
        previous
    );
    OPEN_CFW_RUNTIME_LINKED_LIST_MOVE_SET_PREVIOUS(list, before, moving);
    OPEN_CFW_RUNTIME_LINKED_LIST_MOVE_SET_NEXT(list, moving, before);

    if (before == 0U) {
        list->tail = moving;
    }
    if (previous == 0U) {
        list->head = moving;
    }
}

#undef OPEN_CFW_RUNTIME_LINKED_LIST_MOVE_GET_TAIL
#undef OPEN_CFW_RUNTIME_LINKED_LIST_MOVE_GET_PREVIOUS
#undef OPEN_CFW_RUNTIME_LINKED_LIST_MOVE_REMOVE
#undef OPEN_CFW_RUNTIME_LINKED_LIST_MOVE_SET_PREVIOUS
#undef OPEN_CFW_RUNTIME_LINKED_LIST_MOVE_SET_NEXT
