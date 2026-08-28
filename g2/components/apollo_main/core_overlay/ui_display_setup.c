/*
 * SPDX-License-Identifier: MIT
 *
 * Display/input setup helper replacements for the Even Realities G2
 * 2.2.6.10 Apollo510B application. Exact stock boundaries, the sole caller,
 * persistent SRAM record, and behavioral evidence are recorded in
 * EVIDENCE.md.
 */

typedef void (*open_cfw_ui_setup_void_fn)(void);
typedef void (*open_cfw_ui_setup_callback_fn)(
    void *unused,
    void *context
);
typedef void (*open_cfw_ui_setup_bind_fn)(
    open_cfw_ui_setup_callback_fn callback
);
typedef void (*open_cfw_ui_setup_record_fn)(void *record);
typedef void (*open_cfw_ui_setup_record_configure_fn)(
    unsigned int selector,
    void *record
);
typedef void (*open_cfw_ui_setup_value_fn)(unsigned int value);
typedef void (*open_cfw_ui_setup_event_fn)(
    unsigned int service,
    unsigned int event
);

#ifndef OPEN_CFW_UI_SETUP_INPUT_RECORD
#define OPEN_CFW_UI_SETUP_INPUT_RECORD \
    ((volatile unsigned char *)0x20073B48U)
#endif

#ifndef OPEN_CFW_UI_SETUP_DISPLAY_RUNTIME_BEGIN
#define OPEN_CFW_UI_SETUP_DISPLAY_RUNTIME_BEGIN() \
    (((open_cfw_ui_setup_void_fn)0x00473549U)())
#endif

#ifndef OPEN_CFW_UI_SETUP_DISPLAY_CALLBACK
extern void open_cfw_ui_display_callback(
    void *unused,
    void *context
);
#define OPEN_CFW_UI_SETUP_DISPLAY_CALLBACK \
    open_cfw_ui_display_callback
#endif

#ifndef OPEN_CFW_UI_SETUP_DISPLAY_BIND
#define OPEN_CFW_UI_SETUP_DISPLAY_BIND(callback) \
    (((open_cfw_ui_setup_bind_fn)0x0044D255U)(callback))
#endif

#ifndef OPEN_CFW_UI_SETUP_DISPLAY_RUNTIME_COMMIT
#define OPEN_CFW_UI_SETUP_DISPLAY_RUNTIME_COMMIT() \
    (((open_cfw_ui_setup_void_fn)0x00473929U)())
#endif

#ifndef OPEN_CFW_UI_SETUP_INPUT_RECORD_RESET
#define OPEN_CFW_UI_SETUP_INPUT_RECORD_RESET(record) \
    (((open_cfw_ui_setup_record_fn)0x00471CAFU)((void *)(record)))
#endif

#ifndef OPEN_CFW_UI_SETUP_INPUT_RECORD_CONFIGURE
#define OPEN_CFW_UI_SETUP_INPUT_RECORD_CONFIGURE(selector, record) \
    (((open_cfw_ui_setup_record_configure_fn)0x00471C9BU)( \
        (selector), \
        (void *)(record) \
    ))
#endif

#ifndef OPEN_CFW_UI_SETUP_INPUT_TRANSITION_ZERO
#define OPEN_CFW_UI_SETUP_INPUT_TRANSITION_ZERO(value) \
    (((open_cfw_ui_setup_value_fn)0x00471DADU)(value))
#endif

#ifndef OPEN_CFW_UI_SETUP_INPUT_TRANSITION_ONE
#define OPEN_CFW_UI_SETUP_INPUT_TRANSITION_ONE(value) \
    (((open_cfw_ui_setup_value_fn)0x00471E93U)(value))
#endif

#ifndef OPEN_CFW_UI_SETUP_INPUT_POST_EVENT
#define OPEN_CFW_UI_SETUP_INPUT_POST_EVENT(service, event) \
    (((open_cfw_ui_setup_event_fn)0x00442257U)((service), (event)))
#endif

#ifndef OPEN_CFW_UI_SETUP_INPUT_PUBLISH
#define OPEN_CFW_UI_SETUP_INPUT_PUBLISH(service) \
    (((open_cfw_ui_setup_value_fn)0x00442239U)(service))
#endif

#ifndef OPEN_CFW_UI_SETUP_INPUT_RUNTIME_COMMIT
#define OPEN_CFW_UI_SETUP_INPUT_RUNTIME_COMMIT() \
    (((open_cfw_ui_setup_void_fn)0x00473935U)())
#endif

#ifndef OPEN_CFW_UI_SETUP_INPUT_SET_ACTIVE
#define OPEN_CFW_UI_SETUP_INPUT_SET_ACTIVE(value) \
    (((open_cfw_ui_setup_value_fn)0x00471D59U)(value))
#endif

/*
 * Stock ABI at 0x00444694. Its only recovered caller ignores the incidental
 * r0 value produced by the stock epilogue.
 */
__attribute__((used, noinline))
void open_cfw_ui_prepare_display(void)
{
    OPEN_CFW_UI_SETUP_DISPLAY_RUNTIME_BEGIN();
    OPEN_CFW_UI_SETUP_DISPLAY_BIND(OPEN_CFW_UI_SETUP_DISPLAY_CALLBACK);
    OPEN_CFW_UI_SETUP_DISPLAY_RUNTIME_COMMIT();
}

/*
 * Stock ABI at 0x004446B4. The reset hook owns unspecified record fields;
 * this helper writes only the five recovered fields before the ordered
 * transition/event sequence.
 */
__attribute__((used, noinline))
void open_cfw_ui_prepare_input(void)
{
    volatile unsigned char *record = OPEN_CFW_UI_SETUP_INPUT_RECORD;

    OPEN_CFW_UI_SETUP_INPUT_RECORD_RESET(record);
    *(volatile unsigned short *)(record + 0U) = 1U;
    record[2] = 2U;
    *(volatile unsigned int *)(record + 12U) = 0U;
    *(volatile unsigned int *)(record + 16U) = 6000U;
    OPEN_CFW_UI_SETUP_INPUT_RECORD_CONFIGURE(0U, record);
    OPEN_CFW_UI_SETUP_INPUT_TRANSITION_ZERO(0U);
    OPEN_CFW_UI_SETUP_INPUT_TRANSITION_ONE(1U);
    OPEN_CFW_UI_SETUP_INPUT_POST_EVENT(0x43U, 4U);
    OPEN_CFW_UI_SETUP_INPUT_PUBLISH(0x43U);
    OPEN_CFW_UI_SETUP_INPUT_RUNTIME_COMMIT();
    OPEN_CFW_UI_SETUP_INPUT_SET_ACTIVE(0U);
}
