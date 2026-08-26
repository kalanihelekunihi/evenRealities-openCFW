#include <stdint.h>
#include <stddef.h>
#include <string.h>

void *host_box_timer_force;
void *host_box_timer_reconnect;
uint8_t host_box_local[4];
uint8_t host_box_last_local[4];
uint8_t host_box_case[8];
uint8_t host_box_force;
uint8_t host_box_ring_connected;
uint8_t host_box_ring_reconnect;
uint32_t host_box_timer_start_count;
uint32_t host_box_timer_stop_count;
uint32_t host_box_timer_delete_count;
uint32_t host_box_display_open_count;
uint32_t host_box_display_close_count;
uint32_t host_box_publish_count;
uint32_t host_box_sync_count;
uint32_t host_box_notify_count;
uint32_t host_box_ring_change_count;
uint32_t host_box_input_out_count;
uint32_t host_box_reconnect_count;
uint32_t host_box_queue_count;
uint32_t host_box_case_request_count;
uint8_t host_box_last_sync[8];
uint8_t host_box_last_notify[8];
uint8_t host_box_lens_side;
uint8_t host_box_product_mode;
int host_box_display_ready;
int host_box_display_active;
int host_box_publish_role;
int host_box_reconnect_queue_result;
int host_box_timer_running;

void host_box_reset(void)
{
    memset(host_box_local, 0, sizeof(host_box_local));
    memset(host_box_last_local, 0, sizeof(host_box_last_local));
    memset(host_box_case, 0, sizeof(host_box_case));
    memset(host_box_last_sync, 0, sizeof(host_box_last_sync));
    memset(host_box_last_notify, 0, sizeof(host_box_last_notify));
    host_box_timer_force = NULL;
    host_box_timer_reconnect = NULL;
    host_box_force = 0;
    host_box_ring_connected = 0;
    host_box_ring_reconnect = 0;
    host_box_timer_start_count = 0;
    host_box_timer_stop_count = 0;
    host_box_timer_delete_count = 0;
    host_box_display_open_count = 0;
    host_box_display_close_count = 0;
    host_box_publish_count = 0;
    host_box_sync_count = 0;
    host_box_notify_count = 0;
    host_box_ring_change_count = 0;
    host_box_input_out_count = 0;
    host_box_reconnect_count = 0;
    host_box_queue_count = 0;
    host_box_case_request_count = 0;
    host_box_lens_side = 0;
    host_box_product_mode = 0;
    host_box_display_ready = 1;
    host_box_display_active = 1;
    host_box_publish_role = 0;
    host_box_reconnect_queue_result = 1;
    host_box_timer_running = 1;
}

void *open_cfw_retained_box_detect_memcpy(void *d, const void *s, uint32_t n)
{ return memcpy(d, s, n); }
void *open_cfw_retained_box_detect_memset(void *d, int v, uint32_t n)
{ return memset(d, v, n); }
void *open_cfw_retained_box_detect_timer_new(
    void (*callback)(void *), uint32_t type, void *argument, const void *attr)
{
    (void)callback; (void)type; (void)argument;
    return (void *)attr;
}
int open_cfw_retained_box_detect_timer_start(void *timer, uint32_t ticks)
{ (void)timer; (void)ticks; ++host_box_timer_start_count; return 0; }
int open_cfw_retained_box_detect_timer_stop(void *timer)
{ (void)timer; ++host_box_timer_stop_count; return 0; }
int open_cfw_retained_box_detect_timer_is_running(void *timer)
{ (void)timer; return host_box_timer_running; }
int open_cfw_retained_box_detect_timer_delete(void *timer)
{ (void)timer; ++host_box_timer_delete_count; return 0; }
int open_cfw_retained_box_detect_display_ready(void)
{ return host_box_display_ready; }
int open_cfw_retained_box_detect_should_publish_status(void)
{ return host_box_publish_role; }
uint8_t open_cfw_retained_box_detect_lens_side(void)
{ return host_box_lens_side; }
int open_cfw_retained_box_detect_send_notification(
    uint32_t service, const void *data, uint32_t length,
    uint32_t flags, uint32_t destination)
{
    (void)service; (void)flags; (void)destination;
    memcpy(host_box_last_notify, data, length > 8 ? 8 : length);
    ++host_box_notify_count; return 0;
}
int open_cfw_retained_box_detect_send_sync(
    uint32_t service, const void *data, uint32_t length,
    uint32_t flags, uint32_t destination)
{
    (void)service; (void)flags; (void)destination;
    memcpy(host_box_last_sync, data, length > 8 ? 8 : length);
    ++host_box_sync_count; return 0;
}
int open_cfw_retained_box_detect_display_is_active(void)
{ return host_box_display_active; }
void open_cfw_retained_box_detect_display_open(void)
{ ++host_box_display_open_count; }
void open_cfw_retained_box_detect_display_close(void)
{ ++host_box_display_close_count; }
void open_cfw_retained_box_detect_ring_state_changed(void)
{ ++host_box_ring_change_count; }
int open_cfw_retained_box_detect_ring_reconnect(void)
{ ++host_box_reconnect_count; return 0; }
int open_cfw_retained_box_detect_ring_reconnect_queue(uint8_t scene)
{ (void)scene; return host_box_reconnect_queue_result; }
uint8_t open_cfw_retained_box_detect_product_mode(void)
{ return host_box_product_mode; }
int open_cfw_retained_box_detect_queue(const void *message)
{ (void)message; ++host_box_queue_count; return 0; }
uint8_t *open_cfw_retained_box_detect_device_state(uint32_t index)
{ static uint8_t value = 1; (void)index; return &value; }
int open_cfw_retained_box_detect_case_request(const uint8_t *data, uint16_t n)
{ (void)data; (void)n; ++host_box_case_request_count; return -9; }
int open_cfw_retained_box_detect_case_status(uint32_t type, const void *data)
{ (void)type; (void)data; ++host_box_publish_count; return 0; }
int open_cfw_retained_box_detect_case_interrupt(uint32_t context)
{ (void)context; return 0; }
void open_cfw_retained_box_detect_input_out(void)
{ ++host_box_input_out_count; }
