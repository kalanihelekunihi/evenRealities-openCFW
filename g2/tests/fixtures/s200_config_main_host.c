#include <stdint.h>
#include <string.h>

typedef struct {
    void *target;
    uint32_t code;
} host_s200_event;

typedef struct HostS200Object {
    struct HostS200Object *parent;
    int32_t value;
    int32_t width;
    int32_t height;
    uint8_t padding[0x1c];
    uint8_t flags;
} HostS200Object;

uint8_t host_s200_reset_storage[16];
HostS200Object host_s200_objects[4];
uint8_t host_s200_input[9];
int32_t host_s200_point[2];
uint32_t host_s200_set_count;
uint32_t host_s200_event_count;
uint32_t host_s200_reset_clear_count;
uint32_t host_s200_init_mask;
uint32_t host_s200_release_count;
uint32_t host_s200_created_count;
uint32_t host_s200_direction;
int32_t host_s200_performance_result;

void host_s200_reset(void)
{
    memset(host_s200_reset_storage, 0, sizeof(host_s200_reset_storage));
    memset(host_s200_objects, 0, sizeof(host_s200_objects));
    memset(host_s200_input, 0, sizeof(host_s200_input));
    memset(host_s200_point, 0, sizeof(host_s200_point));
    host_s200_set_count = 0;
    host_s200_event_count = 0;
    host_s200_reset_clear_count = 0;
    host_s200_init_mask = 0;
    host_s200_release_count = 0;
    host_s200_created_count = 0;
    host_s200_direction = 0;
    host_s200_performance_result = -7;
}

void *host_s200_object(uint32_t index) { return &host_s200_objects[index]; }
void host_s200_object_parent(uint32_t index, uint32_t parent)
{ host_s200_objects[index].parent = &host_s200_objects[parent]; }
void host_s200_object_value(uint32_t index, int32_t value)
{ host_s200_objects[index].value = value; }
int32_t host_s200_object_value_get(uint32_t index)
{ return host_s200_objects[index].value; }
void host_s200_object_extent(uint32_t index, int32_t width, int32_t height)
{ host_s200_objects[index].width = width; host_s200_objects[index].height = height; }
void host_s200_object_flags(uint32_t index, uint8_t flags)
{ host_s200_objects[index].flags = flags; }

int open_cfw_retained_s200_event_is_class(const void *type, const void *event)
{ (void)type; (void)event; return 1; }
uint32_t open_cfw_retained_s200_event_code(const void *event)
{ return ((const host_s200_event *)event)->code; }
void *open_cfw_retained_s200_event_target(const void *event)
{ return ((const host_s200_event *)event)->target; }
void *open_cfw_retained_s200_parent(void *object)
{ return ((HostS200Object *)object)->parent; }
int32_t open_cfw_retained_s200_value_get(void *object)
{ return ((HostS200Object *)object)->value; }
void open_cfw_retained_s200_value_set(void *object, int32_t value, uint32_t animate)
{ (void)animate; ((HostS200Object *)object)->value = value; ++host_s200_set_count; }
void open_cfw_retained_s200_event_send(void *object, uint32_t code, void *parameter)
{ (void)object; (void)code; (void)parameter; ++host_s200_event_count; }
void *open_cfw_retained_s200_input_device(void) { return host_s200_input; }
void open_cfw_retained_s200_input_point(void *target, int32_t *point)
{ (void)target; point[0] = host_s200_point[0]; point[1] = host_s200_point[1]; }
int32_t open_cfw_retained_s200_object_width(void *object)
{ return ((HostS200Object *)object)->width; }
int32_t open_cfw_retained_s200_object_height(void *object)
{ return ((HostS200Object *)object)->height; }
uint32_t open_cfw_retained_s200_value_direction(void *object, uint32_t part)
{ (void)object; (void)part; return host_s200_direction; }
int32_t open_cfw_retained_s200_content_width(void *object)
{ return ((HostS200Object *)object)->width; }
int32_t open_cfw_retained_s200_content_height(void *object)
{ return ((HostS200Object *)object)->height; }
void open_cfw_retained_s200_object_size(void *object, int32_t width, int32_t height)
{ ((HostS200Object *)object)->width = width; ((HostS200Object *)object)->height = height; }
void open_cfw_retained_s200_layout(void *object, uint32_t mode)
{ (void)object; (void)mode; }
void *open_cfw_retained_s200_object_create(void *parent)
{ HostS200Object *object = &host_s200_objects[2 + host_s200_created_count++]; object->parent = parent; return object; }
void open_cfw_retained_s200_object_configure(void *object) { (void)object; }
int32_t open_cfw_retained_s200_display_width(void) { return 400; }
void open_cfw_retained_s200_object_align(void *object, uint32_t a, uint32_t b, uint32_t c)
{ (void)object; (void)a; (void)b; (void)c; }
void open_cfw_retained_s200_object_mode(void *object, uint32_t mode)
{ (void)object; (void)mode; }
void open_cfw_retained_s200_object_limit(void *object, int32_t value)
{ ((HostS200Object *)object)->value = value; }
void open_cfw_retained_s200_reset_capture(volatile void *state)
{ (void)state; host_s200_init_mask |= 1U; }
void open_cfw_retained_s200_watchdog_prepare(void) { host_s200_init_mask |= 2U; }
void open_cfw_retained_s200_clock_prepare(void) { host_s200_init_mask |= 4U; }
void open_cfw_retained_s200_clock_select(uint32_t value) { if (value == 1U) host_s200_init_mask |= 8U; }
void open_cfw_retained_s200_transport_prepare(void) { host_s200_init_mask |= 0x10U; }
void open_cfw_retained_s200_power_prepare(void) { host_s200_init_mask |= 0x20U; }
void open_cfw_retained_s200_power_select(uint32_t value) { if (value == 1U) host_s200_init_mask |= 0x40U; }
int32_t open_cfw_retained_s200_performance_select(uint32_t value)
{ if (value == 2U) host_s200_init_mask |= 0x80U; return host_s200_performance_result; }
void open_cfw_retained_s200_runtime_prepare(void) { host_s200_init_mask |= 0x100U; }
void open_cfw_retained_s200_service_prepare(void) { host_s200_init_mask |= 0x200U; }
void open_cfw_retained_s200_release_register(const char *a, const char *b, const char *c)
{ (void)a; (void)b; (void)c; ++host_s200_release_count; }
void open_cfw_retained_s200_reset_status_clear(uint32_t a, uint32_t b)
{ (void)a; (void)b; ++host_s200_reset_clear_count; }
void open_cfw_retained_s200_delay(uint32_t ticks) { (void)ticks; }
void open_cfw_retained_s200_application_prepare(void) {}
void open_cfw_retained_s200_product_rtos_init(void) {}
void open_cfw_retained_s200_startup_handoff(void) {}
