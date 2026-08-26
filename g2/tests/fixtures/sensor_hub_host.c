#include <stdint.h>
#include <stdlib.h>
#include <string.h>

struct open_cfw_sensor_hub_record {
    uint16_t id;
    uint16_t reserved;
    uint32_t argument;
};
typedef void (*open_cfw_sensor_hub_handler)(const void *record);
struct open_cfw_sensor_hub_handler_slot {
    uint16_t id;
    uint16_t reserved;
    open_cfw_sensor_hub_handler handler;
};
struct open_cfw_sensor_hub_calibration { float value[9]; };

void *host_sensor_hub_thread_id;
void *host_sensor_hub_queue_id;
void *host_sensor_hub_timer_id;
uint32_t host_sensor_hub_last_tick;
uint32_t host_sensor_hub_timer_enabled;
uint16_t host_sensor_hub_role;
void *host_sensor_hub_calibration_screen;
void *host_sensor_hub_calibration_label_left;
void *host_sensor_hub_calibration_label_right;
uint8_t host_sensor_hub_handler_storage[128];
#define HOST_SENSOR_HUB_TABLE \
    ((volatile struct open_cfw_sensor_hub_handler_slot *)(void *) \
        host_sensor_hub_handler_storage)

uint32_t host_sensor_hub_queue_depth;
uint32_t host_sensor_hub_queue_item_size;
uint32_t host_sensor_hub_queue_count;
uint32_t host_sensor_hub_queue_put_fail;
struct open_cfw_sensor_hub_record host_sensor_hub_queue[64];
uint32_t host_sensor_hub_thread_new_count;
uint32_t host_sensor_hub_thread_terminate_count;
uint32_t host_sensor_hub_timer_new_type;
uint32_t host_sensor_hub_timer_start_ticks;
uint32_t host_sensor_hub_timer_stop_count;
uint32_t host_sensor_hub_tick_value;
uint32_t host_sensor_hub_active_index;
uint32_t host_sensor_hub_exit_index;
uint32_t host_sensor_hub_critical_enter_count;
uint32_t host_sensor_hub_critical_exit_count;
uint32_t host_sensor_hub_product_mode_value;
uint32_t host_sensor_hub_ota_active_value;
uint32_t host_sensor_hub_role_getter_value;
uint32_t host_sensor_hub_als_init_count;
uint32_t host_sensor_hub_als_open_count;
uint32_t host_sensor_hub_als_close_count;
uint32_t host_sensor_hub_imu_reset_count;
uint32_t host_sensor_hub_imu_init_count;
uint8_t host_sensor_hub_imu_init_mode;
uint32_t host_sensor_hub_imu_read_count;
uint32_t host_sensor_hub_imu_read_tick;
uint32_t host_sensor_hub_imu_start_count;
uint32_t host_sensor_hub_imu_stop_count;
uint32_t host_sensor_hub_imu_mode_count;
uint8_t host_sensor_hub_imu_mode;
uint32_t host_sensor_hub_threshold;
uint32_t host_sensor_hub_period[2];
uint32_t host_sensor_hub_accel;
uint8_t host_sensor_hub_states[4];
uint32_t host_sensor_hub_calibration_load_count;
uint32_t host_sensor_hub_calibration_apply_count;
uint32_t host_sensor_hub_dispatch_count;
struct open_cfw_sensor_hub_record host_sensor_hub_dispatched;
uint32_t host_sensor_hub_screen_count;
uint32_t host_sensor_hub_label_count;
uint32_t host_sensor_hub_text_count;
uint32_t host_sensor_hub_last_string_id;
uint32_t host_sensor_hub_last_alignment;

static void host_sensor_hub_capture(const void *record)
{
    host_sensor_hub_dispatched =
        *(const struct open_cfw_sensor_hub_record *)record;
    ++host_sensor_hub_dispatch_count;
}

void host_sensor_hub_register_capture(uint16_t id)
{
    HOST_SENSOR_HUB_TABLE[0].id = id;
    HOST_SENSOR_HUB_TABLE[0].handler = host_sensor_hub_capture;
}

void *host_sensor_hub_thread_new(
    void (*entry)(void *), void *argument, const void *attributes)
{
    (void)entry; (void)argument; (void)attributes;
    ++host_sensor_hub_thread_new_count;
    return (void *)(uintptr_t)0x101u;
}
int32_t host_sensor_hub_thread_terminate(void *thread_id)
{ (void)thread_id; ++host_sensor_hub_thread_terminate_count; return 0; }
void *host_sensor_hub_queue_new(uint32_t count, uint32_t size, const void *attributes)
{
    (void)attributes; host_sensor_hub_queue_depth = count;
    host_sensor_hub_queue_item_size = size; return (void *)(uintptr_t)0x202u;
}
int32_t host_sensor_hub_queue_put(
    void *queue_id, const void *message, uint8_t priority, uint32_t timeout)
{
    (void)priority; (void)timeout;
    if (queue_id == NULL || message == NULL || host_sensor_hub_queue_put_fail ||
        host_sensor_hub_queue_count >= 64u) return -1;
    host_sensor_hub_queue[host_sensor_hub_queue_count++] =
        *(const struct open_cfw_sensor_hub_record *)message;
    return 0;
}
int32_t host_sensor_hub_queue_get(
    void *queue_id, void *message, uint8_t *priority, uint32_t timeout)
{
    uint32_t i; (void)priority; (void)timeout;
    if (queue_id == NULL || message == NULL || host_sensor_hub_queue_count == 0u)
        return -1;
    *(struct open_cfw_sensor_hub_record *)message = host_sensor_hub_queue[0];
    for (i = 1u; i < host_sensor_hub_queue_count; ++i)
        host_sensor_hub_queue[i - 1u] = host_sensor_hub_queue[i];
    --host_sensor_hub_queue_count; return 0;
}
void *host_sensor_hub_timer_new(
    void (*callback)(void *), uint32_t type, void *argument, const void *attributes)
{
    (void)callback; (void)argument; (void)attributes;
    host_sensor_hub_timer_new_type = type; return (void *)(uintptr_t)0x303u;
}
int32_t host_sensor_hub_timer_start(void *timer_id, uint32_t ticks)
{ if (!timer_id) return -1; host_sensor_hub_timer_start_ticks = ticks; return 0; }
int32_t host_sensor_hub_timer_stop(void *timer_id)
{ if (!timer_id) return -1; ++host_sensor_hub_timer_stop_count; return 0; }
uint32_t host_sensor_hub_tick(void) { return host_sensor_hub_tick_value; }
void host_sensor_hub_state_active(uint32_t index) { host_sensor_hub_active_index=index; }
void host_sensor_hub_state_exit(uint32_t index) { host_sensor_hub_exit_index=index; }
void host_sensor_hub_critical_enter(void) { ++host_sensor_hub_critical_enter_count; }
void host_sensor_hub_critical_exit(void) { ++host_sensor_hub_critical_exit_count; }
uint32_t host_sensor_hub_product_mode(void) { return host_sensor_hub_product_mode_value; }
uint32_t host_sensor_hub_ota_active(void) { return host_sensor_hub_ota_active_value; }
uint32_t host_sensor_hub_role_getter(void) { return host_sensor_hub_role_getter_value; }
void host_sensor_hub_als_initialize(void) { ++host_sensor_hub_als_init_count; }
void host_sensor_hub_als_open(void) { ++host_sensor_hub_als_open_count; }
void host_sensor_hub_als_close(void) { ++host_sensor_hub_als_close_count; }
void host_sensor_hub_imu_reset(void) { ++host_sensor_hub_imu_reset_count; }
void host_sensor_hub_imu_initialize(uint8_t mode)
{ ++host_sensor_hub_imu_init_count; host_sensor_hub_imu_init_mode=mode; }
void host_sensor_hub_imu_read(uint32_t tick)
{ ++host_sensor_hub_imu_read_count; host_sensor_hub_imu_read_tick=tick; }
void host_sensor_hub_imu_start(void) { ++host_sensor_hub_imu_start_count; }
void host_sensor_hub_imu_stop(void) { ++host_sensor_hub_imu_stop_count; }
void host_sensor_hub_imu_set_mode(uint8_t mode)
{ ++host_sensor_hub_imu_mode_count; host_sensor_hub_imu_mode=mode; }
void host_sensor_hub_imu_threshold(uint32_t value) { host_sensor_hub_threshold=value; }
void host_sensor_hub_imu_period(uint32_t first,uint32_t second)
{ host_sensor_hub_period[0]=first; host_sensor_hub_period[1]=second; }
void host_sensor_hub_imu_accel(uint32_t value) { host_sensor_hub_accel=value; }
uint8_t host_sensor_hub_state_zero(void) { return host_sensor_hub_states[0]; }
uint8_t host_sensor_hub_state_one(void) { return host_sensor_hub_states[1]; }
uint8_t host_sensor_hub_state_two(void) { return host_sensor_hub_states[2]; }
uint8_t host_sensor_hub_state_three(void) { return host_sensor_hub_states[3]; }
void host_sensor_hub_set_state_zero(uint8_t value) { host_sensor_hub_states[0]=value; }
void host_sensor_hub_set_state_one(uint8_t value) { host_sensor_hub_states[1]=value; }
void host_sensor_hub_set_state_two(uint8_t value) { host_sensor_hub_states[2]=value; }
void host_sensor_hub_set_state_three(uint8_t value) { host_sensor_hub_states[3]=value; }
void host_sensor_hub_calibration_load(
    float *a,float *b,struct open_cfw_sensor_hub_calibration *matrix)
{ (void)a;(void)b;(void)matrix;++host_sensor_hub_calibration_load_count; }
void host_sensor_hub_calibration_apply(
    const float *a,const float *b,
    const struct open_cfw_sensor_hub_calibration *matrix)
{ (void)a;(void)b;(void)matrix;++host_sensor_hub_calibration_apply_count; }
void host_sensor_hub_zero(void *destination,uint32_t size) { memset(destination,0,size); }
void *host_sensor_hub_object_create(void *parent)
{ (void)parent; ++host_sensor_hub_screen_count; return (void *)(uintptr_t)(0x400u+host_sensor_hub_screen_count); }
void *host_sensor_hub_label_create(void *parent)
{ (void)parent; ++host_sensor_hub_label_count; return (void *)(uintptr_t)(0x500u+host_sensor_hub_label_count); }
void host_sensor_hub_ui_size(void *o,int32_t w,int32_t h){(void)o;(void)w;(void)h;}
void host_sensor_hub_ui_position(void *o,int32_t x,int32_t y){(void)o;(void)x;(void)y;}
void host_sensor_hub_ui_text(void *o,const char *text){(void)o;(void)text;++host_sensor_hub_text_count;}
void host_sensor_hub_ui_font(void *o,uint32_t f,uint32_t s){(void)o;(void)f;(void)s;}
void host_sensor_hub_ui_color(void *o,uint32_t c,uint32_t s){(void)o;(void)c;(void)s;}
void host_sensor_hub_ui_alignment(void *o,uint32_t a,uint32_t s)
{(void)o;(void)s;host_sensor_hub_last_alignment=a;}
void host_sensor_hub_ui_padding(void *o,int32_t p,uint32_t s)
{(void)o;(void)p;(void)s;}
uint32_t host_sensor_hub_translate_language(uint32_t id)
{ host_sensor_hub_last_string_id=id; return 1u; }
const char *host_sensor_hub_translate_string(uint32_t id,uint32_t language)
{ host_sensor_hub_last_string_id=id;(void)language;return "translated"; }

void host_sensor_hub_reset(void)
{
    host_sensor_hub_thread_id = NULL;
    host_sensor_hub_queue_id = NULL;
    host_sensor_hub_timer_id = NULL;
    host_sensor_hub_last_tick = 0u;
    host_sensor_hub_timer_enabled = 0u;
    host_sensor_hub_role = 0u;
    host_sensor_hub_calibration_screen = NULL;
    host_sensor_hub_calibration_label_left = NULL;
    host_sensor_hub_calibration_label_right = NULL;
    memset(host_sensor_hub_handler_storage, 0,
           sizeof(host_sensor_hub_handler_storage));
    host_sensor_hub_queue_depth = 0u;
    host_sensor_hub_queue_item_size = 0u;
    host_sensor_hub_queue_count = 0u;
    host_sensor_hub_queue_put_fail = 0u;
    memset(host_sensor_hub_queue, 0, sizeof(host_sensor_hub_queue));
    host_sensor_hub_thread_new_count = 0u;
    host_sensor_hub_thread_terminate_count = 0u;
    host_sensor_hub_timer_new_type = 0u;
    host_sensor_hub_timer_start_ticks = 0u;
    host_sensor_hub_timer_stop_count = 0u;
    host_sensor_hub_active_index = 0u;
    host_sensor_hub_exit_index = 0u;
    host_sensor_hub_critical_enter_count = 0u;
    host_sensor_hub_critical_exit_count = 0u;
    host_sensor_hub_product_mode_value = 0u;
    host_sensor_hub_ota_active_value = 0u;
    host_sensor_hub_role_getter_value = 0u;
    host_sensor_hub_als_init_count = 0u;
    host_sensor_hub_als_open_count = 0u;
    host_sensor_hub_als_close_count = 0u;
    host_sensor_hub_imu_reset_count = 0u;
    host_sensor_hub_imu_init_count = 0u;
    host_sensor_hub_imu_init_mode = 0u;
    host_sensor_hub_imu_read_count = 0u;
    host_sensor_hub_imu_read_tick = 0u;
    host_sensor_hub_imu_start_count = 0u;
    host_sensor_hub_imu_stop_count = 0u;
    host_sensor_hub_imu_mode_count = 0u;
    host_sensor_hub_imu_mode = 0u;
    host_sensor_hub_threshold = 0u;
    memset(host_sensor_hub_period, 0, sizeof(host_sensor_hub_period));
    host_sensor_hub_accel = 0u;
    memset(host_sensor_hub_states, 0, sizeof(host_sensor_hub_states));
    host_sensor_hub_calibration_load_count = 0u;
    host_sensor_hub_calibration_apply_count = 0u;
    host_sensor_hub_dispatch_count = 0u;
    memset(&host_sensor_hub_dispatched, 0, sizeof(host_sensor_hub_dispatched));
    host_sensor_hub_screen_count = 0u;
    host_sensor_hub_label_count = 0u;
    host_sensor_hub_text_count = 0u;
    host_sensor_hub_last_string_id = 0u;
    host_sensor_hub_last_alignment = 0u;
    host_sensor_hub_tick_value = 1234u;
}
