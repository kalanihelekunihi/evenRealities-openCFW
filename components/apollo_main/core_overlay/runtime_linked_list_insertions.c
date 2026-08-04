/*
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * Bounded source replacements for the G2 2.2.6.10 LVGL linked-list
 * insertion cluster at 0x00482B12...0x00482C0D:
 *
 *   0x00482B12...0x00482B55  insert a newly allocated head
 *   0x00482B56...0x00482BC9  insert a newly allocated node before one
 *   0x00482BCA...0x00482C0D  insert a newly allocated tail
 *
 * Each node allocation contains the rounded payload followed by two
 * 32-bit metadata pointers: previous at payload_size and next at
 * payload_size + 4. The three public functions remain distinct noinline
 * symbols so their stock entries can be redirected independently.
 */

typedef unsigned int open_cfw_runtime_linked_list_insert_word;
typedef unsigned int open_cfw_runtime_linked_list_insert_pointer;

struct open_cfw_runtime_linked_list_insert_descriptor {
    open_cfw_runtime_linked_list_insert_word node_size;
    open_cfw_runtime_linked_list_insert_pointer head;
    open_cfw_runtime_linked_list_insert_pointer tail;
};

_Static_assert(
    sizeof(open_cfw_runtime_linked_list_insert_word) == 4U,
    "linked-list insertion word width changed"
);
_Static_assert(
    sizeof(open_cfw_runtime_linked_list_insert_pointer) == 4U,
    "linked-list insertion pointer width changed"
);
_Static_assert(
    sizeof(struct open_cfw_runtime_linked_list_insert_descriptor) == 12U,
    "linked-list insertion descriptor size changed"
);
_Static_assert(
    __builtin_offsetof(
        struct open_cfw_runtime_linked_list_insert_descriptor,
        node_size
    ) == 0U,
    "linked-list insertion node-size offset changed"
);
_Static_assert(
    __builtin_offsetof(
        struct open_cfw_runtime_linked_list_insert_descriptor,
        head
    ) == 4U,
    "linked-list insertion head offset changed"
);
_Static_assert(
    __builtin_offsetof(
        struct open_cfw_runtime_linked_list_insert_descriptor,
        tail
    ) == 8U,
    "linked-list insertion tail offset changed"
);

#ifndef OPEN_CFW_RUNTIME_LINKED_LIST_INSERT_ALLOCATE
#define OPEN_CFW_RUNTIME_LINKED_LIST_INSERT_ALLOCATE(size) \
    ((open_cfw_runtime_linked_list_insert_pointer)(__UINTPTR_TYPE__) \
        (((void *(*)(unsigned int))0x0044F719U)((size))))
#endif

#ifndef OPEN_CFW_RUNTIME_LINKED_LIST_INSERT_GET_HEAD
#define OPEN_CFW_RUNTIME_LINKED_LIST_INSERT_GET_HEAD(list) \
    ((open_cfw_runtime_linked_list_insert_pointer)(__UINTPTR_TYPE__) \
        (((void *(*)(const void *))0x00482CD9U)((list))))
#endif

#ifndef OPEN_CFW_RUNTIME_LINKED_LIST_INSERT_GET_PREVIOUS
#define OPEN_CFW_RUNTIME_LINKED_LIST_INSERT_GET_PREVIOUS(list, node) \
    ((open_cfw_runtime_linked_list_insert_pointer)(__UINTPTR_TYPE__) \
        (((void *(*)(const void *, void *))0x00482CFBU)( \
            (list), \
            (void *)(__UINTPTR_TYPE__)(node) \
        )))
#endif

#ifndef OPEN_CFW_RUNTIME_LINKED_LIST_INSERT_SET_PREVIOUS
#define OPEN_CFW_RUNTIME_LINKED_LIST_INSERT_SET_PREVIOUS( \
    list, node, previous \
) \
    (((void (*)(const void *, void *, void *))0x00482DAFU)( \
        (list), \
        (void *)(__UINTPTR_TYPE__)(node), \
        (void *)(__UINTPTR_TYPE__)(previous) \
    ))
#endif

#ifndef OPEN_CFW_RUNTIME_LINKED_LIST_INSERT_SET_NEXT
#define OPEN_CFW_RUNTIME_LINKED_LIST_INSERT_SET_NEXT(list, node, next) \
    (((void (*)(const void *, void *, void *))0x00482DC3U)( \
        (list), \
        (void *)(__UINTPTR_TYPE__)(node), \
        (void *)(__UINTPTR_TYPE__)(next) \
    ))
#endif

__attribute__((used, noinline))
open_cfw_runtime_linked_list_insert_pointer
open_cfw_runtime_linked_list_insert_head(
    struct open_cfw_runtime_linked_list_insert_descriptor *list
)
{
    open_cfw_runtime_linked_list_insert_pointer new_node;

    new_node = OPEN_CFW_RUNTIME_LINKED_LIST_INSERT_ALLOCATE(
        list->node_size + 8U
    );
    if (new_node != 0U) {
        OPEN_CFW_RUNTIME_LINKED_LIST_INSERT_SET_PREVIOUS(
            list,
            new_node,
            0U
        );
        OPEN_CFW_RUNTIME_LINKED_LIST_INSERT_SET_NEXT(
            list,
            new_node,
            list->head
        );
        if (list->head != 0U) {
            OPEN_CFW_RUNTIME_LINKED_LIST_INSERT_SET_PREVIOUS(
                list,
                list->head,
                new_node
            );
        }
        list->head = new_node;
        if (list->tail == 0U) {
            list->tail = new_node;
        }
    }
    return new_node;
}

#ifndef OPEN_CFW_RUNTIME_LINKED_LIST_INSERT_HEAD
#define OPEN_CFW_RUNTIME_LINKED_LIST_INSERT_HEAD(list) \
    open_cfw_runtime_linked_list_insert_head((list))
#endif

__attribute__((used, noinline))
open_cfw_runtime_linked_list_insert_pointer
open_cfw_runtime_linked_list_insert_before(
    struct open_cfw_runtime_linked_list_insert_descriptor *list,
    open_cfw_runtime_linked_list_insert_pointer active
)
{
    open_cfw_runtime_linked_list_insert_pointer new_node;
    open_cfw_runtime_linked_list_insert_pointer previous;

    if (
        list
            == (struct open_cfw_runtime_linked_list_insert_descriptor *)0
        || active == 0U
    ) {
        return 0U;
    }

    if (OPEN_CFW_RUNTIME_LINKED_LIST_INSERT_GET_HEAD(list) == active) {
        new_node = OPEN_CFW_RUNTIME_LINKED_LIST_INSERT_HEAD(list);
        if (new_node == 0U) {
            return 0U;
        }
    }
    else {
        new_node = OPEN_CFW_RUNTIME_LINKED_LIST_INSERT_ALLOCATE(
            list->node_size + 8U
        );
        if (new_node == 0U) {
            return 0U;
        }

        previous = OPEN_CFW_RUNTIME_LINKED_LIST_INSERT_GET_PREVIOUS(
            list,
            active
        );
        OPEN_CFW_RUNTIME_LINKED_LIST_INSERT_SET_NEXT(
            list,
            previous,
            new_node
        );
        OPEN_CFW_RUNTIME_LINKED_LIST_INSERT_SET_PREVIOUS(
            list,
            new_node,
            previous
        );
        OPEN_CFW_RUNTIME_LINKED_LIST_INSERT_SET_PREVIOUS(
            list,
            active,
            new_node
        );
        OPEN_CFW_RUNTIME_LINKED_LIST_INSERT_SET_NEXT(
            list,
            new_node,
            active
        );
    }

    return new_node;
}

__attribute__((used, noinline))
open_cfw_runtime_linked_list_insert_pointer
open_cfw_runtime_linked_list_insert_tail(
    struct open_cfw_runtime_linked_list_insert_descriptor *list
)
{
    open_cfw_runtime_linked_list_insert_pointer new_node;

    new_node = OPEN_CFW_RUNTIME_LINKED_LIST_INSERT_ALLOCATE(
        list->node_size + 8U
    );
    if (new_node != 0U) {
        OPEN_CFW_RUNTIME_LINKED_LIST_INSERT_SET_NEXT(
            list,
            new_node,
            0U
        );
        OPEN_CFW_RUNTIME_LINKED_LIST_INSERT_SET_PREVIOUS(
            list,
            new_node,
            list->tail
        );
        if (list->tail != 0U) {
            OPEN_CFW_RUNTIME_LINKED_LIST_INSERT_SET_NEXT(
                list,
                list->tail,
                new_node
            );
        }
        list->tail = new_node;
        if (list->head == 0U) {
            list->head = new_node;
        }
    }
    return new_node;
}

#undef OPEN_CFW_RUNTIME_LINKED_LIST_INSERT_ALLOCATE
#undef OPEN_CFW_RUNTIME_LINKED_LIST_INSERT_GET_HEAD
#undef OPEN_CFW_RUNTIME_LINKED_LIST_INSERT_GET_PREVIOUS
#undef OPEN_CFW_RUNTIME_LINKED_LIST_INSERT_SET_PREVIOUS
#undef OPEN_CFW_RUNTIME_LINKED_LIST_INSERT_SET_NEXT
#undef OPEN_CFW_RUNTIME_LINKED_LIST_INSERT_HEAD
