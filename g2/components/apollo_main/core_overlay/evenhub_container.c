/*
 * SPDX-License-Identifier: MIT
 *
 * Bounded EvenHub container-lookup replacement for the Even Realities G2
 * 2.2.6.10 Apollo510B application. Exact stock boundaries, callers, RAM
 * state, diagnostics, and return behavior are recorded in EVIDENCE.md.
 */

struct open_cfw_evenhub_manager_view {
    void *page_root_obj;
    void *container_list_head;
};

typedef void *(*open_cfw_evenhub_find_node_fn)(
    void *manager,
    unsigned int foreground_id
);
typedef unsigned int (*open_cfw_evenhub_log_flags_fn)(void);
typedef void (*open_cfw_evenhub_log_record_fn)(
    unsigned int level,
    const void *module,
    const void *file,
    const void *tag,
    unsigned int line,
    const void *format,
    ...
);
typedef void (*open_cfw_evenhub_trace_record_fn)(
    unsigned int mask,
    const void *schema,
    const void *format,
    ...
);

#ifndef OPEN_CFW_EVENHUB_MANAGER_CONTEXT
#define OPEN_CFW_EVENHUB_MANAGER_CONTEXT \
    (*(struct open_cfw_evenhub_manager_view * volatile *)0x200745A8U)
#endif

#ifndef OPEN_CFW_EVENHUB_FIND_NODE
#define OPEN_CFW_EVENHUB_FIND_NODE(manager, foreground_id) \
    (((open_cfw_evenhub_find_node_fn)0x00493FA9U)( \
        (manager), \
        (foreground_id) \
    ))
#endif

#ifndef OPEN_CFW_EVENHUB_LOG_FLAGS
#define OPEN_CFW_EVENHUB_LOG_FLAGS \
    ((open_cfw_evenhub_log_flags_fn)0x0043D0CFU)
#endif

#ifndef OPEN_CFW_EVENHUB_LOG_RECORD
#define OPEN_CFW_EVENHUB_LOG_RECORD \
    ((open_cfw_evenhub_log_record_fn)0x0043D575U)
#endif

#ifndef OPEN_CFW_EVENHUB_TRACE_RECORD
#define OPEN_CFW_EVENHUB_TRACE_RECORD \
    ((open_cfw_evenhub_trace_record_fn)0x0043CE9FU)
#endif

#define OPEN_CFW_EVENHUB_LOG_MODULE ((const void *)0x00785E70U)
#define OPEN_CFW_EVENHUB_LOG_FILE ((const void *)0x00702988U)
#define OPEN_CFW_EVENHUB_LOG_TAG ((const void *)0x0075462CU)
#define OPEN_CFW_EVENHUB_CONTEXT_ERROR ((const void *)0x006D6128U)
#define OPEN_CFW_EVENHUB_CONTEXT_TRACE ((const void *)0x0077F400U)

/*
 * ABI-compatible source replacement for stock 0x004E0CCE...0x004E0D39.
 * Return the matching container node when all three manager-context anchors
 * exist. A missing manager, container-list head, or page-root object is the
 * stock nonfatal path: emit its gated diagnostics and return null.
 */
__attribute__((used, noinline))
void *open_cfw_evenhub_container_find_node_by_id(
    unsigned int foreground_id
)
{
    struct open_cfw_evenhub_manager_view *manager =
        OPEN_CFW_EVENHUB_MANAGER_CONTEXT;
    unsigned int flags;

    if (
        manager != (struct open_cfw_evenhub_manager_view *)0 &&
        manager->container_list_head != (void *)0 &&
        manager->page_root_obj != (void *)0
    ) {
        return OPEN_CFW_EVENHUB_FIND_NODE(manager, foreground_id);
    }

    flags = OPEN_CFW_EVENHUB_LOG_FLAGS();
    if (flags & 2U) {
        OPEN_CFW_EVENHUB_LOG_RECORD(
            1U,
            OPEN_CFW_EVENHUB_LOG_MODULE,
            OPEN_CFW_EVENHUB_LOG_FILE,
            OPEN_CFW_EVENHUB_LOG_TAG,
            0x65U,
            OPEN_CFW_EVENHUB_CONTEXT_ERROR
        );
    }
    flags = OPEN_CFW_EVENHUB_LOG_FLAGS();
    if ((flags & 1U) || (OPEN_CFW_EVENHUB_LOG_FLAGS() & 4U)) {
        OPEN_CFW_EVENHUB_TRACE_RECORD(
            0x04000000U,
            OPEN_CFW_EVENHUB_CONTEXT_TRACE,
            OPEN_CFW_EVENHUB_CONTEXT_TRACE
        );
    }
    return (void *)0;
}
