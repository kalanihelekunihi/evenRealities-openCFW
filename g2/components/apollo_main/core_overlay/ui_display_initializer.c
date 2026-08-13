/*
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * Display-subsystem initializer replacement for the Even Realities G2
 * 2.2.6.10 Apollo510B application. Exact stock boundaries, persistent SRAM
 * state, RTOS configuration records, and behavioral evidence are recorded in
 * EVIDENCE.md.
 */

typedef void (*open_cfw_ui_initializer_thread_entry_fn)(void *context);
typedef void *(*open_cfw_ui_initializer_void_result_fn)(void);
typedef void (*open_cfw_ui_initializer_void_fn)(void);
typedef void *(*open_cfw_ui_initializer_queue_create_fn)(
    unsigned int storage_size,
    unsigned int item_size,
    const void *configuration
);
typedef unsigned int (*open_cfw_ui_initializer_ring_init_fn)(
    void *descriptor,
    void *storage,
    unsigned int capacity
);
typedef void *(*open_cfw_ui_initializer_mutex_create_fn)(
    unsigned int attributes
);
typedef void (*open_cfw_ui_initializer_thread_register_fn)(
    open_cfw_ui_initializer_thread_entry_fn entry,
    void *context,
    const void *configuration
);
typedef unsigned int (*open_cfw_ui_initializer_log_flags_fn)(void);
typedef void (*open_cfw_ui_initializer_log_record_fn)(
    unsigned int level,
    const void *module,
    const void *file,
    const void *tag,
    unsigned int line,
    const void *format,
    ...
);
typedef void (*open_cfw_ui_initializer_trace_record_fn)(
    unsigned int mask,
    const void *schema,
    const void *format,
    ...
);

extern void open_cfw_ui_display_thread(void *context);
extern void open_cfw_ui_prepare_display(void);
extern void open_cfw_ui_prepare_input(void);

#ifndef OPEN_CFW_UI_INITIALIZER_DRIVER
#define OPEN_CFW_UI_INITIALIZER_DRIVER \
    (*(void * volatile *)0x200744CCU)
#endif

#ifndef OPEN_CFW_UI_INITIALIZER_QUEUE
#define OPEN_CFW_UI_INITIALIZER_QUEUE \
    (*(void * volatile *)0x200744E4U)
#endif

#ifndef OPEN_CFW_UI_INITIALIZER_MUTEX
#define OPEN_CFW_UI_INITIALIZER_MUTEX \
    (*(void * volatile *)0x200744E8U)
#endif

#ifndef OPEN_CFW_UI_INITIALIZER_RING_DESCRIPTOR
#define OPEN_CFW_UI_INITIALIZER_RING_DESCRIPTOR ((void *)0x20073B60U)
#endif

#ifndef OPEN_CFW_UI_INITIALIZER_RING_STORAGE
#define OPEN_CFW_UI_INITIALIZER_RING_STORAGE ((void *)0x200E99B4U)
#endif

#ifndef OPEN_CFW_UI_INITIALIZER_GET_DRIVER
#define OPEN_CFW_UI_INITIALIZER_GET_DRIVER() \
    (((open_cfw_ui_initializer_void_result_fn)0x0047394DU)())
#endif

#ifndef OPEN_CFW_UI_INITIALIZER_PREPARE_DISPLAY
#define OPEN_CFW_UI_INITIALIZER_PREPARE_DISPLAY() \
    open_cfw_ui_prepare_display()
#endif

#ifndef OPEN_CFW_UI_INITIALIZER_PREPARE_INPUT
#define OPEN_CFW_UI_INITIALIZER_PREPARE_INPUT() \
    open_cfw_ui_prepare_input()
#endif

#ifndef OPEN_CFW_UI_INITIALIZER_QUEUE_CREATE
#define OPEN_CFW_UI_INITIALIZER_QUEUE_CREATE( \
    storage_size, \
    item_size, \
    configuration \
) \
    (((open_cfw_ui_initializer_queue_create_fn)0x00449A33U)( \
        (storage_size), \
        (item_size), \
        (configuration) \
    ))
#endif

#ifndef OPEN_CFW_UI_INITIALIZER_RING_INITIALIZE
#define OPEN_CFW_UI_INITIALIZER_RING_INITIALIZE( \
    descriptor, \
    storage, \
    capacity \
) \
    (((open_cfw_ui_initializer_ring_init_fn)0x0046D8A1U)( \
        (descriptor), \
        (storage), \
        (capacity) \
    ))
#endif

#ifndef OPEN_CFW_UI_INITIALIZER_MUTEX_CREATE
#define OPEN_CFW_UI_INITIALIZER_MUTEX_CREATE(attributes) \
    (((open_cfw_ui_initializer_mutex_create_fn)0x0044971DU)(attributes))
#endif

#ifndef OPEN_CFW_UI_INITIALIZER_REGISTER_THREAD
#define OPEN_CFW_UI_INITIALIZER_REGISTER_THREAD( \
    entry, \
    context, \
    configuration \
) \
    (((open_cfw_ui_initializer_thread_register_fn)0x004490E3U)( \
        (entry), \
        (context), \
        (configuration) \
    ))
#endif

#ifndef OPEN_CFW_UI_INITIALIZER_LOG_FLAGS
#define OPEN_CFW_UI_INITIALIZER_LOG_FLAGS \
    ((open_cfw_ui_initializer_log_flags_fn)0x0043D0CFU)
#endif

#ifndef OPEN_CFW_UI_INITIALIZER_LOG_RECORD
#define OPEN_CFW_UI_INITIALIZER_LOG_RECORD \
    ((open_cfw_ui_initializer_log_record_fn)0x0043D575U)
#endif

#ifndef OPEN_CFW_UI_INITIALIZER_TRACE_RECORD
#define OPEN_CFW_UI_INITIALIZER_TRACE_RECORD \
    ((open_cfw_ui_initializer_trace_record_fn)0x0043CE9FU)
#endif

#define OPEN_CFW_UI_INITIALIZER_LOG_MODULE ((const void *)0x00785AA0U)
#define OPEN_CFW_UI_INITIALIZER_LOG_FILE ((const void *)0x00701FB4U)
#define OPEN_CFW_UI_INITIALIZER_LOG_TAG ((const void *)0x0076AE70U)

#define OPEN_CFW_UI_INITIALIZER_QUEUE_FORMAT ((const void *)0x00753720U)
#define OPEN_CFW_UI_INITIALIZER_QUEUE_TRACE ((const void *)0x00728A60U)
#define OPEN_CFW_UI_INITIALIZER_RING_FORMAT ((const void *)0x0077ED84U)
#define OPEN_CFW_UI_INITIALIZER_RING_TRACE ((const void *)0x00753744U)
#define OPEN_CFW_UI_INITIALIZER_MUTEX_FORMAT ((const void *)0x00753768U)
#define OPEN_CFW_UI_INITIALIZER_MUTEX_TRACE ((const void *)0x00728A94U)

struct open_cfw_ui_initializer_queue_configuration {
    unsigned int words[6];
};

struct open_cfw_ui_initializer_thread_configuration {
    unsigned int words[9];
};

static inline __attribute__((always_inline))
unsigned int open_cfw_ui_initializer_trace_enabled(void)
{
    unsigned int flags = OPEN_CFW_UI_INITIALIZER_LOG_FLAGS();

    if (flags & 1U) {
        return 1U;
    }
    return (OPEN_CFW_UI_INITIALIZER_LOG_FLAGS() & 4U) != 0U;
}

static inline __attribute__((always_inline))
void open_cfw_ui_initializer_diag(
    unsigned int level,
    unsigned int line,
    const void *format,
    unsigned int mask,
    const void *trace
)
{
    if (OPEN_CFW_UI_INITIALIZER_LOG_FLAGS() & 2U) {
        OPEN_CFW_UI_INITIALIZER_LOG_RECORD(
            level,
            OPEN_CFW_UI_INITIALIZER_LOG_MODULE,
            OPEN_CFW_UI_INITIALIZER_LOG_FILE,
            OPEN_CFW_UI_INITIALIZER_LOG_TAG,
            line,
            format
        );
    }
    if (open_cfw_ui_initializer_trace_enabled()) {
        OPEN_CFW_UI_INITIALIZER_TRACE_RECORD(mask, trace, trace);
    }
}

static inline __attribute__((always_inline))
void open_cfw_ui_initializer_set_queue_configuration(
    struct open_cfw_ui_initializer_queue_configuration *configuration
)
{
    configuration->words[0] = 0x0078A7FCU;
    configuration->words[1] = 0U;
    configuration->words[2] = 0x200729E8U;
    configuration->words[3] = 0x50U;
    configuration->words[4] = 0x203780C0U;
    configuration->words[5] = 0x480U;
}

static inline __attribute__((always_inline))
void open_cfw_ui_initializer_set_thread_configuration(
    struct open_cfw_ui_initializer_thread_configuration *configuration
)
{
    configuration->words[0] = 0x0078D3E4U;
    configuration->words[1] = 0U;
    configuration->words[2] = 0U;
    configuration->words[3] = 0U;
    configuration->words[4] = 0U;
    configuration->words[5] = 0xC000U;
    configuration->words[6] = 0x2CU;
    configuration->words[7] = 0U;
    configuration->words[8] = 0U;
}

/*
 * Stock ABI at 0x00444720:
 *   no arguments; r0 is zero on success or 0xFFFFFFFF on a queue, ring, or
 *   mutex creation failure.
 *
 * The stock function does not release an already-created queue when ring
 * initialization fails, nor the queue/ring when mutex creation fails. That
 * ownership edge is retained exactly.
 */
__attribute__((used, noinline))
unsigned int open_cfw_ui_display_initialize(void)
{
    struct open_cfw_ui_initializer_queue_configuration queue_configuration;
    struct open_cfw_ui_initializer_thread_configuration thread_configuration;

    OPEN_CFW_UI_INITIALIZER_DRIVER = OPEN_CFW_UI_INITIALIZER_GET_DRIVER();
    OPEN_CFW_UI_INITIALIZER_PREPARE_DISPLAY();
    OPEN_CFW_UI_INITIALIZER_PREPARE_INPUT();

    open_cfw_ui_initializer_set_queue_configuration(&queue_configuration);
    OPEN_CFW_UI_INITIALIZER_QUEUE = OPEN_CFW_UI_INITIALIZER_QUEUE_CREATE(
        0x60U,
        0x0CU,
        &queue_configuration
    );
    if (OPEN_CFW_UI_INITIALIZER_QUEUE == (void *)0) {
        open_cfw_ui_initializer_diag(
            2U,
            0x43EU,
            OPEN_CFW_UI_INITIALIZER_QUEUE_FORMAT,
            0x08000000U,
            OPEN_CFW_UI_INITIALIZER_QUEUE_TRACE
        );
        return 0xFFFFFFFFU;
    }

    if (
        OPEN_CFW_UI_INITIALIZER_RING_INITIALIZE(
            OPEN_CFW_UI_INITIALIZER_RING_DESCRIPTOR,
            OPEN_CFW_UI_INITIALIZER_RING_STORAGE,
            0xA000U
        ) != 1U
    ) {
        open_cfw_ui_initializer_diag(
            2U,
            0x444U,
            OPEN_CFW_UI_INITIALIZER_RING_FORMAT,
            0x08000000U,
            OPEN_CFW_UI_INITIALIZER_RING_TRACE
        );
        return 0xFFFFFFFFU;
    }

    OPEN_CFW_UI_INITIALIZER_MUTEX =
        OPEN_CFW_UI_INITIALIZER_MUTEX_CREATE(0U);
    if (OPEN_CFW_UI_INITIALIZER_MUTEX == (void *)0) {
        open_cfw_ui_initializer_diag(
            1U,
            0x44AU,
            OPEN_CFW_UI_INITIALIZER_MUTEX_FORMAT,
            0x04000000U,
            OPEN_CFW_UI_INITIALIZER_MUTEX_TRACE
        );
        return 0xFFFFFFFFU;
    }

    open_cfw_ui_initializer_set_thread_configuration(
        &thread_configuration
    );
    OPEN_CFW_UI_INITIALIZER_REGISTER_THREAD(
        open_cfw_ui_display_thread,
        (void *)0,
        &thread_configuration
    );
    return 0U;
}
