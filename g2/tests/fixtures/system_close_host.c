#include <stdint.h>
#include <string.h>

struct host_fifo_layout {
    uint8_t data[128];
    uint16_t write_index;
    uint16_t read_index;
    uint16_t count;
};

static struct host_fifo_layout host_fifo;
static uintptr_t host_root;
static uintptr_t host_content;
static uint32_t host_timestamp;
static uintptr_t host_arrow;
static uintptr_t host_no_label;
static uintptr_t host_mini_label;
static uintptr_t host_yes_label;
static uint32_t host_selected;
static uintptr_t host_confirm_label;
static uint8_t host_style;
static uint8_t host_visible;
static uint8_t host_animating;
static uint32_t host_item_count;
static uintptr_t host_page_descriptor[2];
static const void *host_font = (const void *)(uintptr_t)0xf00du;

#define OPEN_CFW_SYSTEM_CLOSE_FIFO host_fifo
#define OPEN_CFW_SYSTEM_CLOSE_ROOT host_root
#define OPEN_CFW_SYSTEM_CLOSE_CONTENT host_content
#define OPEN_CFW_SYSTEM_CLOSE_TIMESTAMP host_timestamp
#define OPEN_CFW_SYSTEM_CLOSE_ARROW host_arrow
#define OPEN_CFW_SYSTEM_CLOSE_NO_LABEL host_no_label
#define OPEN_CFW_SYSTEM_CLOSE_MINI_LABEL host_mini_label
#define OPEN_CFW_SYSTEM_CLOSE_YES_LABEL host_yes_label
#define OPEN_CFW_SYSTEM_CLOSE_SELECTED host_selected
#define OPEN_CFW_SYSTEM_CLOSE_CONFIRM_LABEL host_confirm_label
#define OPEN_CFW_SYSTEM_CLOSE_STYLE host_style
#define OPEN_CFW_SYSTEM_CLOSE_VISIBLE host_visible
#define OPEN_CFW_SYSTEM_CLOSE_ANIMATING host_animating
#define OPEN_CFW_SYSTEM_CLOSE_ITEM_COUNT host_item_count
#define OPEN_CFW_SYSTEM_CLOSE_PAGE_DESCRIPTOR host_page_descriptor
#define OPEN_CFW_SYSTEM_CLOSE_FONT host_font

struct host_call { uint32_t id; uintptr_t a; uintptr_t b; uintptr_t c; uintptr_t d; };
static struct host_call host_calls[256];
static uint32_t host_call_count;
static uint32_t host_role;
static uint32_t host_display_active;
static uint32_t host_active_app;
static uint32_t host_display_state;
static uint32_t host_message_result;
static void (*host_animation_callback)(void);
void open_cfw_system_close_selection_anim_ready(void);

static void host_record(uint32_t id, uintptr_t a, uintptr_t b, uintptr_t c, uintptr_t d)
{
    if (host_call_count < 256u) {
        host_calls[host_call_count].id = id;
        host_calls[host_call_count].a = a;
        host_calls[host_call_count].b = b;
        host_calls[host_call_count].c = c;
        host_calls[host_call_count].d = d;
        ++host_call_count;
    }
}

static uintptr_t host_make_object(uintptr_t parent)
{
    uintptr_t result = 0x1000u + (uintptr_t)(host_call_count + 1u) * 0x100u;
    host_record(1u, parent, result, 0u, 0u);
    return result;
}

static int32_t host_get_width(uintptr_t object) { host_record(3u, object, 0u, 0u, 0u); return 400; }
static int32_t host_get_height(uintptr_t object) { host_record(4u, object, 0u, 0u, 0u); return 120; }
static uint32_t host_color(uint32_t value) { host_record(12u, value, 0u, 0u, 0u); return value ^ 0x55000000u; }
static uintptr_t host_make_image(uintptr_t parent) { host_record(25u, parent, 0u, 0u, 0u); return 0x3000u; }
static uintptr_t host_make_label(uintptr_t parent)
{
    uintptr_t value = 0x4000u + (uintptr_t)host_call_count * 0x10u;
    host_record(27u, parent, value, 0u, 0u);
    return value;
}
static uint32_t host_translation_id(const char *text) { return (uintptr_t)text == 0x007896a0u ? 1u : ((uintptr_t)text == 0x007896b0u ? 2u : 3u); }
static const char *host_translation(const char *text, uint32_t id) { host_record(30u, id, (uintptr_t)text, 0u, 0u); return text; }
static uint32_t host_get_display_state(uint32_t *app, uint32_t *state) { *app = host_active_app; *state = host_display_state; return 0u; }
static uint32_t host_message(uint32_t id, uint32_t app, const void *data, uint32_t length, uint32_t delay)
{
    uint32_t word = 0u;
    uint32_t index;
    const uint8_t *bytes = (const uint8_t *)data;
    for (index = 0u; bytes != 0 && index < length && index < 4u; ++index) word |= (uint32_t)bytes[index] << (index * 8u);
    host_record(id, app, word, length, delay);
    return host_message_result;
}
static void host_anim_init(void *animation) { memset(animation, 0, 96u); host_record(35u, 0u, 0u, 0u, 0u); }
static void host_anim_set_values(void *animation, int32_t start, int32_t end) { (void)animation; host_record(38u, (uintptr_t)start, (uintptr_t)end, 0u, 0u); }
static void host_anim_start(void *animation) { uint32_t *words=(uint32_t *)animation; host_animation_callback=open_cfw_system_close_selection_anim_ready; host_record(39u, words[0], words[12], 0u, 0u); }

#define OPEN_CFW_SYSTEM_CLOSE_MEMSET(p,v,n) memset((p),(v),(n))
#define OPEN_CFW_SYSTEM_CLOSE_OBJECT_CREATE(p) host_make_object(p)
#define OPEN_CFW_SYSTEM_CLOSE_SET_SIZE(o,w,h) host_record(2u,(o),(uintptr_t)(w),(uintptr_t)(h),0u)
#define OPEN_CFW_SYSTEM_CLOSE_GET_WIDTH(o) host_get_width(o)
#define OPEN_CFW_SYSTEM_CLOSE_GET_HEIGHT(o) host_get_height(o)
#define OPEN_CFW_SYSTEM_CLOSE_SET_X(o,v) host_record(5u,(o),(uintptr_t)(v),0u,0u)
#define OPEN_CFW_SYSTEM_CLOSE_SET_Y(o,v) host_record(6u,(o),(uintptr_t)(v),0u,0u)
#define OPEN_CFW_SYSTEM_CLOSE_SET_POS(o,x,y) host_record(7u,(o),(uintptr_t)(x),(uintptr_t)(y),0u)
#define OPEN_CFW_SYSTEM_CLOSE_CLEAR_FLAGS(o,v) host_record(8u,(o),(v),0u,0u)
#define OPEN_CFW_SYSTEM_CLOSE_ADD_FLAGS(o,v) host_record(9u,(o),(v),0u,0u)
#define OPEN_CFW_SYSTEM_CLOSE_SET_LAYOUT(o,v) host_record(10u,(o),(v),0u,0u)
#define OPEN_CFW_SYSTEM_CLOSE_SET_ALIGN(o,v) host_record(11u,(o),(v),0u,0u)
#define OPEN_CFW_SYSTEM_CLOSE_COLOR(v) host_color(v)
#define OPEN_CFW_SYSTEM_CLOSE_SET_BG_COLOR(o,v,s) host_record(13u,(o),(v),(s),0u)
#define OPEN_CFW_SYSTEM_CLOSE_SET_LABEL_BG_COLOR(o,v,s) host_record(14u,(o),(v),(s),0u)
#define OPEN_CFW_SYSTEM_CLOSE_SET_BG_OPACITY(o,v,s) host_record(15u,(o),(v),(s),0u)
#define OPEN_CFW_SYSTEM_CLOSE_SET_TEXT_COLOR(o,v,s) host_record(16u,(o),(v),(s),0u)
#define OPEN_CFW_SYSTEM_CLOSE_SET_TEXT_ALIGN(o,v,s) host_record(17u,(o),(v),(s),0u)
#define OPEN_CFW_SYSTEM_CLOSE_SET_PAD_TOP(o,v,s) host_record(18u,(o),(v),(s),0u)
#define OPEN_CFW_SYSTEM_CLOSE_SET_PAD_BOTTOM(o,v,s) host_record(19u,(o),(v),(s),0u)
#define OPEN_CFW_SYSTEM_CLOSE_SET_PAD_LEFT(o,v,s) host_record(20u,(o),(v),(s),0u)
#define OPEN_CFW_SYSTEM_CLOSE_SET_PAD_RIGHT(o,v,s) host_record(21u,(o),(v),(s),0u)
#define OPEN_CFW_SYSTEM_CLOSE_SET_SCROLLBAR_MODE(o,v) host_record(22u,(o),(v),0u,0u)
#define OPEN_CFW_SYSTEM_CLOSE_SET_FONT(o,f,s) host_record(23u,(o),(uintptr_t)(f),(s),0u)
#define OPEN_CFW_SYSTEM_CLOSE_DELETE_CHILDREN(o) host_record(24u,(o),0u,0u,0u)
#define OPEN_CFW_SYSTEM_CLOSE_HIDE(o,v) host_record(36u,(o),(v),0u,0u)
#define OPEN_CFW_SYSTEM_CLOSE_IMAGE_CREATE(o) host_make_image(o)
#define OPEN_CFW_SYSTEM_CLOSE_IMAGE_SET_SOURCE(o,s) host_record(26u,(o),(uintptr_t)(s),0u,0u)
#define OPEN_CFW_SYSTEM_CLOSE_LABEL_CREATE(o) host_make_label(o)
#define OPEN_CFW_SYSTEM_CLOSE_LABEL_SET_TEXT(o,s) host_record(28u,(o),(uintptr_t)(s),0u,0u)
#define OPEN_CFW_SYSTEM_CLOSE_TRANSLATION_ID(s) host_translation_id(s)
#define OPEN_CFW_SYSTEM_CLOSE_TRANSLATION(s,i) host_translation((s),(i))
#define OPEN_CFW_SYSTEM_CLOSE_ROLE() host_role
#define OPEN_CFW_SYSTEM_CLOSE_DISPLAY_ACTIVE() host_display_active
#define OPEN_CFW_SYSTEM_CLOSE_DISPLAY_STATE(a,s) host_get_display_state((a),(s))
#define OPEN_CFW_SYSTEM_CLOSE_POST_SELF(...) host_message(31u,__VA_ARGS__)
#define OPEN_CFW_SYSTEM_CLOSE_SEND_PAGE_ACTION(...) host_message(32u,__VA_ARGS__)
#define OPEN_CFW_SYSTEM_CLOSE_NOTIFY_STATE(...) host_message(33u,__VA_ARGS__)
#define OPEN_CFW_SYSTEM_CLOSE_SEND_FACTORY(...) host_message(34u,__VA_ARGS__)
#define OPEN_CFW_SYSTEM_CLOSE_TRANSITION(a,b,c,d) (host_record(37u,(a),(b),(c),(d)), host_message_result)
#define OPEN_CFW_SYSTEM_CLOSE_ANIM_INIT(a) host_anim_init(a)
#define OPEN_CFW_SYSTEM_CLOSE_ANIM_SET_VALUES(a,s,e) host_anim_set_values((a),(s),(e))
#define OPEN_CFW_SYSTEM_CLOSE_ANIM_START(a) host_anim_start(a)

#include "../../components/apollo_main/core_overlay/system_close.c"

void open_cfw_test_system_close_reset(void)
{
    memset(&host_fifo, 0, sizeof(host_fifo));
    memset(host_calls, 0, sizeof(host_calls));
    memset(host_page_descriptor, 0, sizeof(host_page_descriptor));
    host_root = host_content = host_arrow = host_no_label = host_mini_label = host_yes_label = host_confirm_label = 0u;
    host_timestamp = host_selected = host_item_count = 0u;
    host_style = host_visible = host_animating = 0u;
    host_call_count = host_role = host_display_active = host_active_app = host_display_state = host_message_result = 0u;
    host_animation_callback = 0;
}

void open_cfw_test_system_close_inputs(uint32_t role, uint32_t active, uint32_t app, uint32_t state, uint32_t result)
{ host_role = role; host_display_active = active; host_active_app = app; host_display_state = state; host_message_result = result; }
void open_cfw_test_system_close_set_state(uint32_t index, uint32_t value)
{
    switch (index) {
    case 0u: host_style=(uint8_t)value; break; case 1u: host_selected=value; break;
    case 2u: host_item_count=value; break; case 3u: host_animating=(uint8_t)value; break;
    case 4u: host_visible=(uint8_t)value; break; default: break;
    }
}
uint32_t open_cfw_test_system_close_state(uint32_t index)
{
    switch (index) {
    case 0u:return host_style; case 1u:return host_selected; case 2u:return host_item_count;
    case 3u:return host_animating; case 4u:return host_visible; case 5u:return host_timestamp;
    case 6u:return host_fifo.count; case 7u:return (uint32_t)host_root; case 8u:return (uint32_t)host_content;
    case 9u:return (uint32_t)host_arrow; case 10u:return (uint32_t)host_no_label; case 11u:return (uint32_t)host_yes_label;
    case 12u:return (uint32_t)host_confirm_label; case 13u:return (uint32_t)host_page_descriptor[1]; default:return 0u;
    }
}
uint32_t open_cfw_test_system_close_call_count(uint32_t id)
{ uint32_t i,n=0u; for(i=0u;i<host_call_count;++i) if(host_calls[i].id==id) ++n; return n; }
uintptr_t open_cfw_test_system_close_call_arg(uint32_t id,uint32_t occurrence,uint32_t argument)
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
void open_cfw_test_system_close_finish_animation(void) { if(host_animation_callback!=0) host_animation_callback(); }
