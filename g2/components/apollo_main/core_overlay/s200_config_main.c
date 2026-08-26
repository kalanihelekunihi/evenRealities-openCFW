/*
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * Clean-room source replacement for product\s200\app\config\main.c in
 * G2 2.2.6.10. Diagnostics are intentionally omitted; LVGL interaction,
 * platform initialization, reset handling, release registration, and the
 * application startup hand-off are preserved.
 */

typedef unsigned char s200_u8;
typedef unsigned int s200_u32;
typedef signed int s200_i32;

typedef struct {
    s200_u8 reserved0[2];
    s200_u8 external_reset;
    s200_u8 power_on_reset;
    s200_u8 brown_out_reset;
    s200_u8 software_power_on_reset;
    s200_u8 software_power_on_init_reset;
    s200_u8 debugger_reset;
    s200_u8 watchdog_reset;
    s200_u8 reserved9[5];
    s200_u8 cm55_software_reset;
} open_cfw_s200_reset_state;

int open_cfw_retained_s200_event_is_class(const void *, const void *);
s200_u32 open_cfw_retained_s200_event_code(const void *);
void *open_cfw_retained_s200_parent(void *);
s200_i32 open_cfw_retained_s200_value_get(void *);
void open_cfw_retained_s200_value_set(void *, s200_i32, s200_u32);
void open_cfw_retained_s200_event_send(void *, s200_u32, void *);
void *open_cfw_retained_s200_input_device(void);
void open_cfw_retained_s200_input_point(void *, s200_i32 *);
s200_i32 open_cfw_retained_s200_object_width(void *);
s200_i32 open_cfw_retained_s200_object_height(void *);
s200_u32 open_cfw_retained_s200_value_direction(void *, s200_u32);
s200_i32 open_cfw_retained_s200_content_width(void *);
s200_i32 open_cfw_retained_s200_content_height(void *);
void open_cfw_retained_s200_object_size(void *, s200_i32, s200_i32);
void open_cfw_retained_s200_layout(void *, s200_u32);
void *open_cfw_retained_s200_object_create(void *);
void open_cfw_retained_s200_object_configure(void *);
s200_i32 open_cfw_retained_s200_display_width(void);
void open_cfw_retained_s200_object_align(void *, s200_u32, s200_u32, s200_u32);
void open_cfw_retained_s200_object_mode(void *, s200_u32);
void open_cfw_retained_s200_object_limit(void *, s200_i32);
void open_cfw_retained_s200_reset_capture(volatile open_cfw_s200_reset_state *);
void open_cfw_retained_s200_watchdog_prepare(void);
void open_cfw_retained_s200_clock_prepare(void);
void open_cfw_retained_s200_clock_select(s200_u32);
void open_cfw_retained_s200_transport_prepare(void);
void open_cfw_retained_s200_power_prepare(void);
void open_cfw_retained_s200_power_select(s200_u32);
s200_i32 open_cfw_retained_s200_performance_select(s200_u32);
void open_cfw_retained_s200_runtime_prepare(void);
void open_cfw_retained_s200_service_prepare(void);
void open_cfw_retained_s200_release_register(
    const char *, const char *, const char *
);
void open_cfw_retained_s200_reset_status_clear(s200_u32, s200_u32);
void open_cfw_retained_s200_delay(s200_u32);
void open_cfw_retained_s200_application_prepare(void);
void open_cfw_retained_s200_product_rtos_init(void);

#ifndef OPEN_CFW_S200_MAIN_CLASS_DESCRIPTOR
#define OPEN_CFW_S200_MAIN_CLASS_DESCRIPTOR ((const void *)0x007566A8U)
#endif
#ifndef OPEN_CFW_S200_MAIN_RESET_STATE
#define OPEN_CFW_S200_MAIN_RESET_STATE \
    (*(volatile open_cfw_s200_reset_state *)0x20073EA4U)
#endif
#ifndef OPEN_CFW_S200_MAIN_RELEASE_PATH
#define OPEN_CFW_S200_MAIN_RELEASE_PATH ((const char *)0x0074B194U)
#endif
#ifndef OPEN_CFW_S200_MAIN_RELEASE_TYPE
#define OPEN_CFW_S200_MAIN_RELEASE_TYPE ((const char *)0x0078DC9CU)
#endif
#ifndef OPEN_CFW_S200_MAIN_RELEASE_VERSION
#define OPEN_CFW_S200_MAIN_RELEASE_VERSION ((const char *)0x0078B57CU)
#endif
#ifndef OPEN_CFW_S200_MAIN_HALT
#define OPEN_CFW_S200_MAIN_HALT() \
    do { for (;;) { __asm volatile(""); } } while (0)
#endif
#ifndef OPEN_CFW_S200_MAIN_STARTUP_HANDOFF
#define OPEN_CFW_S200_MAIN_STARTUP_HANDOFF() \
    (*(void (**)(void))0x200040D8U)()
#endif

#if defined(OPEN_CFW_S200_MAIN_CLASS_EVENT_ONLY)
#define OPEN_CFW_S200_MAIN_SELECTOR 1
#elif defined(OPEN_CFW_S200_MAIN_INPUT_EVENT_ONLY)
#define OPEN_CFW_S200_MAIN_SELECTOR 2
#elif defined(OPEN_CFW_S200_MAIN_WIDGET_INIT_ONLY)
#define OPEN_CFW_S200_MAIN_SELECTOR 3
#elif defined(OPEN_CFW_S200_MAIN_PLATFORM_INIT_ONLY)
#define OPEN_CFW_S200_MAIN_SELECTOR 4
#elif defined(OPEN_CFW_S200_MAIN_REPORT_RESET_ONLY)
#define OPEN_CFW_S200_MAIN_SELECTOR 5
#elif defined(OPEN_CFW_S200_MAIN_THREAD_ONLY)
#define OPEN_CFW_S200_MAIN_SELECTOR 6
#elif !defined(OPEN_CFW_S200_MAIN_SELECTOR)
#define OPEN_CFW_S200_MAIN_SELECTOR 0
#endif
#define S200_MAIN_BUILD(n) \
    (OPEN_CFW_S200_MAIN_SELECTOR == 0 || OPEN_CFW_S200_MAIN_SELECTOR == (n))

void open_cfw_s200_main_class_event(const void *class_object, const void *event);
void open_cfw_s200_main_input_event(const void *event);
void open_cfw_s200_main_widget_init(const void *class_object, void *object);
s200_i32 open_cfw_s200_main_platform_init(void);
s200_u32 open_cfw_s200_main_report_reset(void);
void open_cfw_s200_main_thread(void);

#if defined(__arm__) || defined(__thumb__)
__asm__(
    ".type open_cfw_s200_main_class_event,%function\n"
    ".type open_cfw_s200_main_input_event,%function\n"
    ".type open_cfw_s200_main_widget_init,%function\n"
    ".type open_cfw_s200_main_platform_init,%function\n"
    ".type open_cfw_s200_main_report_reset,%function\n"
    ".type open_cfw_s200_main_thread,%function\n"
);
#endif

#if S200_MAIN_BUILD(1)
__attribute__((used, noinline))
void open_cfw_s200_main_class_event(
    const void *class_object,
    const void *event
)
{
    void *target;
    (void)class_object;
    if (open_cfw_retained_s200_event_is_class(
            OPEN_CFW_S200_MAIN_CLASS_DESCRIPTOR, event) == 1) {
        target = *(void * const *)event;
        if (open_cfw_retained_s200_event_code(event) == 0x31U) {
            open_cfw_retained_s200_value_set(
                target, open_cfw_retained_s200_value_get(target), 0U
            );
        }
    }
}
#endif

#if S200_MAIN_BUILD(2)
__attribute__((used, noinline))
void open_cfw_s200_main_input_event(const void *event)
{
    void *target = *(void * const *)event;
    s200_u32 code = open_cfw_retained_s200_event_code(event);
    void *object = open_cfw_retained_s200_parent(target);
    if (code == 0x33U) {
        open_cfw_retained_s200_value_set(
            object, open_cfw_retained_s200_value_get(object), 0U
        );
    } else if (code == 0x0EU) {
        void *input = open_cfw_retained_s200_input_device();
        s200_i32 point[2];
        s200_i32 extent;
        s200_i32 value;
        s200_i32 old_value;
        if (input != (void *)0 && *((s200_u8 *)input + 8) == 1U) {
            return;
        }
        open_cfw_retained_s200_input_point(target, point);
        if ((*((s200_u8 *)object + 0x30) & 0x0CU) != 0U) {
            extent = open_cfw_retained_s200_object_width(target);
            if (open_cfw_retained_s200_value_direction(object, 0U) == 1U) {
                value = (extent / 2 - point[0]) / extent;
            } else {
                value = (extent / 2 + point[0]) / extent;
            }
        } else {
            extent = open_cfw_retained_s200_object_height(target);
            value = (extent / 2 + point[1]) / extent;
        }
        if (value < 0) {
            value = 0;
        }
        old_value = open_cfw_retained_s200_value_get(object);
        open_cfw_retained_s200_value_set(
            object, value,
            open_cfw_retained_s200_input_device() == (void *)0 ? 0U : 1U
        );
        if (value != old_value) {
            open_cfw_retained_s200_event_send(object, 0x23U, (void *)0);
        }
    }
}
#endif

#if S200_MAIN_BUILD(3)
__attribute__((used, noinline))
void open_cfw_s200_main_widget_init(const void *class_object, void *object)
{
    void *parent = open_cfw_retained_s200_parent(object);
    s200_i32 width = open_cfw_retained_s200_content_width(parent);
    s200_i32 height = open_cfw_retained_s200_content_height(parent);
    void *child;
    (void)class_object;
    open_cfw_retained_s200_object_size(object, height, width);
    open_cfw_retained_s200_layout(object, 1U);
    child = open_cfw_retained_s200_object_create(object);
    open_cfw_retained_s200_object_configure(object);
    open_cfw_retained_s200_object_size(
        child, 100, open_cfw_retained_s200_display_width() / 2
    );
    open_cfw_retained_s200_layout(child, 0U);
    open_cfw_retained_s200_object_align(child, 0U, 2U, 2U);
    child = open_cfw_retained_s200_object_create(object);
    open_cfw_retained_s200_object_mode(child, 1U);
    open_cfw_retained_s200_object_limit(child, 100);
}
#endif

#if S200_MAIN_BUILD(4)
__attribute__((used, noinline))
s200_i32 open_cfw_s200_main_platform_init(void)
{
    s200_i32 result;
    open_cfw_retained_s200_reset_capture(&OPEN_CFW_S200_MAIN_RESET_STATE);
    open_cfw_retained_s200_watchdog_prepare();
    open_cfw_retained_s200_clock_prepare();
    open_cfw_retained_s200_clock_select(1U);
    open_cfw_retained_s200_transport_prepare();
    open_cfw_retained_s200_power_prepare();
    open_cfw_retained_s200_power_select(1U);
    result = open_cfw_retained_s200_performance_select(2U);
    open_cfw_retained_s200_runtime_prepare();
    open_cfw_retained_s200_service_prepare();
    open_cfw_retained_s200_release_register(
        OPEN_CFW_S200_MAIN_RELEASE_PATH,
        OPEN_CFW_S200_MAIN_RELEASE_TYPE,
        OPEN_CFW_S200_MAIN_RELEASE_VERSION
    );
    return result;
}
#endif

#if S200_MAIN_BUILD(5)
__attribute__((used, noinline))
s200_u32 open_cfw_s200_main_report_reset(void)
{
    volatile open_cfw_s200_reset_state *state = &OPEN_CFW_S200_MAIN_RESET_STATE;
    s200_u32 reason;
    if (state->external_reset != 0U) {
        reason = 1U;
    } else if (state->power_on_reset != 0U) {
        reason = 2U;
    } else if (state->brown_out_reset != 0U) {
        reason = 3U;
        open_cfw_retained_s200_reset_status_clear(0U, 0U);
    } else if (state->software_power_on_reset != 0U) {
        reason = 4U;
    } else if (state->software_power_on_init_reset != 0U) {
        reason = 5U;
    } else if (state->debugger_reset != 0U) {
        reason = 6U;
    } else if (state->watchdog_reset != 0U) {
        reason = 7U;
    } else if (state->cm55_software_reset != 0U) {
        reason = 8U;
    } else {
        reason = 0U;
    }
    return reason;
}
#endif

#if S200_MAIN_BUILD(6)
__attribute__((used, noinline, noreturn))
void open_cfw_s200_main_thread(void)
{
    open_cfw_retained_s200_delay(200U);
    open_cfw_retained_s200_application_prepare();
    (void)open_cfw_s200_main_report_reset();
    open_cfw_retained_s200_product_rtos_init();
    OPEN_CFW_S200_MAIN_STARTUP_HANDOFF();
    OPEN_CFW_S200_MAIN_HALT();
    __builtin_unreachable();
}
#endif
