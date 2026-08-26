#ifndef OPEN_CFW_SENSOR_HUB_HOST_H
#define OPEN_CFW_SENSOR_HUB_HOST_H

#include <stddef.h>
#include <stdint.h>

struct open_cfw_sensor_hub_handler_slot;
struct open_cfw_sensor_hub_calibration;

extern void *host_sensor_hub_thread_id;
extern void *host_sensor_hub_queue_id;
extern void *host_sensor_hub_timer_id;
extern uint32_t host_sensor_hub_last_tick;
extern uint32_t host_sensor_hub_timer_enabled;
extern uint16_t host_sensor_hub_role;
extern void *host_sensor_hub_calibration_screen;
extern void *host_sensor_hub_calibration_label_left;
extern void *host_sensor_hub_calibration_label_right;
extern uint8_t host_sensor_hub_handler_storage[128];

void *host_sensor_hub_thread_new(
    void (*entry)(void *), void *argument, const void *attributes);
int32_t host_sensor_hub_thread_terminate(void *thread_id);
void *host_sensor_hub_queue_new(
    uint32_t count, uint32_t size, const void *attributes);
int32_t host_sensor_hub_queue_put(
    void *queue_id, const void *message, uint8_t priority, uint32_t timeout);
int32_t host_sensor_hub_queue_get(
    void *queue_id, void *message, uint8_t *priority, uint32_t timeout);
void *host_sensor_hub_timer_new(
    void (*callback)(void *), uint32_t type, void *argument,
    const void *attributes);
int32_t host_sensor_hub_timer_start(void *timer_id, uint32_t ticks);
int32_t host_sensor_hub_timer_stop(void *timer_id);
uint32_t host_sensor_hub_tick(void);
void host_sensor_hub_state_active(uint32_t index);
void host_sensor_hub_state_exit(uint32_t index);
void host_sensor_hub_critical_enter(void);
void host_sensor_hub_critical_exit(void);
uint32_t host_sensor_hub_product_mode(void);
uint32_t host_sensor_hub_ota_active(void);
uint32_t host_sensor_hub_role_getter(void);
void host_sensor_hub_als_initialize(void);
void host_sensor_hub_als_open(void);
void host_sensor_hub_als_close(void);
void host_sensor_hub_imu_reset(void);
void host_sensor_hub_imu_initialize(uint8_t mode);
void host_sensor_hub_imu_read(uint32_t tick);
void host_sensor_hub_imu_start(void);
void host_sensor_hub_imu_stop(void);
void host_sensor_hub_imu_set_mode(uint8_t mode);
void host_sensor_hub_imu_threshold(uint32_t value);
void host_sensor_hub_imu_period(uint32_t first, uint32_t second);
void host_sensor_hub_imu_accel(uint32_t value);
uint8_t host_sensor_hub_state_zero(void);
uint8_t host_sensor_hub_state_one(void);
uint8_t host_sensor_hub_state_two(void);
uint8_t host_sensor_hub_state_three(void);
void host_sensor_hub_set_state_zero(uint8_t value);
void host_sensor_hub_set_state_one(uint8_t value);
void host_sensor_hub_set_state_two(uint8_t value);
void host_sensor_hub_set_state_three(uint8_t value);
void host_sensor_hub_calibration_load(
    float *a, float *b, struct open_cfw_sensor_hub_calibration *matrix);
void host_sensor_hub_calibration_apply(
    const float *a, const float *b,
    const struct open_cfw_sensor_hub_calibration *matrix);
void host_sensor_hub_zero(void *destination, uint32_t size);
void *host_sensor_hub_object_create(void *parent);
void *host_sensor_hub_label_create(void *parent);
void host_sensor_hub_ui_size(void *object, int32_t width, int32_t height);
void host_sensor_hub_ui_position(void *object, int32_t x, int32_t y);
void host_sensor_hub_ui_text(void *object, const char *text);
void host_sensor_hub_ui_font(void *object, uint32_t font, uint32_t selector);
void host_sensor_hub_ui_color(void *object, uint32_t color, uint32_t selector);
void host_sensor_hub_ui_alignment(
    void *object, uint32_t alignment, uint32_t selector);
void host_sensor_hub_ui_padding(
    void *object, int32_t padding, uint32_t selector);
uint32_t host_sensor_hub_translate_language(uint32_t id);
const char *host_sensor_hub_translate_string(uint32_t id, uint32_t language);
void host_sensor_hub_reset(void);
void host_sensor_hub_register_capture(uint16_t id);

#define OPEN_CFW_SENSOR_HUB_THREAD_ID host_sensor_hub_thread_id
#define OPEN_CFW_SENSOR_HUB_QUEUE_ID host_sensor_hub_queue_id
#define OPEN_CFW_SENSOR_HUB_TIMER_ID host_sensor_hub_timer_id
#define OPEN_CFW_SENSOR_HUB_LAST_TICK host_sensor_hub_last_tick
#define OPEN_CFW_SENSOR_HUB_TIMER_ENABLED host_sensor_hub_timer_enabled
#define OPEN_CFW_SENSOR_HUB_ROLE host_sensor_hub_role
#define OPEN_CFW_SENSOR_HUB_CALIBRATION_SCREEN host_sensor_hub_calibration_screen
#define OPEN_CFW_SENSOR_HUB_CALIBRATION_LABEL_LEFT \
    host_sensor_hub_calibration_label_left
#define OPEN_CFW_SENSOR_HUB_CALIBRATION_LABEL_RIGHT \
    host_sensor_hub_calibration_label_right
#define OPEN_CFW_SENSOR_HUB_HANDLER_TABLE \
    ((volatile struct open_cfw_sensor_hub_handler_slot *)(void *) \
        host_sensor_hub_handler_storage)
#define OPEN_CFW_SENSOR_HUB_THREAD_ATTRIBUTES ((const void *)0x759048u)
#define OPEN_CFW_SENSOR_HUB_TIMER_ATTRIBUTES ((const void *)0x788660u)
#define OPEN_CFW_SENSOR_HUB_THREAD_NEW(e, a, p) \
    host_sensor_hub_thread_new((e), (a), (p))
#define OPEN_CFW_SENSOR_HUB_THREAD_TERMINATE(i) \
    host_sensor_hub_thread_terminate((i))
#define OPEN_CFW_SENSOR_HUB_QUEUE_NEW(c, s, a) \
    host_sensor_hub_queue_new((c), (s), (a))
#define OPEN_CFW_SENSOR_HUB_QUEUE_PUT(q, m, p, t) \
    host_sensor_hub_queue_put((q), (m), (p), (t))
#define OPEN_CFW_SENSOR_HUB_QUEUE_GET(q, m, p, t) \
    host_sensor_hub_queue_get((q), (m), (p), (t))
#define OPEN_CFW_SENSOR_HUB_TIMER_NEW(c, t, a, p) \
    host_sensor_hub_timer_new((c), (t), (a), (p))
#define OPEN_CFW_SENSOR_HUB_TIMER_START(i, t) \
    host_sensor_hub_timer_start((i), (t))
#define OPEN_CFW_SENSOR_HUB_TIMER_STOP(i) host_sensor_hub_timer_stop((i))
#define OPEN_CFW_SENSOR_HUB_TICK() host_sensor_hub_tick()
#define OPEN_CFW_SENSOR_HUB_STATE_ACTIVE(i) host_sensor_hub_state_active((i))
#define OPEN_CFW_SENSOR_HUB_STATE_EXIT(i) host_sensor_hub_state_exit((i))
#define OPEN_CFW_SENSOR_HUB_CRITICAL_ENTER() host_sensor_hub_critical_enter()
#define OPEN_CFW_SENSOR_HUB_CRITICAL_EXIT() host_sensor_hub_critical_exit()
#define OPEN_CFW_SENSOR_HUB_PRODUCT_MODE() host_sensor_hub_product_mode()
#define OPEN_CFW_SENSOR_HUB_OTA_ACTIVE() host_sensor_hub_ota_active()
#define OPEN_CFW_SENSOR_HUB_ROLE_GETTER() host_sensor_hub_role_getter()

#define open_cfw_retained_als_initialize host_sensor_hub_als_initialize
#define open_cfw_retained_als_open host_sensor_hub_als_open
#define open_cfw_retained_als_close host_sensor_hub_als_close
#define open_cfw_retained_imu_reset host_sensor_hub_imu_reset
#define open_cfw_retained_imu_initialize host_sensor_hub_imu_initialize
#define open_cfw_retained_imu_read_data host_sensor_hub_imu_read
#define open_cfw_retained_imu_start_collection host_sensor_hub_imu_start
#define open_cfw_retained_imu_stop_collection host_sensor_hub_imu_stop
#define open_cfw_retained_imu_set_work_mode host_sensor_hub_imu_set_mode
#define open_cfw_retained_imu_set_motion_threshold host_sensor_hub_imu_threshold
#define open_cfw_retained_imu_set_motion_period host_sensor_hub_imu_period
#define open_cfw_retained_imu_set_accel_config host_sensor_hub_imu_accel
#define open_cfw_retained_imu_state_zero host_sensor_hub_state_zero
#define open_cfw_retained_imu_state_one host_sensor_hub_state_one
#define open_cfw_retained_imu_state_two host_sensor_hub_state_two
#define open_cfw_retained_imu_state_three host_sensor_hub_state_three
#define open_cfw_retained_imu_set_state_zero host_sensor_hub_set_state_zero
#define open_cfw_retained_imu_set_state_one host_sensor_hub_set_state_one
#define open_cfw_retained_imu_set_state_two host_sensor_hub_set_state_two
#define open_cfw_retained_imu_set_state_three host_sensor_hub_set_state_three
#define open_cfw_retained_calibration_load host_sensor_hub_calibration_load
#define open_cfw_retained_imu_apply_calibration host_sensor_hub_calibration_apply
#define open_cfw_retained_zero host_sensor_hub_zero
#define open_cfw_retained_ui_object_create host_sensor_hub_object_create
#define open_cfw_retained_ui_label_create host_sensor_hub_label_create
#define open_cfw_retained_ui_set_size host_sensor_hub_ui_size
#define open_cfw_retained_ui_set_position host_sensor_hub_ui_position
#define open_cfw_retained_ui_set_text host_sensor_hub_ui_text
#define open_cfw_retained_ui_set_font host_sensor_hub_ui_font
#define open_cfw_retained_ui_set_color host_sensor_hub_ui_color
#define open_cfw_retained_ui_set_alignment host_sensor_hub_ui_alignment
#define open_cfw_retained_ui_set_pad_top host_sensor_hub_ui_padding
#define open_cfw_retained_ui_set_pad_bottom host_sensor_hub_ui_padding
#define open_cfw_retained_ui_set_pad_left host_sensor_hub_ui_padding
#define open_cfw_retained_ui_set_pad_right host_sensor_hub_ui_padding
#define open_cfw_retained_translate_language \
    host_sensor_hub_translate_language
#define open_cfw_retained_translate_string host_sensor_hub_translate_string

#endif
