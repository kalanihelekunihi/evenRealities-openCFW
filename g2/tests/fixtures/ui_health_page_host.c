#include <stdarg.h>
#include <stddef.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>

static uint32_t host_widget_initialized;
static void *host_fifo_cell;
static uint32_t host_animating;
static uint32_t host_current_page;
static uint32_t host_ext_initialized;
static uint32_t host_selected_page;
static uintptr_t host_summary_root;
static uintptr_t host_scroll_container;
static uintptr_t host_page_roots[2];
static uintptr_t host_indicators[2];
static uintptr_t host_page_descriptors[4];
static uintptr_t host_widget_handles[32];
static uint8_t host_health_data[0x300];
static const void *host_font = (const void *)(uintptr_t)0x1234u;

#define OPEN_CFW_HEALTH_WIDGET_INITIALIZED host_widget_initialized
#define OPEN_CFW_HEALTH_FIFO host_fifo_cell
#define OPEN_CFW_HEALTH_ANIMATING host_animating
#define OPEN_CFW_HEALTH_CURRENT_PAGE host_current_page
#define OPEN_CFW_HEALTH_EXT_INITIALIZED host_ext_initialized
#define OPEN_CFW_HEALTH_SELECTED_PAGE host_selected_page
#define OPEN_CFW_HEALTH_SUMMARY_ROOT host_summary_root
#define OPEN_CFW_HEALTH_SCROLL_CONTAINER host_scroll_container
#define OPEN_CFW_HEALTH_PAGE_ROOTS host_page_roots
#define OPEN_CFW_HEALTH_INDICATORS host_indicators
#define OPEN_CFW_HEALTH_PAGE_DESCRIPTORS host_page_descriptors
#define OPEN_CFW_HEALTH_WIDGET_HANDLES host_widget_handles
#define OPEN_CFW_HEALTH_DATA host_health_data
#define OPEN_CFW_HEALTH_FONT host_font

static void *host_memset(void *, int, size_t);
static uintptr_t host_object_create(uintptr_t);
static void host_set_size(uintptr_t, int32_t, int32_t);
static void host_set_width(uintptr_t, int32_t);
static void host_set_height(uintptr_t, int32_t);
static void host_set_pos(uintptr_t, int32_t, int32_t);
static void host_set_x(uintptr_t, int32_t);
static int32_t host_get_x(uintptr_t);
static void host_align(uintptr_t, uint32_t, int32_t, int32_t);
static __attribute__((unused)) void host_align_to(
    uintptr_t,
    uintptr_t,
    uint32_t,
    int32_t,
    int32_t
);
static void host_u32_2(uintptr_t, uint32_t);
static void host_color3(uintptr_t, uint32_t, uint32_t);
static uint32_t host_color(uint32_t);
static void host_font_set(uintptr_t, const void *, uint32_t);
static void host_delete_children(uintptr_t);
static uintptr_t host_image_create(uintptr_t);
static void host_image_source(uintptr_t, const void *);
static uintptr_t host_label_create(uintptr_t);
static void host_label_text(uintptr_t, const char *);
static uint32_t host_translation_id(const char *);
static const char *host_translation(const char *, uint32_t);
static int host_format(char *, const char *, ...);
static void *host_fifo_create(void);
static void host_fifo_delete(void *);
static uint32_t host_fifo_empty(void *);
static int32_t host_fifo_push(void *, const void *, uint32_t);
static int32_t host_fifo_pop(void *, void *, uint32_t);
static void host_anim_init(void *);
static void host_anim_set_values(void *, int32_t, int32_t);
static void host_anim_start(void *);
static uint32_t host_notify(uint32_t);
static uint32_t host_send_action(uint32_t, const void *, uint32_t, uint32_t);
static void host_post_exit(void);
static uint32_t host_post_event(uint32_t, const void *, uint32_t, uint32_t);
static void host_minimize(void);
static void host_common_data(const uint8_t *, uint32_t);
static uint32_t host_lock(void);
static void host_unlock(void);

#define OPEN_CFW_HEALTH_MEMSET(...) host_memset(__VA_ARGS__)
#define OPEN_CFW_HEALTH_OBJECT_CREATE(...) host_object_create(__VA_ARGS__)
#define OPEN_CFW_HEALTH_SET_SIZE(...) host_set_size(__VA_ARGS__)
#define OPEN_CFW_HEALTH_SET_WIDTH(...) host_set_width(__VA_ARGS__)
#define OPEN_CFW_HEALTH_SET_HEIGHT(...) host_set_height(__VA_ARGS__)
#define OPEN_CFW_HEALTH_SET_POS(...) host_set_pos(__VA_ARGS__)
#define OPEN_CFW_HEALTH_SET_X(...) host_set_x(__VA_ARGS__)
#define OPEN_CFW_HEALTH_GET_X(...) host_get_x(__VA_ARGS__)
#define OPEN_CFW_HEALTH_ALIGN(...) host_align(__VA_ARGS__)
#define OPEN_CFW_HEALTH_ALIGN_TO(...) host_align_to(__VA_ARGS__)
#define OPEN_CFW_HEALTH_ADD_FLAGS(...) host_u32_2(__VA_ARGS__)
#define OPEN_CFW_HEALTH_CLEAR_FLAGS(...) host_u32_2(__VA_ARGS__)
#define OPEN_CFW_HEALTH_SET_LAYOUT(...) host_u32_2(__VA_ARGS__)
#define OPEN_CFW_HEALTH_SET_SCROLLBAR(...) host_u32_2(__VA_ARGS__)
#define OPEN_CFW_HEALTH_COLOR(...) host_color(__VA_ARGS__)
#define OPEN_CFW_HEALTH_SET_BG_COLOR(...) host_color3(__VA_ARGS__)
#define OPEN_CFW_HEALTH_SET_BG_OPACITY(...) host_color3(__VA_ARGS__)
#define OPEN_CFW_HEALTH_SET_TEXT_COLOR(...) host_color3(__VA_ARGS__)
#define OPEN_CFW_HEALTH_SET_TEXT_ALIGN(...) host_color3(__VA_ARGS__)
#define OPEN_CFW_HEALTH_SET_FONT(...) host_font_set(__VA_ARGS__)
#define OPEN_CFW_HEALTH_DELETE_CHILDREN(...) host_delete_children(__VA_ARGS__)
#define OPEN_CFW_HEALTH_IMAGE_CREATE(...) host_image_create(__VA_ARGS__)
#define OPEN_CFW_HEALTH_IMAGE_SET_SOURCE(...) host_image_source(__VA_ARGS__)
#define OPEN_CFW_HEALTH_LABEL_CREATE(...) host_label_create(__VA_ARGS__)
#define OPEN_CFW_HEALTH_LABEL_SET_TEXT(...) host_label_text(__VA_ARGS__)
#define OPEN_CFW_HEALTH_TRANSLATION_ID(...) host_translation_id(__VA_ARGS__)
#define OPEN_CFW_HEALTH_TRANSLATION(...) host_translation(__VA_ARGS__)
#define OPEN_CFW_HEALTH_FORMAT(...) host_format(__VA_ARGS__)
#define OPEN_CFW_HEALTH_FIFO_CREATE() host_fifo_create()
#define OPEN_CFW_HEALTH_FIFO_DELETE(...) host_fifo_delete(__VA_ARGS__)
#define OPEN_CFW_HEALTH_FIFO_EMPTY(...) host_fifo_empty(__VA_ARGS__)
#define OPEN_CFW_HEALTH_FIFO_PUSH(...) host_fifo_push(__VA_ARGS__)
#define OPEN_CFW_HEALTH_FIFO_POP(...) host_fifo_pop(__VA_ARGS__)
#define OPEN_CFW_HEALTH_ANIM_INIT(...) host_anim_init(__VA_ARGS__)
#define OPEN_CFW_HEALTH_ANIM_SET_VALUES(...) host_anim_set_values(__VA_ARGS__)
#define OPEN_CFW_HEALTH_ANIM_START(...) host_anim_start(__VA_ARGS__)
#define OPEN_CFW_HEALTH_NOTIFY_PAGE(...) host_notify(__VA_ARGS__)
#define OPEN_CFW_HEALTH_SEND_PAGE_ACTION(...) host_send_action(__VA_ARGS__)
#define OPEN_CFW_HEALTH_POST_EXIT() host_post_exit()
#define OPEN_CFW_HEALTH_POST_EVENT(...) host_post_event(__VA_ARGS__)
#define OPEN_CFW_HEALTH_MINIMIZE() host_minimize()
#define OPEN_CFW_HEALTH_COMMON_DATA(...) host_common_data(__VA_ARGS__)
#define OPEN_CFW_HEALTH_LOCK() host_lock()
#define OPEN_CFW_HEALTH_UNLOCK() host_unlock()

#include "../../components/apollo_main/core_overlay/ui_health_page.c"

struct host_fifo {
    uint8_t data[16][5];
    uint32_t head;
    uint32_t tail;
    uint32_t count;
};

static struct host_fifo host_fifo_storage;
static uintptr_t host_next_object;
static int32_t host_x[512];
static uint32_t host_bg[512];
static char host_labels[512][96];
static uint32_t host_notify_value;
static uint32_t host_notify_count;
static uint32_t host_action_count;
static uint8_t host_action_packet[6];
static uint32_t host_exit_count;
static uint32_t host_post_count;
static uint32_t host_minimize_count;
static uint32_t host_common_count;
static uint32_t host_delete_count;
static uint32_t host_lock_count;
static int32_t host_anim_target;

static void *host_memset(void *p, int value, size_t size)
{
    return memset(p, value, size);
}

static uintptr_t host_new_object(void)
{
    ++host_next_object;
    return host_next_object;
}

static uintptr_t host_object_create(uintptr_t parent)
{
    (void)parent;
    return host_new_object();
}

static void host_set_size(uintptr_t o, int32_t w, int32_t h)
{
    (void)o; (void)w; (void)h;
}

static void host_set_width(uintptr_t o, int32_t w) { (void)o; (void)w; }
static void host_set_height(uintptr_t o, int32_t h) { (void)o; (void)h; }
static void host_set_pos(uintptr_t o, int32_t x, int32_t y)
{
    (void)y;
    if (o < 512u) host_x[o] = x;
}
static void host_set_x(uintptr_t o, int32_t x)
{
    if (o < 512u) host_x[o] = x;
}
static int32_t host_get_x(uintptr_t o)
{
    return o < 512u ? host_x[o] : 0;
}
static void host_align(uintptr_t o, uint32_t a, int32_t x, int32_t y)
{ (void)o; (void)a; (void)x; (void)y; }
static void host_align_to(uintptr_t o, uintptr_t r, uint32_t a, int32_t x, int32_t y)
{ (void)o; (void)r; (void)a; (void)x; (void)y; }
static void host_u32_2(uintptr_t o, uint32_t v) { (void)o; (void)v; }
static void host_color3(uintptr_t o, uint32_t value, uint32_t selector)
{
    (void)selector;
    if (o < 512u) host_bg[o] = value;
}
static uint32_t host_color(uint32_t value) { return value; }
static void host_font_set(uintptr_t o, const void *f, uint32_t s)
{ (void)o; (void)f; (void)s; }
static void host_delete_children(uintptr_t o) { (void)o; ++host_delete_count; }
static uintptr_t host_image_create(uintptr_t parent) { return host_object_create(parent); }
static void host_image_source(uintptr_t o, const void *s) { (void)o; (void)s; }
static uintptr_t host_label_create(uintptr_t parent) { return host_object_create(parent); }
static void host_label_text(uintptr_t o, const char *text)
{
    if (o < 512u) {
        (void)snprintf(host_labels[o], sizeof(host_labels[o]), "%s", text ? text : "");
    }
}
static uint32_t host_translation_id(const char *s) { (void)s; return 1u; }
static const char *host_translation(const char *s, uint32_t id) { (void)id; return s; }
static int host_format(char *out, const char *format, ...)
{
    int result;
    va_list args;
    va_start(args, format);
    result = vsnprintf(out, 64u, format, args);
    va_end(args);
    return result;
}
static void *host_fifo_create(void)
{
    memset(&host_fifo_storage, 0, sizeof(host_fifo_storage));
    return &host_fifo_storage;
}
static void host_fifo_delete(void *fifo) { (void)fifo; }
static uint32_t host_fifo_empty(void *fifo)
{
    return ((struct host_fifo *)fifo)->count == 0u ? 1u : 0u;
}
static int32_t host_fifo_push(void *fifo, const void *data, uint32_t length)
{
    struct host_fifo *value = (struct host_fifo *)fifo;
    if (length != 5u || value->count == 16u) return -1;
    memcpy(value->data[value->tail], data, 5u);
    value->tail = (value->tail + 1u) % 16u;
    ++value->count;
    return 0;
}
static int32_t host_fifo_pop(void *fifo, void *data, uint32_t length)
{
    struct host_fifo *value = (struct host_fifo *)fifo;
    if (length != 5u || value->count == 0u) return -1;
    memcpy(data, value->data[value->head], 5u);
    value->head = (value->head + 1u) % 16u;
    --value->count;
    return 0;
}
static void host_anim_init(void *animation)
{
    memset(animation, 0, sizeof(struct open_cfw_health_anim));
}
static void host_anim_set_values(void *animation, int32_t start, int32_t target)
{
    (void)animation; (void)start; host_anim_target = target;
}
static void host_anim_start(void *animation)
{
    struct open_cfw_health_anim *value = (struct open_cfw_health_anim *)animation;
    void (*exec)(uintptr_t, int32_t) =
        (void (*)(uintptr_t, int32_t))value->exec_callback;
    int32_t (*ready)(void) = (int32_t (*)(void))value->ready_callback;
    exec(value->object, host_anim_target);
    (void)ready();
}
static uint32_t host_notify(uint32_t value)
{
    host_notify_value = value; ++host_notify_count; return 0u;
}
static uint32_t host_send_action(uint32_t service, const void *data, uint32_t length, uint32_t flags)
{
    (void)service; (void)flags; ++host_action_count;
    memset(host_action_packet, 0, sizeof(host_action_packet));
    if (data != NULL && length <= sizeof(host_action_packet)) memcpy(host_action_packet, data, length);
    return 0u;
}
static void host_post_exit(void) { ++host_exit_count; }
static uint32_t host_post_event(uint32_t s, const void *d, uint32_t l, uint32_t f)
{ (void)s; (void)d; (void)l; (void)f; ++host_post_count; return 0u; }
static void host_minimize(void) { ++host_minimize_count; }
static void host_common_data(const uint8_t *d, uint32_t l)
{ (void)d; (void)l; ++host_common_count; }
static uint32_t host_lock(void) { ++host_lock_count; return 1u; }
static void host_unlock(void) {}

void open_cfw_health_page_host_reset(void)
{
    memset(&host_fifo_storage, 0, sizeof(host_fifo_storage));
    memset(host_x, 0, sizeof(host_x));
    memset(host_bg, 0, sizeof(host_bg));
    memset(host_labels, 0, sizeof(host_labels));
    memset(host_health_data, 0, sizeof(host_health_data));
    memset(host_widget_handles, 0, sizeof(host_widget_handles));
    host_widget_initialized = 0u;
    host_fifo_cell = NULL;
    host_animating = 0u;
    host_current_page = 0u;
    host_ext_initialized = 0u;
    host_selected_page = 0u;
    host_summary_root = 0u;
    host_scroll_container = 0u;
    host_page_roots[0] = host_page_roots[1] = 0u;
    host_indicators[0] = host_indicators[1] = 0u;
    host_page_descriptors[0] = 0u;
    host_page_descriptors[1] = 300u;
    host_page_descriptors[2] = 0u;
    host_page_descriptors[3] = 301u;
    host_next_object = 0u;
    host_notify_value = host_notify_count = 0u;
    host_action_count = host_exit_count = host_post_count = 0u;
    host_minimize_count = host_common_count = host_delete_count = 0u;
    host_lock_count = 0u;
    host_anim_target = 0;
}

void open_cfw_health_page_host_set_u32(uint32_t offset, uint32_t value)
{
    memcpy(host_health_data + offset, &value, sizeof(value));
}
void open_cfw_health_page_host_set_float(uint32_t offset, float value)
{
    memcpy(host_health_data + offset, &value, sizeof(value));
}
void open_cfw_health_page_host_set_animating(uint32_t value) { host_animating = value; }
uint32_t open_cfw_health_page_host_selected(void) { return host_selected_page; }
uint32_t open_cfw_health_page_host_initialized(void) { return host_ext_initialized; }
uint32_t open_cfw_health_page_host_animating(void) { return host_animating; }
uint32_t open_cfw_health_page_host_notify_value(void) { return host_notify_value; }
uint32_t open_cfw_health_page_host_notify_count(void) { return host_notify_count; }
uint32_t open_cfw_health_page_host_fifo_count(void) { return host_fifo_storage.count; }
uint32_t open_cfw_health_page_host_action_count(void) { return host_action_count; }
uint32_t open_cfw_health_page_host_action_byte(uint32_t index)
{ return index < sizeof(host_action_packet) ? host_action_packet[index] : 0u; }
uint32_t open_cfw_health_page_host_exit_count(void) { return host_exit_count; }
uint32_t open_cfw_health_page_host_post_count(void) { return host_post_count; }
uint32_t open_cfw_health_page_host_minimize_count(void) { return host_minimize_count; }
uint32_t open_cfw_health_page_host_common_count(void) { return host_common_count; }
uint32_t open_cfw_health_page_host_delete_count(void) { return host_delete_count; }
uint32_t open_cfw_health_page_host_lock_count(void) { return host_lock_count; }
uint32_t open_cfw_health_page_host_scroll_x(void)
{ return host_scroll_container < 512u ? (uint32_t)host_x[host_scroll_container] : 0u; }
uint32_t open_cfw_health_page_host_indicator_color(uint32_t index)
{ return index < 2u && host_indicators[index] < 512u ? host_bg[host_indicators[index]] : 0u; }
const char *open_cfw_health_page_host_label(uint32_t handle_index)
{
    uintptr_t handle = handle_index < 32u ? host_widget_handles[handle_index] : 0u;
    return handle < 512u ? host_labels[handle] : "";
}
