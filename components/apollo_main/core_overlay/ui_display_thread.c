/*
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * Main display-thread replacement for the Even Realities G2 2.2.6.10
 * Apollo510B application. Exact stock boundaries, RTOS registration,
 * persistent SRAM state, and behavioral evidence are recorded in EVIDENCE.md.
 */

typedef unsigned long open_cfw_ui_thread_uintptr;
typedef void *(*open_cfw_ui_thread_fill_fn)(
    void *destination,
    unsigned int length,
    unsigned int value
);
typedef int (*open_cfw_ui_thread_receive_fn)(
    void *queue,
    void *message,
    unsigned int wait_mode,
    unsigned int control,
    unsigned int reserved
);
typedef void (*open_cfw_ui_thread_mutex_fn)(
    void *mutex,
    unsigned int timeout
);
typedef void (*open_cfw_ui_thread_extract_fn)(
    void *descriptor,
    void *destination,
    unsigned int token
);
typedef void (*open_cfw_ui_thread_void_fn)(void);
typedef void (*open_cfw_ui_thread_value_fn)(unsigned int value);
typedef void *(*open_cfw_ui_thread_manager_create_fn)(void);
typedef unsigned int (*open_cfw_ui_thread_manager_open_fn)(
    void *manager,
    unsigned int operation,
    unsigned int service_id
);
typedef void (*open_cfw_ui_thread_manager_destroy_fn)(void *manager);
typedef unsigned int (*open_cfw_ui_thread_log_flags_fn)(void);
typedef void (*open_cfw_ui_thread_log_record_fn)(
    unsigned int level,
    const void *module,
    const void *file,
    const void *tag,
    unsigned int line,
    const void *format,
    ...
);
typedef void (*open_cfw_ui_thread_trace_record_fn)(
    unsigned int mask,
    const void *schema,
    const void *format,
    ...
);

extern unsigned int open_cfw_ui_module_dispatch_event(
    unsigned int service_id,
    unsigned int event,
    unsigned int arg1,
    unsigned int arg2
);
extern unsigned int open_cfw_ui_modules_close_mode1(
    unsigned int event,
    unsigned int excluded_state_id,
    unsigned int unused_arg2,
    unsigned int unused_arg3
);
extern void open_cfw_ui_modules_initialize(void);
extern unsigned int open_cfw_ui_switch_display(
    unsigned int target_service,
    unsigned int transition_arg1,
    unsigned int transition_arg2
);
extern unsigned int open_cfw_ui_input_event_handler(
    const unsigned char *record
);

#ifndef OPEN_CFW_UI_THREAD_DRIVER
#define OPEN_CFW_UI_THREAD_DRIVER \
    (*(void * volatile *)0x200744CCU)
#endif

#ifndef OPEN_CFW_UI_THREAD_MANAGER
#define OPEN_CFW_UI_THREAD_MANAGER \
    (*(void * volatile *)0x200744D0U)
#endif

#ifndef OPEN_CFW_UI_THREAD_BACKGROUND_SERVICE
#define OPEN_CFW_UI_THREAD_BACKGROUND_SERVICE \
    (*(volatile unsigned int *)0x200744D8U)
#endif

#ifndef OPEN_CFW_UI_THREAD_DISPLAY_MODE
#define OPEN_CFW_UI_THREAD_DISPLAY_MODE \
    (*(volatile unsigned int *)0x200744DCU)
#endif

#ifndef OPEN_CFW_UI_THREAD_FOREGROUND_SERVICE
#define OPEN_CFW_UI_THREAD_FOREGROUND_SERVICE \
    (*(volatile unsigned int *)0x200744E0U)
#endif

#ifndef OPEN_CFW_UI_THREAD_QUEUE
#define OPEN_CFW_UI_THREAD_QUEUE \
    (*(void * volatile *)0x200744E4U)
#endif

#ifndef OPEN_CFW_UI_THREAD_MUTEX
#define OPEN_CFW_UI_THREAD_MUTEX \
    (*(void * volatile *)0x200744E8U)
#endif

#ifndef OPEN_CFW_UI_THREAD_STATE
#define OPEN_CFW_UI_THREAD_STATE \
    (*(volatile unsigned char *)0x20074F2CU)
#endif

#ifndef OPEN_CFW_UI_THREAD_CONTROL
#define OPEN_CFW_UI_THREAD_CONTROL \
    (*(volatile unsigned int *)0x20000654U)
#endif

#ifndef OPEN_CFW_UI_THREAD_MESSAGE
#define OPEN_CFW_UI_THREAD_MESSAGE \
    ((unsigned char *)0x20073FCCU)
#endif

#ifndef OPEN_CFW_UI_THREAD_INPUT_BUFFER
#define OPEN_CFW_UI_THREAD_INPUT_BUFFER \
    ((unsigned char *)0x2034DC30U)
#endif

#ifndef OPEN_CFW_UI_THREAD_DRIVER_READY
#define OPEN_CFW_UI_THREAD_DRIVER_READY(driver) \
    (*(const volatile unsigned char *)(driver))
#endif

#ifndef OPEN_CFW_UI_THREAD_DRIVER_CALL
#define OPEN_CFW_UI_THREAD_DRIVER_CALL(driver, offset) \
    (((open_cfw_ui_thread_void_fn)(open_cfw_ui_thread_uintptr)( \
        *(const volatile unsigned int *)( \
            (open_cfw_ui_thread_uintptr)(driver) + (offset) \
        ) \
    ))())
#endif

#ifndef OPEN_CFW_UI_THREAD_FILL
#define OPEN_CFW_UI_THREAD_FILL(destination, length, value) \
    (((open_cfw_ui_thread_fill_fn)0x0043C0E5U)( \
        (destination), \
        (length), \
        (value) \
    ))
#endif

#ifndef OPEN_CFW_UI_THREAD_RECEIVE
#define OPEN_CFW_UI_THREAD_RECEIVE(queue, message, control) \
    (((open_cfw_ui_thread_receive_fn)0x00449B3DU)( \
        (queue), \
        (message), \
        0U, \
        (control), \
        0U \
    ))
#endif

#ifndef OPEN_CFW_UI_THREAD_MUTEX_TAKE
#define OPEN_CFW_UI_THREAD_MUTEX_TAKE(mutex) \
    (((open_cfw_ui_thread_mutex_fn)0x004497B7U)((mutex), 0xFFFFFFFFU))
#endif

#ifndef OPEN_CFW_UI_THREAD_MUTEX_GIVE
#define OPEN_CFW_UI_THREAD_MUTEX_GIVE(mutex) \
    (((open_cfw_ui_thread_value_fn)0x0044981DU)( \
        (unsigned int)(open_cfw_ui_thread_uintptr)(mutex) \
    ))
#endif

#ifndef OPEN_CFW_UI_THREAD_EXTRACT_INPUT
#define OPEN_CFW_UI_THREAD_EXTRACT_INPUT(destination, token) \
    (((open_cfw_ui_thread_extract_fn)0x0046D9ADU)( \
        (void *)0x20073B60U, \
        (destination), \
        (token) \
    ))
#endif

#ifndef OPEN_CFW_UI_THREAD_RUNTIME_INITIALIZE
#define OPEN_CFW_UI_THREAD_RUNTIME_INITIALIZE() \
    (((open_cfw_ui_thread_void_fn)0x0046D465U)())
#endif

#ifndef OPEN_CFW_UI_THREAD_BEFORE_COMMAND
#define OPEN_CFW_UI_THREAD_BEFORE_COMMAND() \
    (((open_cfw_ui_thread_void_fn)0x0046D817U)())
#endif

#ifndef OPEN_CFW_UI_THREAD_AFTER_COMMAND
#define OPEN_CFW_UI_THREAD_AFTER_COMMAND() \
    (((open_cfw_ui_thread_void_fn)0x0046D827U)())
#endif

#ifndef OPEN_CFW_UI_THREAD_START_PREPARE
#define OPEN_CFW_UI_THREAD_START_PREPARE() \
    (((open_cfw_ui_thread_void_fn)0x0046F32DU)())
#endif

#ifndef OPEN_CFW_UI_THREAD_START_TRANSPORT
#define OPEN_CFW_UI_THREAD_START_TRANSPORT() \
    (((open_cfw_ui_thread_void_fn)0x0046F68BU)())
#endif

#ifndef OPEN_CFW_UI_THREAD_START_DISPLAY
#define OPEN_CFW_UI_THREAD_START_DISPLAY() \
    (((open_cfw_ui_thread_void_fn)0x0046C01DU)())
#endif

#ifndef OPEN_CFW_UI_THREAD_REGISTRY_RESET
#define OPEN_CFW_UI_THREAD_REGISTRY_RESET() \
    (((open_cfw_ui_thread_void_fn)0x0044227FU)())
#endif

#ifndef OPEN_CFW_UI_THREAD_UI_INITIALIZE
#define OPEN_CFW_UI_THREAD_UI_INITIALIZE() \
    (((open_cfw_ui_thread_void_fn)0x0044FF39U)())
#endif

#ifndef OPEN_CFW_UI_THREAD_MANAGER_CREATE
#define OPEN_CFW_UI_THREAD_MANAGER_CREATE() \
    (((open_cfw_ui_thread_manager_create_fn)0x0045F15BU)())
#endif

#ifndef OPEN_CFW_UI_THREAD_MANAGER_CONFIGURE
#define OPEN_CFW_UI_THREAD_MANAGER_CONFIGURE() \
    (((void (*)(const void *))0x00460091U)((const void *)0x007560E4U))
#endif

#ifndef OPEN_CFW_UI_THREAD_RENDERER_INITIALIZE
#define OPEN_CFW_UI_THREAD_RENDERER_INITIALIZE() \
    (((open_cfw_ui_thread_void_fn)0x00471165U)())
#endif

#ifndef OPEN_CFW_UI_THREAD_MANAGER_COMMIT
#define OPEN_CFW_UI_THREAD_MANAGER_COMMIT() \
    (((open_cfw_ui_thread_void_fn)0x004600B5U)())
#endif

#ifndef OPEN_CFW_UI_THREAD_SET_BACKGROUND_ID
#define OPEN_CFW_UI_THREAD_SET_BACKGROUND_ID(value) \
    (((open_cfw_ui_thread_value_fn)0x00465D7DU)(value))
#endif

#ifndef OPEN_CFW_UI_THREAD_SET_RENDER_MODE
#define OPEN_CFW_UI_THREAD_SET_RENDER_MODE(value) \
    (((open_cfw_ui_thread_value_fn)0x00471CD7U)(value))
#endif

#ifndef OPEN_CFW_UI_THREAD_REFRESH
#define OPEN_CFW_UI_THREAD_REFRESH() \
    (((open_cfw_ui_thread_void_fn)0x00464345U)())
#endif

#ifndef OPEN_CFW_UI_THREAD_NOTIFY_TRANSITION
#define OPEN_CFW_UI_THREAD_NOTIFY_TRANSITION() \
    (((open_cfw_ui_thread_void_fn)0x00471FA5U)())
#endif

#ifndef OPEN_CFW_UI_THREAD_UPDATE_POWER
#define OPEN_CFW_UI_THREAD_UPDATE_POWER() \
    (((open_cfw_ui_thread_void_fn)0x0047243BU)())
#endif

#ifndef OPEN_CFW_UI_THREAD_MANAGER_OPEN
#define OPEN_CFW_UI_THREAD_MANAGER_OPEN(manager, operation, service) \
    (((open_cfw_ui_thread_manager_open_fn)0x0045FAA9U)( \
        (manager), \
        (operation), \
        (service) \
    ))
#endif

#ifndef OPEN_CFW_UI_THREAD_DELAY
#define OPEN_CFW_UI_THREAD_DELAY(ticks) \
    (((open_cfw_ui_thread_value_fn)0x00454B4DU)(ticks))
#endif

#ifndef OPEN_CFW_UI_THREAD_MANAGER_DESTROY
#define OPEN_CFW_UI_THREAD_MANAGER_DESTROY(manager) \
    (((open_cfw_ui_thread_manager_destroy_fn)0x0045F7BFU)(manager))
#endif

#ifndef OPEN_CFW_UI_THREAD_CLOSE_PREPARE
#define OPEN_CFW_UI_THREAD_CLOSE_PREPARE() \
    (((open_cfw_ui_thread_void_fn)0x0046C0E9U)())
#endif

#ifndef OPEN_CFW_UI_THREAD_CLOSE_DISPLAY
#define OPEN_CFW_UI_THREAD_CLOSE_DISPLAY() \
    (((open_cfw_ui_thread_void_fn)0x00465B11U)())
#endif

#ifndef OPEN_CFW_UI_THREAD_SET_ACTIVE
#define OPEN_CFW_UI_THREAD_SET_ACTIVE(value) \
    (((open_cfw_ui_thread_value_fn)0x00471D59U)(value))
#endif

#ifndef OPEN_CFW_UI_THREAD_CLOSE_TRANSPORT
#define OPEN_CFW_UI_THREAD_CLOSE_TRANSPORT() \
    (((open_cfw_ui_thread_void_fn)0x0046F6A3U)())
#endif

#ifndef OPEN_CFW_UI_THREAD_CLOSE_RUNTIME
#define OPEN_CFW_UI_THREAD_CLOSE_RUNTIME() \
    (((open_cfw_ui_thread_void_fn)0x0046BE7DU)())
#endif

#ifndef OPEN_CFW_UI_THREAD_LOOP_CONTINUE
#define OPEN_CFW_UI_THREAD_LOOP_CONTINUE() 1U
#endif

#ifndef OPEN_CFW_UI_THREAD_LOG_FLAGS
#define OPEN_CFW_UI_THREAD_LOG_FLAGS \
    ((open_cfw_ui_thread_log_flags_fn)0x0043D0CFU)
#endif

#ifndef OPEN_CFW_UI_THREAD_LOG_RECORD
#define OPEN_CFW_UI_THREAD_LOG_RECORD \
    ((open_cfw_ui_thread_log_record_fn)0x0043D575U)
#endif

#ifndef OPEN_CFW_UI_THREAD_TRACE_RECORD
#define OPEN_CFW_UI_THREAD_TRACE_RECORD \
    ((open_cfw_ui_thread_trace_record_fn)0x0043CE9FU)
#endif

#define OPEN_CFW_UI_THREAD_LOG_MODULE ((const void *)0x00785AA0U)
#define OPEN_CFW_UI_THREAD_LOG_FILE ((const void *)0x00701FB4U)
#define OPEN_CFW_UI_THREAD_LOG_TAG ((const void *)0x0076ADACU)

#define OPEN_CFW_UI_THREAD_INIT_FORMAT ((const void *)0x0076ADC8U)
#define OPEN_CFW_UI_THREAD_INIT_TRACE ((const void *)0x0073DE20U)
#define OPEN_CFW_UI_THREAD_DRIVER_FORMAT ((const void *)0x00749254U)
#define OPEN_CFW_UI_THREAD_DRIVER_TRACE ((const void *)0x0071DD88U)
#define OPEN_CFW_UI_THREAD_START_FORMAT ((const void *)0x0076ADE4U)
#define OPEN_CFW_UI_THREAD_START_TRACE ((const void *)0x0073DE4CU)
#define OPEN_CFW_UI_THREAD_IDLE_CLOSE_FORMAT ((const void *)0x0074927CU)
#define OPEN_CFW_UI_THREAD_IDLE_CLOSE_TRACE ((const void *)0x0071DDC0U)
#define OPEN_CFW_UI_THREAD_CLOSE_ALL_FORMAT ((const void *)0x00733074U)
#define OPEN_CFW_UI_THREAD_CLOSE_ALL_TRACE ((const void *)0x0070ABE4U)
#define OPEN_CFW_UI_THREAD_RECEIVED_FORMAT ((const void *)0x0075F370U)
#define OPEN_CFW_UI_THREAD_RECEIVED_TRACE ((const void *)0x007330A4U)
#define OPEN_CFW_UI_THREAD_EXIT_FORMAT ((const void *)0x0075F390U)
#define OPEN_CFW_UI_THREAD_EXIT_TRACE ((const void *)0x007330D4U)
#define OPEN_CFW_UI_THREAD_EXIT_FOREGROUND_FORMAT ((const void *)0x0076AE00U)
#define OPEN_CFW_UI_THREAD_EXIT_FOREGROUND_TRACE ((const void *)0x0073DE78U)
#define OPEN_CFW_UI_THREAD_FOREGROUND_EXISTS_FORMAT ((const void *)0x00733104U)
#define OPEN_CFW_UI_THREAD_FOREGROUND_EXISTS_TRACE ((const void *)0x0070AC24U)
#define OPEN_CFW_UI_THREAD_CLOSE_FORMAT ((const void *)0x0076AE1CU)
#define OPEN_CFW_UI_THREAD_CLOSE_TRACE ((const void *)0x0073DEA4U)
#define OPEN_CFW_UI_THREAD_UNKNOWN_EXIT_FORMAT ((const void *)0x0073DED0U)
#define OPEN_CFW_UI_THREAD_UNKNOWN_EXIT_TRACE ((const void *)0x007142D8U)
#define OPEN_CFW_UI_THREAD_CLEANUP_FORMAT ((const void *)0x0071DE30U)
#define OPEN_CFW_UI_THREAD_CLEANUP_TRACE ((const void *)0x006F9D4CU)
#define OPEN_CFW_UI_THREAD_SWITCH_FORMAT ((const void *)0x007492A4U)
#define OPEN_CFW_UI_THREAD_SWITCH_TRACE ((const void *)0x0071DDF8U)
#define OPEN_CFW_UI_THREAD_INPUT_CLOSE_FORMAT ((const void *)0x0073DEFCU)
#define OPEN_CFW_UI_THREAD_INPUT_CLOSE_TRACE ((const void *)0x00714314U)
#define OPEN_CFW_UI_THREAD_CLOSE_FOREGROUND_FORMAT ((const void *)0x0076AE38U)
#define OPEN_CFW_UI_THREAD_CLOSE_FOREGROUND_TRACE ((const void *)0x0073DF28U)
#define OPEN_CFW_UI_THREAD_CLOSE_BACKGROUND_FORMAT ((const void *)0x00753690U)
#define OPEN_CFW_UI_THREAD_CLOSE_BACKGROUND_TRACE ((const void *)0x00728A2CU)
#define OPEN_CFW_UI_THREAD_UNKNOWN_STATE_FORMAT ((const void *)0x0075F3B0U)
#define OPEN_CFW_UI_THREAD_UNKNOWN_STATE_TRACE ((const void *)0x00733134U)

static inline __attribute__((always_inline))
unsigned int open_cfw_ui_thread_u32(const unsigned char *value)
{
    return
        (unsigned int)value[0] |
        ((unsigned int)value[1] << 8U) |
        ((unsigned int)value[2] << 16U) |
        ((unsigned int)value[3] << 24U);
}

static inline __attribute__((always_inline))
unsigned int open_cfw_ui_thread_trace_enabled(void)
{
    unsigned int flags = OPEN_CFW_UI_THREAD_LOG_FLAGS();

    if (flags & 1U) {
        return 1U;
    }
    return (OPEN_CFW_UI_THREAD_LOG_FLAGS() & 4U) != 0U;
}

static inline __attribute__((always_inline))
void open_cfw_ui_thread_diag0(
    unsigned int level,
    unsigned int line,
    const void *format,
    unsigned int mask,
    const void *trace
)
{
    if (OPEN_CFW_UI_THREAD_LOG_FLAGS() & 2U) {
        OPEN_CFW_UI_THREAD_LOG_RECORD(
            level,
            OPEN_CFW_UI_THREAD_LOG_MODULE,
            OPEN_CFW_UI_THREAD_LOG_FILE,
            OPEN_CFW_UI_THREAD_LOG_TAG,
            line,
            format
        );
    }
    if (open_cfw_ui_thread_trace_enabled()) {
        OPEN_CFW_UI_THREAD_TRACE_RECORD(mask, trace, trace);
    }
}

static inline __attribute__((always_inline))
void open_cfw_ui_thread_diag1(
    unsigned int level,
    unsigned int line,
    const void *format,
    unsigned int mask,
    const void *trace,
    unsigned int value
)
{
    if (OPEN_CFW_UI_THREAD_LOG_FLAGS() & 2U) {
        OPEN_CFW_UI_THREAD_LOG_RECORD(
            level,
            OPEN_CFW_UI_THREAD_LOG_MODULE,
            OPEN_CFW_UI_THREAD_LOG_FILE,
            OPEN_CFW_UI_THREAD_LOG_TAG,
            line,
            format,
            value
        );
    }
    if (open_cfw_ui_thread_trace_enabled()) {
        OPEN_CFW_UI_THREAD_TRACE_RECORD(mask, trace, trace, value);
    }
}

static inline __attribute__((always_inline))
void open_cfw_ui_thread_wait_refresh(void)
{
    unsigned int index;

    for (index = 0U; index < 24U; ++index) {
        OPEN_CFW_UI_THREAD_REFRESH();
        OPEN_CFW_UI_THREAD_DELAY(0x10U);
    }
}

static inline __attribute__((always_inline))
void open_cfw_ui_thread_full_cleanup(
    void *driver,
    unsigned char *state
)
{
    open_cfw_ui_thread_diag0(
        3U,
        0x343U,
        OPEN_CFW_UI_THREAD_CLEANUP_FORMAT,
        0x0C000000U,
        OPEN_CFW_UI_THREAD_CLEANUP_TRACE
    );
    OPEN_CFW_UI_THREAD_CLOSE_PREPARE();
    OPEN_CFW_UI_THREAD_DRIVER_CALL(driver, 4U);
    OPEN_CFW_UI_THREAD_DRIVER_CALL(driver, 0x10U);
    OPEN_CFW_UI_THREAD_CLOSE_DISPLAY();
    OPEN_CFW_UI_THREAD_BACKGROUND_SERVICE = 0U;
    OPEN_CFW_UI_THREAD_DISPLAY_MODE = 0U;
    OPEN_CFW_UI_THREAD_FOREGROUND_SERVICE = 0U;
    OPEN_CFW_UI_THREAD_CONTROL = 0xFFFFFFFFU;
    OPEN_CFW_UI_THREAD_SET_ACTIVE(0U);
    (void)OPEN_CFW_UI_THREAD_FILL(state, 2U, 0U);
    OPEN_CFW_UI_THREAD_CLOSE_TRANSPORT();
    OPEN_CFW_UI_THREAD_CLOSE_RUNTIME();
    OPEN_CFW_UI_THREAD_UPDATE_POWER();
}

/*
 * Stock ABI at 0x004437E0. The RTOS registers the Thumb entry 0x004437E1
 * from the literal at 0x004448F0 and supplies a null context. The context is
 * not consumed by the stock implementation.
 */
__attribute__((used, noinline))
void open_cfw_ui_display_thread(void *context)
{
    unsigned char *message = OPEN_CFW_UI_THREAD_MESSAGE;
    unsigned char *input = OPEN_CFW_UI_THREAD_INPUT_BUFFER;
    unsigned char *state = (unsigned char *)&OPEN_CFW_UI_THREAD_STATE;
    void *driver;

    (void)context;
    open_cfw_ui_thread_diag0(
        3U,
        0x279U,
        OPEN_CFW_UI_THREAD_INIT_FORMAT,
        0x0C000000U,
        OPEN_CFW_UI_THREAD_INIT_TRACE
    );
    open_cfw_ui_modules_initialize();
    (void)OPEN_CFW_UI_THREAD_FILL(state, 2U, 0U);
    driver = OPEN_CFW_UI_THREAD_DRIVER;
    if (OPEN_CFW_UI_THREAD_DRIVER_READY(driver) != 1U) {
        open_cfw_ui_thread_diag0(
            1U,
            0x27EU,
            OPEN_CFW_UI_THREAD_DRIVER_FORMAT,
            0x04000000U,
            OPEN_CFW_UI_THREAD_DRIVER_TRACE
        );
        return;
    }

    OPEN_CFW_UI_THREAD_RUNTIME_INITIALIZE();
    do {
        unsigned int received;
        unsigned int command;
        unsigned int service;
        unsigned int token;

        (void)OPEN_CFW_UI_THREAD_FILL(message, 12U, 0U);
        received = OPEN_CFW_UI_THREAD_RECEIVE(
            OPEN_CFW_UI_THREAD_QUEUE,
            message,
            OPEN_CFW_UI_THREAD_CONTROL
        ) == 0;
        if (received != 0U) {
            (void)OPEN_CFW_UI_THREAD_FILL(input, 0x2800U, 0U);
            OPEN_CFW_UI_THREAD_MUTEX_TAKE(OPEN_CFW_UI_THREAD_MUTEX);
            OPEN_CFW_UI_THREAD_EXTRACT_INPUT(
                input,
                open_cfw_ui_thread_u32(message + 8U)
            );
            OPEN_CFW_UI_THREAD_MUTEX_GIVE(OPEN_CFW_UI_THREAD_MUTEX);
        }

        OPEN_CFW_UI_THREAD_BEFORE_COMMAND();
        command = (unsigned int)message[0];
        service = open_cfw_ui_thread_u32(message + 4U);
        token = open_cfw_ui_thread_u32(message + 8U);

        if (*state == 0U) {
            if (received != 0U) {
                if (command == 2U) {
                    OPEN_CFW_UI_THREAD_START_PREPARE();
                    *state = 1U;
                    OPEN_CFW_UI_THREAD_START_TRANSPORT();
                    OPEN_CFW_UI_THREAD_START_DISPLAY();
                    OPEN_CFW_UI_THREAD_DRIVER_CALL(driver, 0xCU);
                    OPEN_CFW_UI_THREAD_DRIVER_CALL(driver, 8U);
                    OPEN_CFW_UI_THREAD_BACKGROUND_SERVICE = 0U;
                    OPEN_CFW_UI_THREAD_DISPLAY_MODE = 0U;
                    OPEN_CFW_UI_THREAD_FOREGROUND_SERVICE = 0U;
                    open_cfw_ui_thread_diag1(
                        3U,
                        0x2A0U,
                        OPEN_CFW_UI_THREAD_START_FORMAT,
                        0x0C400000U,
                        OPEN_CFW_UI_THREAD_START_TRACE,
                        service
                    );
                    OPEN_CFW_UI_THREAD_REGISTRY_RESET();
                    OPEN_CFW_UI_THREAD_UI_INITIALIZE();
                    OPEN_CFW_UI_THREAD_MANAGER =
                        OPEN_CFW_UI_THREAD_MANAGER_CREATE();
                    OPEN_CFW_UI_THREAD_MANAGER_CONFIGURE();
                    OPEN_CFW_UI_THREAD_RENDERER_INITIALIZE();
                    OPEN_CFW_UI_THREAD_MANAGER_COMMIT();
                    (void)open_cfw_ui_module_dispatch_event(
                        service,
                        2U,
                        (unsigned int)(open_cfw_ui_thread_uintptr)input,
                        token
                    );
                    OPEN_CFW_UI_THREAD_BACKGROUND_SERVICE = service;
                    (void)open_cfw_ui_modules_close_mode1(
                        2U,
                        service,
                        0U,
                        0U
                    );
                    OPEN_CFW_UI_THREAD_CONTROL = 0x10U;
                    OPEN_CFW_UI_THREAD_SET_BACKGROUND_ID(service & 0xFFFFU);
                    OPEN_CFW_UI_THREAD_SET_RENDER_MODE(0U);
                    OPEN_CFW_UI_THREAD_REFRESH();
                    OPEN_CFW_UI_THREAD_NOTIFY_TRANSITION();
                    OPEN_CFW_UI_THREAD_UPDATE_POWER();
                } else if (command == 5U) {
                    open_cfw_ui_thread_diag0(
                        4U,
                        0x2B9U,
                        OPEN_CFW_UI_THREAD_IDLE_CLOSE_FORMAT,
                        0x10000000U,
                        OPEN_CFW_UI_THREAD_IDLE_CLOSE_TRACE
                    );
                    (void)OPEN_CFW_UI_THREAD_FILL(state, 2U, 0U);
                    OPEN_CFW_UI_THREAD_BACKGROUND_SERVICE = 0U;
                    OPEN_CFW_UI_THREAD_CONTROL = 0xFFFFFFFFU;
                } else if (command == 8U) {
                    open_cfw_ui_thread_diag0(
                        4U,
                        0x2C0U,
                        OPEN_CFW_UI_THREAD_CLOSE_ALL_FORMAT,
                        0x10000000U,
                        OPEN_CFW_UI_THREAD_CLOSE_ALL_TRACE
                    );
                    (void)OPEN_CFW_UI_THREAD_FILL(state, 2U, 0U);
                    OPEN_CFW_UI_THREAD_BACKGROUND_SERVICE = 0U;
                    OPEN_CFW_UI_THREAD_CONTROL = 0xFFFFFFFFU;
                }
            }
        } else if (*state == 1U) {
            if (received == 0U) {
                unsigned int active =
                    OPEN_CFW_UI_THREAD_FOREGROUND_SERVICE != 0U
                        ? OPEN_CFW_UI_THREAD_FOREGROUND_SERVICE
                        : OPEN_CFW_UI_THREAD_BACKGROUND_SERVICE;

                (void)open_cfw_ui_module_dispatch_event(
                    active,
                    4U,
                    0U,
                    0U
                );
                OPEN_CFW_UI_THREAD_REFRESH();
            } else {
                open_cfw_ui_thread_diag0(
                    4U,
                    0x2CAU,
                    OPEN_CFW_UI_THREAD_RECEIVED_FORMAT,
                    0x10000000U,
                    OPEN_CFW_UI_THREAD_RECEIVED_TRACE
                );

                if (command == 5U) {
                    unsigned int background =
                        OPEN_CFW_UI_THREAD_BACKGROUND_SERVICE;
                    unsigned int mode = OPEN_CFW_UI_THREAD_DISPLAY_MODE;
                    unsigned int foreground =
                        OPEN_CFW_UI_THREAD_FOREGROUND_SERVICE;

                    open_cfw_ui_thread_diag0(
                        4U,
                        0x2CDU,
                        OPEN_CFW_UI_THREAD_EXIT_FORMAT,
                        0x10000000U,
                        OPEN_CFW_UI_THREAD_EXIT_TRACE
                    );
                    if (
                        foreground != 0U &&
                        mode == 1U &&
                        (service == foreground || service == 0U)
                    ) {
                        (void)open_cfw_ui_module_dispatch_event(
                            foreground,
                            5U,
                            (unsigned int)(open_cfw_ui_thread_uintptr)input,
                            token
                        );
                        (void)OPEN_CFW_UI_THREAD_MANAGER_OPEN(
                            OPEN_CFW_UI_THREAD_MANAGER,
                            0U,
                            foreground
                        );
                        open_cfw_ui_thread_diag1(
                            4U,
                            0x2D1U,
                            OPEN_CFW_UI_THREAD_EXIT_FOREGROUND_FORMAT,
                            0x10400000U,
                            OPEN_CFW_UI_THREAD_EXIT_FOREGROUND_TRACE,
                            foreground
                        );
                        OPEN_CFW_UI_THREAD_FOREGROUND_SERVICE = 0U;
                        open_cfw_ui_thread_wait_refresh();
                        OPEN_CFW_UI_THREAD_NOTIFY_TRANSITION();
                    } else if (
                        foreground != 0U &&
                        mode == 1U &&
                        service == background
                    ) {
                        open_cfw_ui_thread_diag0(
                            3U,
                            0x2DAU,
                            OPEN_CFW_UI_THREAD_FOREGROUND_EXISTS_FORMAT,
                            0x0C000000U,
                            OPEN_CFW_UI_THREAD_FOREGROUND_EXISTS_TRACE
                        );
                    } else {
                        open_cfw_ui_thread_diag0(
                            4U,
                            0x2DDU,
                            OPEN_CFW_UI_THREAD_CLOSE_FORMAT,
                            0x10000000U,
                            OPEN_CFW_UI_THREAD_CLOSE_TRACE
                        );
                        if (
                            mode == 2U &&
                            (service == foreground || service == 0U)
                        ) {
                            (void)open_cfw_ui_module_dispatch_event(
                                foreground,
                                5U,
                                (unsigned int)(
                                    open_cfw_ui_thread_uintptr
                                )input,
                                token
                            );
                            (void)OPEN_CFW_UI_THREAD_MANAGER_OPEN(
                                OPEN_CFW_UI_THREAD_MANAGER,
                                0U,
                                foreground
                            );
                            open_cfw_ui_thread_wait_refresh();
                            OPEN_CFW_UI_THREAD_MANAGER_DESTROY(
                                OPEN_CFW_UI_THREAD_MANAGER
                            );
                            OPEN_CFW_UI_THREAD_MANAGER = (void *)0;
                            *state = 2U;
                            OPEN_CFW_UI_THREAD_NOTIFY_TRANSITION();
                            open_cfw_ui_thread_full_cleanup(driver, state);
                        } else if (
                            mode == 1U &&
                            foreground == 0U &&
                            (service == background || service == 0U)
                        ) {
                            (void)open_cfw_ui_module_dispatch_event(
                                background,
                                5U,
                                (unsigned int)(
                                    open_cfw_ui_thread_uintptr
                                )input,
                                token
                            );
                            OPEN_CFW_UI_THREAD_REFRESH();
                            OPEN_CFW_UI_THREAD_MANAGER_DESTROY(
                                OPEN_CFW_UI_THREAD_MANAGER
                            );
                            OPEN_CFW_UI_THREAD_MANAGER = (void *)0;
                            *state = 2U;
                            OPEN_CFW_UI_THREAD_NOTIFY_TRANSITION();
                            open_cfw_ui_thread_full_cleanup(driver, state);
                        } else {
                            open_cfw_ui_thread_diag1(
                                2U,
                                0x2F1U,
                                OPEN_CFW_UI_THREAD_UNKNOWN_EXIT_FORMAT,
                                0x08400000U,
                                OPEN_CFW_UI_THREAD_UNKNOWN_EXIT_TRACE,
                                service
                            );
                        }
                    }
                } else if (command == 3U) {
                    if (
                        service == OPEN_CFW_UI_THREAD_BACKGROUND_SERVICE ||
                        service == OPEN_CFW_UI_THREAD_FOREGROUND_SERVICE
                    ) {
                        (void)open_cfw_ui_module_dispatch_event(
                            service,
                            3U,
                            (unsigned int)(open_cfw_ui_thread_uintptr)input,
                            token
                        );
                        OPEN_CFW_UI_THREAD_REFRESH();
                    }
                } else if (command == 2U) {
                    unsigned int result;

                    open_cfw_ui_thread_diag0(
                        3U,
                        0x2FEU,
                        OPEN_CFW_UI_THREAD_SWITCH_FORMAT,
                        0x0C000000U,
                        OPEN_CFW_UI_THREAD_SWITCH_TRACE
                    );
                    OPEN_CFW_UI_THREAD_REGISTRY_RESET();
                    result = open_cfw_ui_switch_display(
                        service,
                        (unsigned int)(open_cfw_ui_thread_uintptr)input,
                        token
                    );
                    OPEN_CFW_UI_THREAD_NOTIFY_TRANSITION();
                    if (result == 1U) {
                        open_cfw_ui_thread_wait_refresh();
                    } else {
                        OPEN_CFW_UI_THREAD_REFRESH();
                    }
                } else if (command == 7U) {
                    if (open_cfw_ui_input_event_handler(input) != 1U) {
                        OPEN_CFW_UI_THREAD_REFRESH();
                    } else {
                        unsigned int foreground =
                            OPEN_CFW_UI_THREAD_FOREGROUND_SERVICE;

                        open_cfw_ui_thread_diag0(
                            3U,
                            0x30FU,
                            OPEN_CFW_UI_THREAD_INPUT_CLOSE_FORMAT,
                            0x0C000000U,
                            OPEN_CFW_UI_THREAD_INPUT_CLOSE_TRACE
                        );
                        OPEN_CFW_UI_THREAD_NOTIFY_TRANSITION();
                        *state = 2U;
                        (void)open_cfw_ui_module_dispatch_event(
                            foreground,
                            5U,
                            0U,
                            0U
                        );
                        (void)OPEN_CFW_UI_THREAD_MANAGER_OPEN(
                            OPEN_CFW_UI_THREAD_MANAGER,
                            0U,
                            foreground
                        );
                        open_cfw_ui_thread_wait_refresh();
                        OPEN_CFW_UI_THREAD_MANAGER_DESTROY(
                            OPEN_CFW_UI_THREAD_MANAGER
                        );
                        OPEN_CFW_UI_THREAD_MANAGER = (void *)0;
                        open_cfw_ui_thread_full_cleanup(driver, state);
                    }
                } else if (command == 8U) {
                    unsigned int foreground =
                        OPEN_CFW_UI_THREAD_FOREGROUND_SERVICE;
                    unsigned int background =
                        OPEN_CFW_UI_THREAD_BACKGROUND_SERVICE;

                    open_cfw_ui_thread_diag0(
                        4U,
                        0x320U,
                        OPEN_CFW_UI_THREAD_CLOSE_ALL_FORMAT,
                        0x10000000U,
                        OPEN_CFW_UI_THREAD_CLOSE_ALL_TRACE
                    );
                    if (foreground != 0U) {
                        open_cfw_ui_thread_diag1(
                            4U,
                            0x322U,
                            OPEN_CFW_UI_THREAD_CLOSE_FOREGROUND_FORMAT,
                            0x10400000U,
                            OPEN_CFW_UI_THREAD_CLOSE_FOREGROUND_TRACE,
                            foreground
                        );
                        (void)open_cfw_ui_module_dispatch_event(
                            foreground,
                            5U,
                            0U,
                            0U
                        );
                        (void)OPEN_CFW_UI_THREAD_MANAGER_OPEN(
                            OPEN_CFW_UI_THREAD_MANAGER,
                            0U,
                            foreground
                        );
                        open_cfw_ui_thread_wait_refresh();
                        OPEN_CFW_UI_THREAD_FOREGROUND_SERVICE = 0U;
                    }
                    if (
                        background != 0U &&
                        background !=
                            OPEN_CFW_UI_THREAD_FOREGROUND_SERVICE &&
                        OPEN_CFW_UI_THREAD_DISPLAY_MODE == 1U
                    ) {
                        open_cfw_ui_thread_diag1(
                            4U,
                            0x32DU,
                            OPEN_CFW_UI_THREAD_CLOSE_BACKGROUND_FORMAT,
                            0x10400000U,
                            OPEN_CFW_UI_THREAD_CLOSE_BACKGROUND_TRACE,
                            background
                        );
                        (void)open_cfw_ui_module_dispatch_event(
                            background,
                            5U,
                            0U,
                            0U
                        );
                        OPEN_CFW_UI_THREAD_BACKGROUND_SERVICE = 0U;
                    }
                    OPEN_CFW_UI_THREAD_MANAGER_DESTROY(
                        OPEN_CFW_UI_THREAD_MANAGER
                    );
                    OPEN_CFW_UI_THREAD_MANAGER = (void *)0;
                    OPEN_CFW_UI_THREAD_NOTIFY_TRANSITION();
                    *state = 2U;
                    open_cfw_ui_thread_full_cleanup(driver, state);
                } else {
                    open_cfw_ui_thread_full_cleanup(driver, state);
                }
            }
        } else if (*state == 2U) {
            open_cfw_ui_thread_full_cleanup(driver, state);
        } else {
            open_cfw_ui_thread_diag0(
                2U,
                0x359U,
                OPEN_CFW_UI_THREAD_UNKNOWN_STATE_FORMAT,
                0x08000000U,
                OPEN_CFW_UI_THREAD_UNKNOWN_STATE_TRACE
            );
            OPEN_CFW_UI_THREAD_DRIVER_CALL(driver, 4U);
            OPEN_CFW_UI_THREAD_DRIVER_CALL(driver, 0x10U);
            OPEN_CFW_UI_THREAD_CLOSE_PREPARE();
            (void)OPEN_CFW_UI_THREAD_FILL(state, 2U, 0U);
            OPEN_CFW_UI_THREAD_BACKGROUND_SERVICE = 0U;
            OPEN_CFW_UI_THREAD_CONTROL = 0xFFFFFFFFU;
        }

        OPEN_CFW_UI_THREAD_AFTER_COMMAND();
    } while (OPEN_CFW_UI_THREAD_LOOP_CONTINUE() != 0U);
}
