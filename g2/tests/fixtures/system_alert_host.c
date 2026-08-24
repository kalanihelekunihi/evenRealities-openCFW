#include <stdint.h>
#include <string.h>

static uint8_t host_alert_type;
static uintptr_t host_root;
static uintptr_t host_content;
static uint32_t host_last_tick;
static uint8_t host_visible;
static uint32_t host_animation_ticks;
static uintptr_t host_page_descriptor[2];
static const void *host_font = (const void *)(uintptr_t)0xf00du;

#define OPEN_CFW_SYSTEM_ALERT_TYPE host_alert_type
#define OPEN_CFW_SYSTEM_ALERT_ROOT host_root
#define OPEN_CFW_SYSTEM_ALERT_CONTENT host_content
#define OPEN_CFW_SYSTEM_ALERT_LAST_TICK host_last_tick
#define OPEN_CFW_SYSTEM_ALERT_VISIBLE host_visible
#define OPEN_CFW_SYSTEM_ALERT_ANIMATION_TICKS host_animation_ticks
#define OPEN_CFW_SYSTEM_ALERT_PAGE_DESCRIPTOR host_page_descriptor
#define OPEN_CFW_SYSTEM_ALERT_FONT host_font

#define OPEN_CFW_SYSTEM_ALERT_OBJECT_CREATE(parent) test_object_create(parent)
#define OPEN_CFW_SYSTEM_ALERT_SET_WIDTH(...) test_call2(1u, __VA_ARGS__)
#define OPEN_CFW_SYSTEM_ALERT_SET_HEIGHT(...) test_call2(2u, __VA_ARGS__)
#define OPEN_CFW_SYSTEM_ALERT_SET_FLEX_FLOW(...) test_call4(3u, __VA_ARGS__)
#define OPEN_CFW_SYSTEM_ALERT_ADD_FLAGS(...) test_call2(4u, __VA_ARGS__)
#define OPEN_CFW_SYSTEM_ALERT_CLEAR_FLAGS(...) test_call2(31u, __VA_ARGS__)
#define OPEN_CFW_SYSTEM_ALERT_SET_LAYOUT(...) test_call2(5u, __VA_ARGS__)
#define OPEN_CFW_SYSTEM_ALERT_SET_ALIGN(...) test_call2(6u, __VA_ARGS__)
#define OPEN_CFW_SYSTEM_ALERT_COLOR(value) test_color(value)
#define OPEN_CFW_SYSTEM_ALERT_SET_BG_COLOR(...) test_call3(8u, __VA_ARGS__)
#define OPEN_CFW_SYSTEM_ALERT_SET_LABEL_BG_COLOR(...) test_call3(32u, __VA_ARGS__)
#define OPEN_CFW_SYSTEM_ALERT_SET_BG_OPACITY(...) test_call3(9u, __VA_ARGS__)
#define OPEN_CFW_SYSTEM_ALERT_SET_TEXT_COLOR(...) test_call3(10u, __VA_ARGS__)
#define OPEN_CFW_SYSTEM_ALERT_SET_TEXT_ALIGN(...) test_call3(11u, __VA_ARGS__)
#define OPEN_CFW_SYSTEM_ALERT_SET_PAD_TOP(...) test_call3(12u, __VA_ARGS__)
#define OPEN_CFW_SYSTEM_ALERT_SET_PAD_BOTTOM(...) test_call3(13u, __VA_ARGS__)
#define OPEN_CFW_SYSTEM_ALERT_SET_PAD_LEFT(...) test_call3(14u, __VA_ARGS__)
#define OPEN_CFW_SYSTEM_ALERT_SET_PAD_RIGHT(...) test_call3(15u, __VA_ARGS__)
#define OPEN_CFW_SYSTEM_ALERT_SET_RADIUS(...) test_call3(16u, __VA_ARGS__)
#define OPEN_CFW_SYSTEM_ALERT_SET_BORDER_WIDTH(...) test_call3(17u, __VA_ARGS__)
#define OPEN_CFW_SYSTEM_ALERT_SET_SCROLLBAR_MODE(...) test_call2(18u, __VA_ARGS__)
#define OPEN_CFW_SYSTEM_ALERT_SET_SCROLL_DIR(...) test_call2(19u, __VA_ARGS__)
#define OPEN_CFW_SYSTEM_ALERT_SET_FONT(object, font, selector) test_call3(20u, (object), (uintptr_t)(font), (selector))
#define OPEN_CFW_SYSTEM_ALERT_DELETE_CHILDREN(object) test_call1(21u, object)
#define OPEN_CFW_SYSTEM_ALERT_IMAGE_CREATE(parent) test_image_create(parent)
#define OPEN_CFW_SYSTEM_ALERT_IMAGE_SET_SOURCE(image, source) test_call2(23u, (image), (uintptr_t)(source))
#define OPEN_CFW_SYSTEM_ALERT_LABEL_CREATE(parent) test_label_create(parent)
#define OPEN_CFW_SYSTEM_ALERT_LABEL_SET_TEXT(label, text) test_call2(25u, (label), (uintptr_t)(text))
#define OPEN_CFW_SYSTEM_ALERT_TRANSLATION_ID(text) test_translation_id(text)
#define OPEN_CFW_SYSTEM_ALERT_TRANSLATION(text, index) test_translation((text), (index))
#define OPEN_CFW_SYSTEM_ALERT_ROLE() host_role
#define OPEN_CFW_SYSTEM_ALERT_DISPLAY_ACTIVE() host_display_active
#define OPEN_CFW_SYSTEM_ALERT_POST_SELF(...) test_message(28u, __VA_ARGS__)
#define OPEN_CFW_SYSTEM_ALERT_NOTIFY_STATE(...) test_message(29u, __VA_ARGS__)
#define OPEN_CFW_SYSTEM_ALERT_SEND_EVENT(...) test_message(30u, __VA_ARGS__)
#define OPEN_CFW_SYSTEM_ALERT_TICK() host_tick

struct test_call {
    uint32_t id;
    uintptr_t a;
    uintptr_t b;
    uintptr_t c;
    uintptr_t d;
};

static struct test_call host_calls[128];
static uint32_t host_call_count;
static uint32_t host_role;
static uint32_t host_display_active;
static uint32_t host_tick;
static uint32_t host_message_result;

static void test_record(uint32_t id, uintptr_t a, uintptr_t b, uintptr_t c, uintptr_t d)
{
    if (host_call_count < 128u) {
        host_calls[host_call_count].id = id;
        host_calls[host_call_count].a = a;
        host_calls[host_call_count].b = b;
        host_calls[host_call_count].c = c;
        host_calls[host_call_count].d = d;
        ++host_call_count;
    }
}

static void test_call1(uint32_t id, uintptr_t a) { test_record(id, a, 0u, 0u, 0u); }
static void test_call2(uint32_t id, uintptr_t a, uintptr_t b) { test_record(id, a, b, 0u, 0u); }
static void test_call3(uint32_t id, uintptr_t a, uintptr_t b, uintptr_t c) { test_record(id, a, b, c, 0u); }
static void test_call4(uint32_t id, uintptr_t a, uintptr_t b, uintptr_t c, uintptr_t d) { test_record(id, a, b, c, d); }

static uintptr_t test_object_create(uintptr_t parent)
{
    uintptr_t result = host_root == 0u ? 0x1000u : 0x2000u;
    test_record(0u, parent, result, 0u, 0u);
    return result;
}

static uint32_t test_color(uint32_t value)
{
    test_record(7u, value, 0u, 0u, 0u);
    return value ^ 0x55000000u;
}

static uintptr_t test_image_create(uintptr_t parent)
{
    test_record(22u, parent, 0x3000u, 0u, 0u);
    return 0x3000u;
}

static uintptr_t test_label_create(uintptr_t parent)
{
    test_record(24u, parent, 0x4000u, 0u, 0u);
    return 0x4000u;
}

static uint32_t test_translation_id(const char *text)
{
    uint32_t result = strstr(text, "DISCONNECT") != 0 ? 1u : 2u;
    test_record(26u, result, 0u, 0u, 0u);
    return result;
}

static const char *test_translation(const char *text, uint32_t index)
{
    test_record(27u, index, (uintptr_t)text, 0u, 0u);
    return index == 1u ? "disconnect" : "connect";
}

static uint32_t test_message(uint32_t id, uint32_t app, const void *data, uint32_t length, uint32_t delay)
{
    uintptr_t first = data != 0 && length != 0u ? *(const uint8_t *)data : 0u;
    test_record(id, app, first, length, delay);
    return host_message_result;
}

#include "../../components/apollo_main/core_overlay/system_alert.c"

void open_cfw_test_system_alert_reset(void)
{
    memset(host_calls, 0, sizeof(host_calls));
    memset(host_page_descriptor, 0, sizeof(host_page_descriptor));
    host_alert_type = 0u;
    host_root = 0u;
    host_content = 0u;
    host_last_tick = 0u;
    host_visible = 0u;
    host_animation_ticks = 0u;
    host_call_count = 0u;
    host_role = 0u;
    host_display_active = 0u;
    host_tick = 0u;
    host_message_result = 0u;
}

void open_cfw_test_system_alert_set_inputs(uint32_t role, uint32_t active, uint32_t tick, uint32_t result)
{
    host_role = role;
    host_display_active = active;
    host_tick = tick;
    host_message_result = result;
}

void open_cfw_test_system_alert_set_type(uint8_t value) { host_alert_type = value; }
void open_cfw_test_system_alert_set_last_tick(uint32_t value) { host_last_tick = value; }
uint32_t open_cfw_test_system_alert_state(uint32_t index)
{
    switch (index) {
    case 0u: return host_alert_type;
    case 1u: return (uint32_t)host_root;
    case 2u: return (uint32_t)host_content;
    case 3u: return host_last_tick;
    case 4u: return host_visible;
    case 5u: return host_animation_ticks;
    case 6u: return (uint32_t)host_page_descriptor[1];
    default: return 0u;
    }
}

uint32_t open_cfw_test_system_alert_call_count(uint32_t id)
{
    uint32_t i;
    uint32_t count = 0u;
    for (i = 0u; i < host_call_count; ++i) if (host_calls[i].id == id) ++count;
    return count;
}

uintptr_t open_cfw_test_system_alert_call_arg(uint32_t id, uint32_t occurrence, uint32_t argument)
{
    uint32_t i;
    for (i = 0u; i < host_call_count; ++i) {
        if (host_calls[i].id == id && occurrence-- == 0u) {
            const uintptr_t *args = &host_calls[i].a;
            return argument < 4u ? args[argument] : 0u;
        }
    }
    return 0u;
}
