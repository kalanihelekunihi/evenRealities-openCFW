/*
 * OpenCFW clean-room G2 sensor-hub policy and message router.
 *
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * Recreated from authenticated linked-object behavior and ABI evidence. No
 * vendor source text is included. Hardware register/FIFO work remains in the
 * independently bounded IMU and ALS providers.
 */

#include <stddef.h>
#include <stdint.h>

#ifndef OPEN_CFW_SENSOR_HUB_SELECTOR
#define OPEN_CFW_SENSOR_HUB_SELECTOR 0
#endif

typedef void (*open_cfw_sensor_hub_handler)(const void *record);

struct open_cfw_sensor_hub_record {
    uint16_t id;
    uint16_t reserved;
    uint32_t argument;
};

struct open_cfw_sensor_hub_handler_slot {
    uint16_t id;
    uint16_t reserved;
    open_cfw_sensor_hub_handler handler;
};

struct open_cfw_sensor_hub_calibration {
    float value[9];
};

_Static_assert(sizeof(struct open_cfw_sensor_hub_record) == 8u,
               "G2 sensor-hub record ABI changed");

#ifndef OPEN_CFW_SENSOR_HUB_THREAD_ID
#define OPEN_CFW_SENSOR_HUB_THREAD_ID \
    (*(void * volatile *)(uintptr_t)0x2000366cu)
#endif
#ifndef OPEN_CFW_SENSOR_HUB_QUEUE_ID
#define OPEN_CFW_SENSOR_HUB_QUEUE_ID \
    (*(void * volatile *)(uintptr_t)0x20003670u)
#endif
#ifndef OPEN_CFW_SENSOR_HUB_TIMER_ID
#define OPEN_CFW_SENSOR_HUB_TIMER_ID \
    (*(void * volatile *)(uintptr_t)0x20074908u)
#endif
#ifndef OPEN_CFW_SENSOR_HUB_LAST_TICK
#define OPEN_CFW_SENSOR_HUB_LAST_TICK \
    (*(volatile uint32_t *)(uintptr_t)0x2007490cu)
#endif
#ifndef OPEN_CFW_SENSOR_HUB_TIMER_ENABLED
#define OPEN_CFW_SENSOR_HUB_TIMER_ENABLED \
    (*(volatile uint32_t *)(uintptr_t)0x20074910u)
#endif
#ifndef OPEN_CFW_SENSOR_HUB_ROLE
#define OPEN_CFW_SENSOR_HUB_ROLE \
    (*(volatile uint16_t *)(uintptr_t)0x20004526u)
#endif
#ifndef OPEN_CFW_SENSOR_HUB_HANDLER_TABLE
#define OPEN_CFW_SENSOR_HUB_HANDLER_TABLE \
    ((volatile struct open_cfw_sensor_hub_handler_slot *)(uintptr_t)0x20003688u)
#endif
#ifndef OPEN_CFW_SENSOR_HUB_CALIBRATION_SCREEN
#define OPEN_CFW_SENSOR_HUB_CALIBRATION_SCREEN \
    (*(void * volatile *)(uintptr_t)0x200749a8u)
#endif
#ifndef OPEN_CFW_SENSOR_HUB_CALIBRATION_LABEL_LEFT
#define OPEN_CFW_SENSOR_HUB_CALIBRATION_LABEL_LEFT \
    (*(void * volatile *)(uintptr_t)0x200749acu)
#endif
#ifndef OPEN_CFW_SENSOR_HUB_CALIBRATION_LABEL_RIGHT
#define OPEN_CFW_SENSOR_HUB_CALIBRATION_LABEL_RIGHT \
    (*(void * volatile *)(uintptr_t)0x200749b0u)
#endif
#ifndef OPEN_CFW_SENSOR_HUB_THREAD_ATTRIBUTES
#define OPEN_CFW_SENSOR_HUB_THREAD_ATTRIBUTES \
    ((const void *)(uintptr_t)0x00759048u)
#endif
#ifndef OPEN_CFW_SENSOR_HUB_TIMER_ATTRIBUTES
#define OPEN_CFW_SENSOR_HUB_TIMER_ATTRIBUTES \
    ((const void *)(uintptr_t)0x00788660u)
#endif

void *open_cfw_cmsis_thread_new(
    void (*entry)(void *), void *argument, const void *attributes);
int32_t open_cfw_cmsis_thread_terminate(void *thread_id);
void *open_cfw_cmsis_message_queue_new(
    uint32_t count, uint32_t size, const void *attributes);
int32_t open_cfw_cmsis_message_queue_put(
    void *queue_id, const void *message, uint8_t priority, uint32_t timeout);
int32_t open_cfw_cmsis_message_queue_get(
    void *queue_id, void *message, uint8_t *priority, uint32_t timeout);
void *open_cfw_cmsis_timer_new(
    void (*callback)(void *), uint32_t type, void *argument,
    const void *attributes);
int32_t open_cfw_cmsis_timer_start(void *timer_id, uint32_t ticks);
int32_t open_cfw_cmsis_timer_stop(void *timer_id);
uint32_t open_cfw_cmsis_kernel_get_tick_count(void);

#ifndef OPEN_CFW_SENSOR_HUB_THREAD_NEW
#define OPEN_CFW_SENSOR_HUB_THREAD_NEW(e, a, p) \
    open_cfw_cmsis_thread_new((e), (a), (p))
#endif
#ifndef OPEN_CFW_SENSOR_HUB_THREAD_TERMINATE
#define OPEN_CFW_SENSOR_HUB_THREAD_TERMINATE(i) \
    open_cfw_cmsis_thread_terminate((i))
#endif
#ifndef OPEN_CFW_SENSOR_HUB_QUEUE_NEW
#define OPEN_CFW_SENSOR_HUB_QUEUE_NEW(c, s, a) \
    open_cfw_cmsis_message_queue_new((c), (s), (a))
#endif
#ifndef OPEN_CFW_SENSOR_HUB_QUEUE_PUT
#define OPEN_CFW_SENSOR_HUB_QUEUE_PUT(q, m, p, t) \
    open_cfw_cmsis_message_queue_put((q), (m), (p), (t))
#endif
#ifndef OPEN_CFW_SENSOR_HUB_QUEUE_GET
#define OPEN_CFW_SENSOR_HUB_QUEUE_GET(q, m, p, t) \
    open_cfw_cmsis_message_queue_get((q), (m), (p), (t))
#endif
#ifndef OPEN_CFW_SENSOR_HUB_TIMER_NEW
#define OPEN_CFW_SENSOR_HUB_TIMER_NEW(c, t, a, p) \
    open_cfw_cmsis_timer_new((c), (t), (a), (p))
#endif
#ifndef OPEN_CFW_SENSOR_HUB_TIMER_START
#define OPEN_CFW_SENSOR_HUB_TIMER_START(i, t) \
    open_cfw_cmsis_timer_start((i), (t))
#endif
#ifndef OPEN_CFW_SENSOR_HUB_TIMER_STOP
#define OPEN_CFW_SENSOR_HUB_TIMER_STOP(i) open_cfw_cmsis_timer_stop((i))
#endif
#ifndef OPEN_CFW_SENSOR_HUB_TICK
#define OPEN_CFW_SENSOR_HUB_TICK() open_cfw_cmsis_kernel_get_tick_count()
#endif

void open_cfw_retained_thread_state_active(uint32_t thread_index);
void open_cfw_retained_thread_state_exit(uint32_t thread_index);
void open_cfw_retained_critical_enter(void);
void open_cfw_retained_critical_exit(void);
uint32_t open_cfw_retained_product_mode(void);
uint32_t open_cfw_retained_ota_active(void);
uint32_t open_cfw_retained_glasses_role(void);
void open_cfw_retained_als_initialize(void);
void open_cfw_retained_als_open(void);
void open_cfw_retained_als_close(void);

void open_cfw_retained_imu_reset(void);
void open_cfw_retained_imu_initialize(uint8_t mode);
void open_cfw_retained_imu_read_data(uint32_t tick);
void open_cfw_retained_imu_start_collection(void);
void open_cfw_retained_imu_stop_collection(void);
void open_cfw_retained_imu_set_work_mode(uint8_t mode);
void open_cfw_retained_imu_set_motion_threshold(uint32_t value);
void open_cfw_retained_imu_set_motion_period(uint32_t first, uint32_t second);
void open_cfw_retained_imu_set_accel_config(uint32_t value);
uint8_t open_cfw_retained_imu_state_zero(void);
uint8_t open_cfw_retained_imu_state_one(void);
uint8_t open_cfw_retained_imu_state_two(void);
uint8_t open_cfw_retained_imu_state_three(void);
void open_cfw_retained_imu_set_state_zero(uint8_t value);
void open_cfw_retained_imu_set_state_one(uint8_t value);
void open_cfw_retained_imu_set_state_two(uint8_t value);
void open_cfw_retained_imu_set_state_three(uint8_t value);
void open_cfw_retained_calibration_load(
    float *first, float *second, struct open_cfw_sensor_hub_calibration *matrix);
void open_cfw_retained_imu_apply_calibration(
    const float *first, const float *second,
    const struct open_cfw_sensor_hub_calibration *matrix);
void open_cfw_retained_zero(void *destination, uint32_t size);

#ifndef OPEN_CFW_SENSOR_HUB_STATE_ACTIVE
#define OPEN_CFW_SENSOR_HUB_STATE_ACTIVE(i) \
    open_cfw_retained_thread_state_active((i))
#endif
#ifndef OPEN_CFW_SENSOR_HUB_STATE_EXIT
#define OPEN_CFW_SENSOR_HUB_STATE_EXIT(i) \
    open_cfw_retained_thread_state_exit((i))
#endif
#ifndef OPEN_CFW_SENSOR_HUB_CRITICAL_ENTER
#define OPEN_CFW_SENSOR_HUB_CRITICAL_ENTER() open_cfw_retained_critical_enter()
#endif
#ifndef OPEN_CFW_SENSOR_HUB_CRITICAL_EXIT
#define OPEN_CFW_SENSOR_HUB_CRITICAL_EXIT() open_cfw_retained_critical_exit()
#endif
#ifndef OPEN_CFW_SENSOR_HUB_PRODUCT_MODE
#define OPEN_CFW_SENSOR_HUB_PRODUCT_MODE() open_cfw_retained_product_mode()
#endif
#ifndef OPEN_CFW_SENSOR_HUB_OTA_ACTIVE
#define OPEN_CFW_SENSOR_HUB_OTA_ACTIVE() open_cfw_retained_ota_active()
#endif
#ifndef OPEN_CFW_SENSOR_HUB_ROLE_GETTER
#define OPEN_CFW_SENSOR_HUB_ROLE_GETTER() open_cfw_retained_glasses_role()
#endif

void *open_cfw_retained_ui_object_create(void *parent);
void *open_cfw_retained_ui_label_create(void *parent);
void open_cfw_retained_ui_set_size(void *object, int32_t width, int32_t height);
void open_cfw_retained_ui_set_position(void *object, int32_t x, int32_t y);
void open_cfw_retained_ui_set_text(void *label, const char *text);
void open_cfw_retained_ui_set_font(
    void *label, uint32_t font, uint32_t selector);
void open_cfw_retained_ui_set_color(
    void *object, uint32_t color, uint32_t selector);
void open_cfw_retained_ui_set_alignment(
    void *object, uint32_t alignment, uint32_t selector);
void open_cfw_retained_ui_set_pad_top(
    void *object, int32_t value, uint32_t selector);
void open_cfw_retained_ui_set_pad_bottom(
    void *object, int32_t value, uint32_t selector);
void open_cfw_retained_ui_set_pad_left(
    void *object, int32_t value, uint32_t selector);
void open_cfw_retained_ui_set_pad_right(
    void *object, int32_t value, uint32_t selector);
uint32_t open_cfw_retained_translate_language(uint32_t string_id);
const char *open_cfw_retained_translate_string(
    uint32_t string_id, uint32_t language);

#ifndef OPEN_CFW_SENSOR_HUB_UI_OBJECT_CREATE
#define OPEN_CFW_SENSOR_HUB_UI_OBJECT_CREATE(p) open_cfw_retained_ui_object_create((p))
#endif
#ifndef OPEN_CFW_SENSOR_HUB_UI_LABEL_CREATE
#define OPEN_CFW_SENSOR_HUB_UI_LABEL_CREATE(p) open_cfw_retained_ui_label_create((p))
#endif
#ifndef OPEN_CFW_SENSOR_HUB_UI_SET_SIZE
#define OPEN_CFW_SENSOR_HUB_UI_SET_SIZE(o, w, h) \
    open_cfw_retained_ui_set_size((o), (w), (h))
#endif
#ifndef OPEN_CFW_SENSOR_HUB_UI_SET_POSITION
#define OPEN_CFW_SENSOR_HUB_UI_SET_POSITION(o, x, y) \
    open_cfw_retained_ui_set_position((o), (x), (y))
#endif
#ifndef OPEN_CFW_SENSOR_HUB_UI_SET_TEXT
#define OPEN_CFW_SENSOR_HUB_UI_SET_TEXT(o, s) open_cfw_retained_ui_set_text((o), (s))
#endif
#ifndef OPEN_CFW_SENSOR_HUB_UI_SET_FONT
#define OPEN_CFW_SENSOR_HUB_UI_SET_FONT(o, f) \
    open_cfw_retained_ui_set_font((o), (f), 0u)
#endif
#ifndef OPEN_CFW_SENSOR_HUB_UI_SET_COLOR
#define OPEN_CFW_SENSOR_HUB_UI_SET_COLOR(o, c) \
    open_cfw_retained_ui_set_color((o), (c), 0u)
#endif
#ifndef OPEN_CFW_SENSOR_HUB_UI_SET_ALIGNMENT
#define OPEN_CFW_SENSOR_HUB_UI_SET_ALIGNMENT(o, a) \
    open_cfw_retained_ui_set_alignment((o), (a), 0u)
#endif
#ifndef OPEN_CFW_SENSOR_HUB_UI_SET_PADDING_ALL
#define OPEN_CFW_SENSOR_HUB_UI_SET_PADDING_ALL(o, v, s) \
    do { \
        open_cfw_retained_ui_set_pad_top((o), (v), (s)); \
        open_cfw_retained_ui_set_pad_bottom((o), (v), (s)); \
        open_cfw_retained_ui_set_pad_left((o), (v), (s)); \
        open_cfw_retained_ui_set_pad_right((o), (v), (s)); \
    } while (0)
#endif
#ifndef OPEN_CFW_SENSOR_HUB_TRANSLATE
#define OPEN_CFW_SENSOR_HUB_TRANSLATE(i) \
    open_cfw_retained_translate_string( \
        (i), open_cfw_retained_translate_language((i)))
#endif

enum {
    OPEN_CFW_SENSOR_HUB_THREAD_INDEX = 5u,
    OPEN_CFW_SENSOR_HUB_QUEUE_DEPTH = 50u,
    OPEN_CFW_SENSOR_HUB_HANDLER_COUNT = 8u,
    OPEN_CFW_SENSOR_HUB_MESSAGE_SET_MODE = 1u,
    OPEN_CFW_SENSOR_HUB_MESSAGE_ALS_SAMPLE = 2u,
    OPEN_CFW_SENSOR_HUB_MESSAGE_CALIBRATION = 3u,
    OPEN_CFW_SENSOR_HUB_MESSAGE_PRODUCT_MODE = 4u,
    OPEN_CFW_SENSOR_HUB_MESSAGE_OPEN = 5u,
    OPEN_CFW_SENSOR_HUB_MESSAGE_CLOSE = 6u,
    OPEN_CFW_SENSOR_HUB_MESSAGE_CALIB_INIT = 8u,
    OPEN_CFW_SENSOR_HUB_ROLE_BLOCKED = 2u,
    OPEN_CFW_SENSOR_HUB_STRING_CALIBRATING_LEFT = 0x77be3cu,
    OPEN_CFW_SENSOR_HUB_STRING_CALIBRATING_RIGHT = 0x77be54u,
    OPEN_CFW_SENSOR_HUB_STRING_SUCCESS_LEFT = 0x75a3b0u,
    OPEN_CFW_SENSOR_HUB_STRING_SUCCESS_RIGHT = 0x75a3d4u
};

void open_cfw_sensor_hub_thread_init(void);
void open_cfw_sensor_hub_resource_init(void);
void open_cfw_sensor_hub_thread_terminate(void);
void open_cfw_sensor_hub_state_enter(void);
void open_cfw_sensor_hub_state_exit(void);
void open_cfw_sensor_hub_thread_entry(void *argument);
void open_cfw_sensor_hub_message_process(const void *record);
int32_t open_cfw_sensor_hub_send_id8(void);
int32_t open_cfw_sensor_hub_timer_start(uint32_t ticks);
int32_t open_cfw_sensor_hub_timer_stop(void);
void open_cfw_sensor_hub_imu_read(void);
void open_cfw_sensor_hub_calibration_init_wrapper(const void *record);
void open_cfw_sensor_hub_collection_handler(const void *record);
int32_t open_cfw_sensor_hub_send(const void *record);
int32_t open_cfw_sensor_hub_send_id1(uint8_t mode);
int32_t open_cfw_sensor_hub_send_id4(uint8_t mode);
int32_t open_cfw_sensor_hub_send_id3(void);
void open_cfw_sensor_hub_als_timer_callback(void *argument);
void open_cfw_sensor_hub_set_mode_handler(const void *record);
void open_cfw_sensor_hub_calibration_init(void);
void open_cfw_sensor_hub_empty_hook(void);
void open_cfw_sensor_hub_role_init(void);
uint16_t open_cfw_sensor_hub_role_get(void);
int32_t open_cfw_sensor_hub_open(uint32_t function);
int32_t open_cfw_sensor_hub_close(uint32_t function);
int32_t open_cfw_sensor_hub_parameter_config(
    uint8_t type, const uint32_t *parameters);
void open_cfw_sensor_hub_function_open_handler(const void *record);
void open_cfw_sensor_hub_function_close_handler(const void *record);
void open_cfw_sensor_hub_labels_update(
    void *object, int32_t value, uint32_t selector);
void open_cfw_sensor_hub_calibration_display_update(void *parent);
void open_cfw_sensor_hub_calibration_success_display(void);

#if OPEN_CFW_SENSOR_HUB_SELECTOR == 0 || OPEN_CFW_SENSOR_HUB_SELECTOR == 1
__attribute__((noinline)) void open_cfw_sensor_hub_thread_init(void)
{
    OPEN_CFW_SENSOR_HUB_THREAD_ID = OPEN_CFW_SENSOR_HUB_THREAD_NEW(
        open_cfw_sensor_hub_thread_entry, NULL,
        OPEN_CFW_SENSOR_HUB_THREAD_ATTRIBUTES);
}
#endif

#if OPEN_CFW_SENSOR_HUB_SELECTOR == 0 || OPEN_CFW_SENSOR_HUB_SELECTOR == 2
__attribute__((noinline)) void open_cfw_sensor_hub_resource_init(void)
{
    if (OPEN_CFW_SENSOR_HUB_QUEUE_ID == NULL) {
        OPEN_CFW_SENSOR_HUB_QUEUE_ID = OPEN_CFW_SENSOR_HUB_QUEUE_NEW(
            OPEN_CFW_SENSOR_HUB_QUEUE_DEPTH,
            sizeof(struct open_cfw_sensor_hub_record), NULL);
    }
    if (OPEN_CFW_SENSOR_HUB_TIMER_ID == NULL) {
        OPEN_CFW_SENSOR_HUB_TIMER_ID = OPEN_CFW_SENSOR_HUB_TIMER_NEW(
            open_cfw_sensor_hub_als_timer_callback, 1u, NULL,
            OPEN_CFW_SENSOR_HUB_TIMER_ATTRIBUTES);
    }
}
#endif

#if OPEN_CFW_SENSOR_HUB_SELECTOR == 0 || OPEN_CFW_SENSOR_HUB_SELECTOR == 3
__attribute__((noinline)) void open_cfw_sensor_hub_thread_terminate(void)
{
    if (OPEN_CFW_SENSOR_HUB_THREAD_ID != NULL) {
        (void)OPEN_CFW_SENSOR_HUB_THREAD_TERMINATE(OPEN_CFW_SENSOR_HUB_THREAD_ID);
        OPEN_CFW_SENSOR_HUB_THREAD_ID = NULL;
    }
}
#endif

#if OPEN_CFW_SENSOR_HUB_SELECTOR == 0 || OPEN_CFW_SENSOR_HUB_SELECTOR == 4
__attribute__((noinline)) void open_cfw_sensor_hub_state_enter(void)
{
    OPEN_CFW_SENSOR_HUB_STATE_ACTIVE(OPEN_CFW_SENSOR_HUB_THREAD_INDEX);
}
#endif

#if OPEN_CFW_SENSOR_HUB_SELECTOR == 0 || OPEN_CFW_SENSOR_HUB_SELECTOR == 5
__attribute__((noinline)) void open_cfw_sensor_hub_state_exit(void)
{
    OPEN_CFW_SENSOR_HUB_STATE_EXIT(OPEN_CFW_SENSOR_HUB_THREAD_INDEX);
}
#endif

#if OPEN_CFW_SENSOR_HUB_SELECTOR == 0 || OPEN_CFW_SENSOR_HUB_SELECTOR == 6
__attribute__((noinline)) void open_cfw_sensor_hub_thread_entry(void *argument)
{
    struct open_cfw_sensor_hub_record record;
    (void)argument;
    open_cfw_sensor_hub_state_enter();
    open_cfw_sensor_hub_resource_init();
    open_cfw_sensor_hub_calibration_init();
    open_cfw_sensor_hub_role_init();
    OPEN_CFW_SENSOR_HUB_TIMER_ENABLED = 1u;
    open_cfw_retained_als_initialize();
    if (OPEN_CFW_SENSOR_HUB_PRODUCT_MODE() == 1u) {
        (void)open_cfw_sensor_hub_send_id4(4u);
        open_cfw_retained_als_open();
    } else if (open_cfw_sensor_hub_role_get() == 3u) {
        open_cfw_retained_imu_initialize(0u);
    } else {
        open_cfw_retained_imu_reset();
    }
    open_cfw_sensor_hub_state_exit();
    for (;;) {
        if (OPEN_CFW_SENSOR_HUB_QUEUE_GET(
                OPEN_CFW_SENSOR_HUB_QUEUE_ID, &record, NULL, UINT32_MAX) == 0) {
            OPEN_CFW_SENSOR_HUB_CRITICAL_ENTER();
            open_cfw_sensor_hub_message_process(&record);
            OPEN_CFW_SENSOR_HUB_CRITICAL_EXIT();
        }
    }
}
#endif

#if OPEN_CFW_SENSOR_HUB_SELECTOR == 0 || OPEN_CFW_SENSOR_HUB_SELECTOR == 7
__attribute__((noinline)) void open_cfw_sensor_hub_message_process(
    const void *record)
{
    const struct open_cfw_sensor_hub_record *message = record;
    uint32_t index;
    if (message == NULL) {
        return;
    }
    for (index = 0u; index < OPEN_CFW_SENSOR_HUB_HANDLER_COUNT; ++index) {
        volatile struct open_cfw_sensor_hub_handler_slot *slot =
            &OPEN_CFW_SENSOR_HUB_HANDLER_TABLE[index];
        if (slot->id == message->id && slot->handler != NULL) {
            slot->handler(message);
            return;
        }
    }
}
#endif

#define OPEN_CFW_SENSOR_HUB_DEFINE_SEND0(selector, name, message_id) \
    /* selector-isolated record sender */ \
    __attribute__((noinline)) int32_t name(void) \
    { \
        const struct open_cfw_sensor_hub_record record = { \
            (uint16_t)(message_id), 0u, 0u}; \
        return open_cfw_sensor_hub_send(&record); \
    }

#if OPEN_CFW_SENSOR_HUB_SELECTOR == 0 || OPEN_CFW_SENSOR_HUB_SELECTOR == 8
OPEN_CFW_SENSOR_HUB_DEFINE_SEND0(8, open_cfw_sensor_hub_send_id8,
                                 OPEN_CFW_SENSOR_HUB_MESSAGE_CALIB_INIT)
#endif

#if OPEN_CFW_SENSOR_HUB_SELECTOR == 0 || OPEN_CFW_SENSOR_HUB_SELECTOR == 9
__attribute__((noinline)) int32_t open_cfw_sensor_hub_timer_start(uint32_t ticks)
{
    if (OPEN_CFW_SENSOR_HUB_TIMER_ID == NULL) {
        return -1;
    }
    return OPEN_CFW_SENSOR_HUB_TIMER_START(OPEN_CFW_SENSOR_HUB_TIMER_ID, ticks);
}
#endif

#if OPEN_CFW_SENSOR_HUB_SELECTOR == 0 || OPEN_CFW_SENSOR_HUB_SELECTOR == 10
__attribute__((noinline)) int32_t open_cfw_sensor_hub_timer_stop(void)
{
    if (OPEN_CFW_SENSOR_HUB_TIMER_ID == NULL) {
        return -1;
    }
    return OPEN_CFW_SENSOR_HUB_TIMER_STOP(OPEN_CFW_SENSOR_HUB_TIMER_ID);
}
#endif

#if OPEN_CFW_SENSOR_HUB_SELECTOR == 0 || OPEN_CFW_SENSOR_HUB_SELECTOR == 11
__attribute__((noinline)) void open_cfw_sensor_hub_imu_read(void)
{
    open_cfw_retained_imu_read_data(OPEN_CFW_SENSOR_HUB_LAST_TICK);
}
#endif

#if OPEN_CFW_SENSOR_HUB_SELECTOR == 0 || OPEN_CFW_SENSOR_HUB_SELECTOR == 12
__attribute__((noinline)) void open_cfw_sensor_hub_calibration_init_wrapper(
    const void *record)
{
    (void)record;
    open_cfw_sensor_hub_calibration_init();
}
#endif

#if OPEN_CFW_SENSOR_HUB_SELECTOR == 0 || OPEN_CFW_SENSOR_HUB_SELECTOR == 13
__attribute__((noinline)) void open_cfw_sensor_hub_collection_handler(
    const void *record)
{
    const struct open_cfw_sensor_hub_record *message = record;
    if (message == NULL) {
        return;
    }
    if (message->argument == 1u) {
        open_cfw_retained_imu_start_collection();
    } else if (message->argument == 0u) {
        open_cfw_retained_imu_stop_collection();
    }
}
#endif

#if OPEN_CFW_SENSOR_HUB_SELECTOR == 0 || OPEN_CFW_SENSOR_HUB_SELECTOR == 14
__attribute__((noinline)) int32_t open_cfw_sensor_hub_send(const void *record)
{
    if (record == NULL || OPEN_CFW_SENSOR_HUB_QUEUE_ID == NULL) {
        return -1;
    }
    return OPEN_CFW_SENSOR_HUB_QUEUE_PUT(
        OPEN_CFW_SENSOR_HUB_QUEUE_ID, record, 0u, 0u);
}
#endif

#define OPEN_CFW_SENSOR_HUB_DEFINE_SEND1(name, message_id) \
    __attribute__((noinline)) int32_t name(uint8_t value) \
    { \
        const struct open_cfw_sensor_hub_record record = { \
            (uint16_t)(message_id), 0u, value}; \
        return open_cfw_sensor_hub_send(&record); \
    }

#if OPEN_CFW_SENSOR_HUB_SELECTOR == 0 || OPEN_CFW_SENSOR_HUB_SELECTOR == 15
OPEN_CFW_SENSOR_HUB_DEFINE_SEND1(open_cfw_sensor_hub_send_id1,
                                 OPEN_CFW_SENSOR_HUB_MESSAGE_SET_MODE)
#endif

#if OPEN_CFW_SENSOR_HUB_SELECTOR == 0 || OPEN_CFW_SENSOR_HUB_SELECTOR == 16
OPEN_CFW_SENSOR_HUB_DEFINE_SEND1(open_cfw_sensor_hub_send_id4,
                                 OPEN_CFW_SENSOR_HUB_MESSAGE_PRODUCT_MODE)
#endif

#if OPEN_CFW_SENSOR_HUB_SELECTOR == 0 || OPEN_CFW_SENSOR_HUB_SELECTOR == 17
OPEN_CFW_SENSOR_HUB_DEFINE_SEND0(17, open_cfw_sensor_hub_send_id3,
                                 OPEN_CFW_SENSOR_HUB_MESSAGE_CALIBRATION)
#endif

#if OPEN_CFW_SENSOR_HUB_SELECTOR == 0 || OPEN_CFW_SENSOR_HUB_SELECTOR == 18
__attribute__((noinline)) void open_cfw_sensor_hub_als_timer_callback(void *argument)
{
    const struct open_cfw_sensor_hub_record record = {
        OPEN_CFW_SENSOR_HUB_MESSAGE_ALS_SAMPLE, 0u, 0u};
    (void)argument;
    if (OPEN_CFW_SENSOR_HUB_TIMER_ENABLED == 0u ||
        OPEN_CFW_SENSOR_HUB_OTA_ACTIVE() != 0u) {
        return;
    }
    OPEN_CFW_SENSOR_HUB_LAST_TICK = OPEN_CFW_SENSOR_HUB_TICK();
    (void)open_cfw_sensor_hub_send(&record);
}
#endif

#if OPEN_CFW_SENSOR_HUB_SELECTOR == 0 || OPEN_CFW_SENSOR_HUB_SELECTOR == 19
__attribute__((noinline)) void open_cfw_sensor_hub_set_mode_handler(
    const void *record)
{
    const struct open_cfw_sensor_hub_record *message = record;
    if (message != NULL && message->argument < 5u) {
        OPEN_CFW_SENSOR_HUB_TIMER_ENABLED = 0u;
        open_cfw_retained_imu_set_work_mode((uint8_t)message->argument);
        OPEN_CFW_SENSOR_HUB_TIMER_ENABLED = 1u;
    }
}
#endif

#if OPEN_CFW_SENSOR_HUB_SELECTOR == 0 || OPEN_CFW_SENSOR_HUB_SELECTOR == 20
__attribute__((noinline)) void open_cfw_sensor_hub_calibration_init(void)
{
    float first[3] = {0.0f, 0.0f, 0.0f};
    float second[3] = {0.0f, 0.0f, 0.0f};
    struct open_cfw_sensor_hub_calibration matrix;
    open_cfw_retained_zero(&matrix, sizeof(matrix));
    open_cfw_retained_calibration_load(first, second, &matrix);
    open_cfw_retained_imu_apply_calibration(first, second, &matrix);
}
#endif

#if OPEN_CFW_SENSOR_HUB_SELECTOR == 0 || OPEN_CFW_SENSOR_HUB_SELECTOR == 21
__attribute__((noinline)) void open_cfw_sensor_hub_empty_hook(void)
{
}
#endif

#if OPEN_CFW_SENSOR_HUB_SELECTOR == 0 || OPEN_CFW_SENSOR_HUB_SELECTOR == 22
__attribute__((noinline)) void open_cfw_sensor_hub_role_init(void)
{
    uint32_t role = OPEN_CFW_SENSOR_HUB_ROLE_GETTER();
    if ((uint8_t)role == 1u) {
        OPEN_CFW_SENSOR_HUB_ROLE = 3u;
    } else if ((uint8_t)role == 2u) {
        OPEN_CFW_SENSOR_HUB_ROLE = 2u;
    }
}
#endif

#if OPEN_CFW_SENSOR_HUB_SELECTOR == 0 || OPEN_CFW_SENSOR_HUB_SELECTOR == 23
__attribute__((noinline)) uint16_t open_cfw_sensor_hub_role_get(void)
{
    return OPEN_CFW_SENSOR_HUB_ROLE;
}
#endif

#if OPEN_CFW_SENSOR_HUB_SELECTOR == 0 || OPEN_CFW_SENSOR_HUB_SELECTOR == 24
__attribute__((noinline)) int32_t open_cfw_sensor_hub_open(uint32_t function)
{
    const struct open_cfw_sensor_hub_record record = {
        OPEN_CFW_SENSOR_HUB_MESSAGE_OPEN, 0u, (uint8_t)function};
    if (open_cfw_sensor_hub_role_get() == OPEN_CFW_SENSOR_HUB_ROLE_BLOCKED) {
        return -1;
    }
    return open_cfw_sensor_hub_send(&record);
}
#endif

#if OPEN_CFW_SENSOR_HUB_SELECTOR == 0 || OPEN_CFW_SENSOR_HUB_SELECTOR == 25
__attribute__((noinline)) int32_t open_cfw_sensor_hub_close(uint32_t function)
{
    const struct open_cfw_sensor_hub_record record = {
        OPEN_CFW_SENSOR_HUB_MESSAGE_CLOSE, 0u, (uint8_t)function};
    if (open_cfw_sensor_hub_role_get() == OPEN_CFW_SENSOR_HUB_ROLE_BLOCKED) {
        return -1;
    }
    return open_cfw_sensor_hub_send(&record);
}
#endif

#if OPEN_CFW_SENSOR_HUB_SELECTOR == 0 || OPEN_CFW_SENSOR_HUB_SELECTOR == 26
__attribute__((noinline)) int32_t open_cfw_sensor_hub_parameter_config(
    uint8_t type, const uint32_t *parameters)
{
    if (parameters == NULL ||
        open_cfw_sensor_hub_role_get() == OPEN_CFW_SENSOR_HUB_ROLE_BLOCKED) {
        return -1;
    }
    if (type == 1u) {
        open_cfw_retained_imu_set_motion_threshold(parameters[0]);
    } else if (type == 2u) {
        open_cfw_retained_imu_set_motion_period(parameters[0], parameters[1]);
    } else if (type == 5u) {
        open_cfw_retained_imu_set_accel_config(parameters[0]);
    }
    return 0;
}
#endif

#if OPEN_CFW_SENSOR_HUB_SELECTOR == 0 || OPEN_CFW_SENSOR_HUB_SELECTOR == 27
__attribute__((noinline)) void open_cfw_sensor_hub_function_open_handler(
    const void *record)
{
    const struct open_cfw_sensor_hub_record *message = record;
    uint8_t function;
    if (message == NULL || message->argument >= 6u) {
        return;
    }
    function = (uint8_t)message->argument;
    if (function == 1u || function == 5u) {
        if (function == 1u) {
            open_cfw_retained_imu_set_state_zero(1u);
        } else {
            open_cfw_retained_imu_set_state_three(1u);
        }
        if (open_cfw_retained_imu_state_two() == 1u ||
            open_cfw_retained_imu_state_one() == 1u) {
            return;
        }
        (void)open_cfw_sensor_hub_send_id1(0u);
    } else if (function == 2u) {
        open_cfw_retained_imu_set_state_one(1u);
        if (open_cfw_retained_imu_state_two() != 1u) {
            (void)open_cfw_sensor_hub_send_id1(2u);
        }
    } else if (function == 3u) {
        open_cfw_retained_imu_set_state_two(1u);
        (void)open_cfw_sensor_hub_send_id1(1u);
    } else if (function == 4u) {
        open_cfw_retained_als_open();
    }
}
#endif

#if OPEN_CFW_SENSOR_HUB_SELECTOR == 0 || OPEN_CFW_SENSOR_HUB_SELECTOR == 28
__attribute__((noinline)) void open_cfw_sensor_hub_function_close_handler(
    const void *record)
{
    const struct open_cfw_sensor_hub_record *message = record;
    uint8_t function;
    if (message == NULL || message->argument >= 6u) {
        return;
    }
    function = (uint8_t)message->argument;
    if (function == 1u) {
        open_cfw_retained_imu_set_state_zero(0u);
    } else if (function == 2u) {
        open_cfw_retained_imu_set_state_one(0u);
    } else if (function == 3u) {
        open_cfw_retained_imu_set_state_two(0u);
    } else if (function == 4u) {
        open_cfw_retained_als_close();
        return;
    } else if (function == 5u) {
        open_cfw_retained_imu_set_state_three(0u);
    }
    if (open_cfw_retained_imu_state_two() == 1u) {
        (void)open_cfw_sensor_hub_send_id1(1u);
    } else if (open_cfw_retained_imu_state_one() == 1u) {
        (void)open_cfw_sensor_hub_send_id1(2u);
    } else if (open_cfw_retained_imu_state_zero() == 1u ||
               open_cfw_retained_imu_state_three() == 1u) {
        (void)open_cfw_sensor_hub_send_id1(0u);
    } else {
        open_cfw_retained_imu_reset();
    }
}
#endif

#if OPEN_CFW_SENSOR_HUB_SELECTOR == 0 || OPEN_CFW_SENSOR_HUB_SELECTOR == 29
__attribute__((noinline)) void open_cfw_sensor_hub_labels_update(
    void *object, int32_t value, uint32_t selector)
{
    if (object != NULL) {
        OPEN_CFW_SENSOR_HUB_UI_SET_PADDING_ALL(object, value, selector);
    }
}
#endif

#if OPEN_CFW_SENSOR_HUB_SELECTOR == 0 || OPEN_CFW_SENSOR_HUB_SELECTOR == 30
__attribute__((noinline)) void open_cfw_sensor_hub_calibration_display_update(
    void *parent)
{
    void *screen = OPEN_CFW_SENSOR_HUB_UI_OBJECT_CREATE(parent);
    void *title;
    void *status;
    if (screen == NULL) {
        return;
    }
    OPEN_CFW_SENSOR_HUB_UI_SET_SIZE(screen, 576, 288);
    OPEN_CFW_SENSOR_HUB_UI_SET_POSITION(screen, 0, 0);
    OPEN_CFW_SENSOR_HUB_UI_SET_COLOR(screen, 0u);
    OPEN_CFW_SENSOR_HUB_CALIBRATION_SCREEN = screen;
    title = OPEN_CFW_SENSOR_HUB_UI_LABEL_CREATE(screen);
    status = OPEN_CFW_SENSOR_HUB_UI_LABEL_CREATE(screen);
    OPEN_CFW_SENSOR_HUB_CALIBRATION_LABEL_LEFT = title;
    OPEN_CFW_SENSOR_HUB_CALIBRATION_LABEL_RIGHT = status;
    if (title != NULL) {
        OPEN_CFW_SENSOR_HUB_UI_SET_POSITION(title, 138, 99);
        OPEN_CFW_SENSOR_HUB_UI_SET_FONT(title, 28u);
        OPEN_CFW_SENSOR_HUB_UI_SET_TEXT(
            title, OPEN_CFW_SENSOR_HUB_TRANSLATE(
                OPEN_CFW_SENSOR_HUB_STRING_CALIBRATING_LEFT));
        open_cfw_sensor_hub_labels_update(title, 0u, 0u);
    }
    if (status != NULL) {
        OPEN_CFW_SENSOR_HUB_UI_SET_POSITION(status, 297, 143);
        OPEN_CFW_SENSOR_HUB_UI_SET_FONT(status, 28u);
        OPEN_CFW_SENSOR_HUB_UI_SET_TEXT(
            status, OPEN_CFW_SENSOR_HUB_TRANSLATE(
                OPEN_CFW_SENSOR_HUB_STRING_CALIBRATING_RIGHT));
        open_cfw_sensor_hub_labels_update(status, 0u, 0u);
    }
}
#endif

#if OPEN_CFW_SENSOR_HUB_SELECTOR == 0 || OPEN_CFW_SENSOR_HUB_SELECTOR == 31
__attribute__((noinline)) void open_cfw_sensor_hub_calibration_success_display(void)
{
    if (OPEN_CFW_SENSOR_HUB_CALIBRATION_LABEL_LEFT != NULL) {
        OPEN_CFW_SENSOR_HUB_UI_SET_TEXT(
            OPEN_CFW_SENSOR_HUB_CALIBRATION_LABEL_LEFT,
            OPEN_CFW_SENSOR_HUB_TRANSLATE(
                OPEN_CFW_SENSOR_HUB_STRING_SUCCESS_LEFT));
    }
    if (OPEN_CFW_SENSOR_HUB_CALIBRATION_LABEL_RIGHT != NULL) {
        OPEN_CFW_SENSOR_HUB_UI_SET_TEXT(
            OPEN_CFW_SENSOR_HUB_CALIBRATION_LABEL_RIGHT,
            OPEN_CFW_SENSOR_HUB_TRANSLATE(
                OPEN_CFW_SENSOR_HUB_STRING_SUCCESS_RIGHT));
        OPEN_CFW_SENSOR_HUB_UI_SET_ALIGNMENT(
            OPEN_CFW_SENSOR_HUB_CALIBRATION_LABEL_RIGHT, 1u);
    }
}
#endif
