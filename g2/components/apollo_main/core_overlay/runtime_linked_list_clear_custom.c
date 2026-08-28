/*
 * SPDX-License-Identifier: MIT
 *
 * Source replacement for the G2 2.2.6.10 LVGL linked-list custom-clear
 * routine at 0x00482C9A...0x00482CD7. The next node is captured before
 * cleanup, removal, or deallocation so a cleanup callback may release or
 * unlink the current node without breaking traversal.
 */

typedef unsigned int open_cfw_runtime_linked_list_clear_custom_word;
typedef unsigned int open_cfw_runtime_linked_list_clear_custom_pointer;

struct open_cfw_runtime_linked_list_clear_custom_descriptor {
    open_cfw_runtime_linked_list_clear_custom_word node_size;
    open_cfw_runtime_linked_list_clear_custom_pointer head;
    open_cfw_runtime_linked_list_clear_custom_pointer tail;
};

_Static_assert(
    sizeof(open_cfw_runtime_linked_list_clear_custom_word) == 4U,
    "linked-list custom-clear word width changed"
);
_Static_assert(
    sizeof(open_cfw_runtime_linked_list_clear_custom_pointer) == 4U,
    "linked-list custom-clear pointer width changed"
);
_Static_assert(
    sizeof(
        struct open_cfw_runtime_linked_list_clear_custom_descriptor
    ) == 12U,
    "linked-list custom-clear descriptor size changed"
);

#ifndef OPEN_CFW_RUNTIME_LINKED_LIST_CLEAR_CUSTOM_GET_HEAD
typedef open_cfw_runtime_linked_list_clear_custom_pointer
(*open_cfw_runtime_linked_list_clear_custom_get_head_fn)(
    const struct open_cfw_runtime_linked_list_clear_custom_descriptor *
);
#define OPEN_CFW_RUNTIME_LINKED_LIST_CLEAR_CUSTOM_GET_HEAD(list) \
    (((open_cfw_runtime_linked_list_clear_custom_get_head_fn) \
        (__UINTPTR_TYPE__)0x00482CD9U)((list)))
#endif

#ifndef OPEN_CFW_RUNTIME_LINKED_LIST_CLEAR_CUSTOM_GET_NEXT
typedef open_cfw_runtime_linked_list_clear_custom_pointer
(*open_cfw_runtime_linked_list_clear_custom_get_next_fn)(
    const struct open_cfw_runtime_linked_list_clear_custom_descriptor *,
    open_cfw_runtime_linked_list_clear_custom_pointer
);
#define OPEN_CFW_RUNTIME_LINKED_LIST_CLEAR_CUSTOM_GET_NEXT(list, node) \
    (((open_cfw_runtime_linked_list_clear_custom_get_next_fn) \
        (__UINTPTR_TYPE__)0x00482CF1U)((list), (node)))
#endif

#ifndef OPEN_CFW_RUNTIME_LINKED_LIST_CLEAR_CUSTOM_REMOVE
typedef void (*open_cfw_runtime_linked_list_clear_custom_remove_fn)(
    struct open_cfw_runtime_linked_list_clear_custom_descriptor *,
    open_cfw_runtime_linked_list_clear_custom_pointer
);
#define OPEN_CFW_RUNTIME_LINKED_LIST_CLEAR_CUSTOM_REMOVE(list, node) \
    (((open_cfw_runtime_linked_list_clear_custom_remove_fn) \
        (__UINTPTR_TYPE__)0x00482C0FU)((list), (node)))
#endif

#ifndef OPEN_CFW_RUNTIME_LINKED_LIST_CLEAR_CUSTOM_FREE
typedef void (*open_cfw_runtime_linked_list_clear_custom_free_fn)(
    open_cfw_runtime_linked_list_clear_custom_pointer
);
#define OPEN_CFW_RUNTIME_LINKED_LIST_CLEAR_CUSTOM_FREE(node) \
    (((open_cfw_runtime_linked_list_clear_custom_free_fn) \
        (__UINTPTR_TYPE__)0x0044F759U)((node)))
#endif

#ifndef OPEN_CFW_RUNTIME_LINKED_LIST_CLEAR_CUSTOM_CALL_CLEANUP
typedef void (*open_cfw_runtime_linked_list_clear_custom_cleanup_fn)(
    open_cfw_runtime_linked_list_clear_custom_pointer
);
#define OPEN_CFW_RUNTIME_LINKED_LIST_CLEAR_CUSTOM_CALL_CLEANUP( \
    cleanup, \
    node \
) \
    (((open_cfw_runtime_linked_list_clear_custom_cleanup_fn) \
        (__UINTPTR_TYPE__)(cleanup))((node)))
#endif

__attribute__((used, noinline))
void open_cfw_runtime_linked_list_clear_custom(
    struct open_cfw_runtime_linked_list_clear_custom_descriptor *list,
    open_cfw_runtime_linked_list_clear_custom_pointer cleanup
)
{
    open_cfw_runtime_linked_list_clear_custom_pointer current;

    current = OPEN_CFW_RUNTIME_LINKED_LIST_CLEAR_CUSTOM_GET_HEAD(list);
    while (current != 0U) {
        open_cfw_runtime_linked_list_clear_custom_pointer next =
            OPEN_CFW_RUNTIME_LINKED_LIST_CLEAR_CUSTOM_GET_NEXT(
                list,
                current
            );

        if (cleanup == 0U) {
            OPEN_CFW_RUNTIME_LINKED_LIST_CLEAR_CUSTOM_REMOVE(
                list,
                current
            );
            OPEN_CFW_RUNTIME_LINKED_LIST_CLEAR_CUSTOM_FREE(current);
        } else {
            OPEN_CFW_RUNTIME_LINKED_LIST_CLEAR_CUSTOM_CALL_CLEANUP(
                cleanup,
                current
            );
        }
        current = next;
    }
}

#undef OPEN_CFW_RUNTIME_LINKED_LIST_CLEAR_CUSTOM_CALL_CLEANUP
#undef OPEN_CFW_RUNTIME_LINKED_LIST_CLEAR_CUSTOM_FREE
#undef OPEN_CFW_RUNTIME_LINKED_LIST_CLEAR_CUSTOM_REMOVE
#undef OPEN_CFW_RUNTIME_LINKED_LIST_CLEAR_CUSTOM_GET_NEXT
#undef OPEN_CFW_RUNTIME_LINKED_LIST_CLEAR_CUSTOM_GET_HEAD
