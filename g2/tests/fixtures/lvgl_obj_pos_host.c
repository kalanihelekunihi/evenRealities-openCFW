/* Host oracle for the reconstructed LVGL v9.3.0-dev lv_obj_pos.c geometry
 * functions (see components/apollo_main/core_overlay/lvgl_obj_pos.c).
 *
 * The production offsets assume the real target's 4-byte pointer width;
 * this fixture predefines them via offsetof() against its own 64-bit
 * object model before including the production file, so the very same
 * pointer-chasing source is exercised here as on-device. */
#include <setjmp.h>
#include <stddef.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>

typedef struct test_obj test_obj;

typedef struct test_spec_attr {
    test_obj **children;
} test_spec_attr;

struct test_obj {
    test_obj *parent;
    test_spec_attr *spec_attr;
    int32_t x1;
    int32_t y1;
    int32_t x2;
    int32_t y2;

    /* test-only instrumentation; never touched via offset arithmetic */
    int32_t style_width;
    int32_t style_height;
    int32_t style_x;
    int32_t style_y;
    int32_t style_align;
    int32_t style_translate_x;
    int32_t style_translate_y;
    int32_t style_base_dir;
    int32_t style_space_left;
    int32_t style_space_right;
    int32_t style_space_top;
    int32_t style_space_bottom;
    int is_layout_positioned;
    int layout_dirty_calls;
    uint32_t flags;
    int32_t scroll_x;
    int32_t scroll_y;
    int32_t self_size_x;
    int32_t self_size_y;
    int invalidate_calls;
    int scrollbar_invalidate_calls;
    int send_event_calls;
    uint32_t last_event_code;
    void *last_event_param;
};

#define OPEN_CFW_LV_OBJ_PARENT_OFFSET     offsetof(test_obj, parent)
#define OPEN_CFW_LV_OBJ_SPEC_ATTR_OFFSET  offsetof(test_obj, spec_attr)
#define OPEN_CFW_LV_OBJ_COORDS_OFFSET     offsetof(test_obj, x1)

#define OPEN_CFW_LVGL_OBJ_POS_BUILD_ALL 1
#include "../../components/apollo_main/core_overlay/lvgl_obj_pos.c"

/* ---- retained provider mocks ---------------------------------------- */

int32_t open_cfw_retained_lvgl_obj_pos_get_style_width(const open_cfw_lv_obj *o, uint32_t s)
{ (void)s; return ((const test_obj *)o)->style_width; }
int32_t open_cfw_retained_lvgl_obj_pos_get_style_height(const open_cfw_lv_obj *o, uint32_t s)
{ (void)s; return ((const test_obj *)o)->style_height; }
int32_t open_cfw_retained_lvgl_obj_pos_get_style_x(const open_cfw_lv_obj *o, uint32_t s)
{ (void)s; return ((const test_obj *)o)->style_x; }
int32_t open_cfw_retained_lvgl_obj_pos_get_style_y(const open_cfw_lv_obj *o, uint32_t s)
{ (void)s; return ((const test_obj *)o)->style_y; }
int32_t open_cfw_retained_lvgl_obj_pos_get_style_align(const open_cfw_lv_obj *o, uint32_t s)
{ (void)s; return ((const test_obj *)o)->style_align; }
int32_t open_cfw_retained_lvgl_obj_pos_get_style_translate_x(const open_cfw_lv_obj *o, uint32_t s)
{ (void)s; return ((const test_obj *)o)->style_translate_x; }
int32_t open_cfw_retained_lvgl_obj_pos_get_style_translate_y(const open_cfw_lv_obj *o, uint32_t s)
{ (void)s; return ((const test_obj *)o)->style_translate_y; }
int32_t open_cfw_retained_lvgl_obj_pos_get_style_base_dir(const open_cfw_lv_obj *o, uint32_t s)
{ (void)s; return ((const test_obj *)o)->style_base_dir; }
int32_t open_cfw_retained_lvgl_obj_pos_get_style_space_left(const open_cfw_lv_obj *o, uint32_t s)
{ (void)s; return ((const test_obj *)o)->style_space_left; }
int32_t open_cfw_retained_lvgl_obj_pos_get_style_space_right(const open_cfw_lv_obj *o, uint32_t s)
{ (void)s; return ((const test_obj *)o)->style_space_right; }
int32_t open_cfw_retained_lvgl_obj_pos_get_style_space_top(const open_cfw_lv_obj *o, uint32_t s)
{ (void)s; return ((const test_obj *)o)->style_space_top; }
int32_t open_cfw_retained_lvgl_obj_pos_get_style_space_bottom(const open_cfw_lv_obj *o, uint32_t s)
{ (void)s; return ((const test_obj *)o)->style_space_bottom; }
int open_cfw_retained_lvgl_obj_pos_is_layout_positioned(const open_cfw_lv_obj *o)
{ return ((const test_obj *)o)->is_layout_positioned; }
void open_cfw_retained_lvgl_obj_pos_mark_layout_as_dirty(open_cfw_lv_obj *o)
{ ((test_obj *)o)->layout_dirty_calls++; }
void open_cfw_retained_lvgl_obj_pos_get_coords(const open_cfw_lv_obj *o, open_cfw_lv_area *coords)
{
    const test_obj *obj = (const test_obj *)o;
    coords->x1 = obj->x1;
    coords->y1 = obj->y1;
    coords->x2 = obj->x2;
    coords->y2 = obj->y2;
}
int open_cfw_retained_lvgl_obj_pos_has_flag(const open_cfw_lv_obj *o, uint32_t flag)
{ return (((const test_obj *)o)->flags & flag) != 0U; }
open_cfw_lv_obj *open_cfw_retained_lvgl_obj_pos_get_parent(const open_cfw_lv_obj *o)
{ return (open_cfw_lv_obj *)((const test_obj *)o)->parent; }
uint32_t open_cfw_retained_lvgl_obj_pos_get_child_count(const open_cfw_lv_obj *o)
{
    const test_obj *obj = (const test_obj *)o;
    if (obj->spec_attr == NULL) {
        return 0U;
    }
    uint32_t count = 0U;
    while (obj->spec_attr->children[count] != NULL) {
        ++count;
    }
    return count;
}
int32_t open_cfw_retained_lvgl_obj_pos_get_scroll_x(const open_cfw_lv_obj *o)
{ return ((const test_obj *)o)->scroll_x; }
int32_t open_cfw_retained_lvgl_obj_pos_get_scroll_y(const open_cfw_lv_obj *o)
{ return ((const test_obj *)o)->scroll_y; }
int open_cfw_retained_lvgl_obj_pos_area_is_in(
    const open_cfw_lv_area *in_area, const open_cfw_lv_area *out_area, int32_t radius
)
{
    (void)radius;
    return in_area->x1 >= out_area->x1 && in_area->y1 >= out_area->y1 &&
           in_area->x2 <= out_area->x2 && in_area->y2 <= out_area->y2;
}
void open_cfw_retained_lvgl_obj_pos_scrollbar_invalidate(open_cfw_lv_obj *o)
{ ((test_obj *)o)->scrollbar_invalidate_calls++; }
void open_cfw_retained_lvgl_obj_pos_area_copy(open_cfw_lv_area *dest, const open_cfw_lv_area *src)
{ *dest = *src; }
int32_t open_cfw_retained_lvgl_obj_pos_area_get_width(const open_cfw_lv_area *area)
{ return area->x2 - area->x1 + 1; }
int32_t open_cfw_retained_lvgl_obj_pos_area_get_height(const open_cfw_lv_area *area)
{ return area->y2 - area->y1 + 1; }

static int32_t g_self_size_probe_x = -1;
static int32_t g_self_size_probe_y = -1;

void open_cfw_retained_lvgl_obj_pos_send_event(open_cfw_lv_obj *o, uint32_t event_code, void *param)
{
    test_obj *obj = (test_obj *)o;
    obj->send_event_calls++;
    obj->last_event_code = event_code;
    obj->last_event_param = param;
    if (event_code == OPEN_CFW_LV_EVENT_GET_SELF_SIZE) {
        int32_t *p = (int32_t *)param;
        g_self_size_probe_x = p[0];
        g_self_size_probe_y = p[1];
        p[0] = obj->self_size_x;
        p[1] = obj->self_size_y;
    }
}
void open_cfw_retained_lvgl_obj_pos_invalidate(const open_cfw_lv_obj *o)
{
    test_obj *obj;
    memcpy(&obj, &o, sizeof(obj));
    obj->invalidate_calls++;
}

static jmp_buf g_assert_jmp;
static int g_log_calls;
static int g_last_log_level;
static char g_last_log_file[160];
static int g_last_log_line;
static char g_last_log_func[64];

void open_cfw_retained_lvgl_obj_pos_log_add(
    int level, const char *file, int line, const char *func, const char *format, ...
)
{
    (void)format;
    g_log_calls++;
    g_last_log_level = level;
    snprintf(g_last_log_file, sizeof(g_last_log_file), "%s", file);
    g_last_log_line = line;
    snprintf(g_last_log_func, sizeof(g_last_log_func), "%s", func);
    longjmp(g_assert_jmp, 1);
}

/* ---- test world ------------------------------------------------------ */

static test_obj g_objs[4];
static test_spec_attr g_spec_attr[4];
static test_obj *g_children[4][3];

static test_obj *obj_by_id(int id)
{
    if (id < 0 || id >= 4) {
        return NULL;
    }
    return &g_objs[id];
}

static open_cfw_lv_obj *lv_obj_by_id(int id)
{
    return (open_cfw_lv_obj *)obj_by_id(id);
}

void open_cfw_test_reset(void)
{
    int i;
    int j;
    for (i = 0; i < 4; ++i) {
        test_obj zero = {0};
        g_objs[i] = zero;
        g_spec_attr[i].children = g_children[i];
        for (j = 0; j < 3; ++j) {
            g_children[i][j] = NULL;
        }
    }
    g_log_calls = 0;
    g_self_size_probe_x = -1;
    g_self_size_probe_y = -1;
}

void open_cfw_test_set_coords(int id, int32_t x1, int32_t y1, int32_t x2, int32_t y2)
{
    test_obj *obj = obj_by_id(id);
    obj->x1 = x1; obj->y1 = y1; obj->x2 = x2; obj->y2 = y2;
}
void open_cfw_test_set_style_wh(int id, int32_t w, int32_t h)
{ test_obj *o = obj_by_id(id); o->style_width = w; o->style_height = h; }
void open_cfw_test_set_style_xy(int id, int32_t x, int32_t y)
{ test_obj *o = obj_by_id(id); o->style_x = x; o->style_y = y; }
void open_cfw_test_set_style_spacing(int id, int32_t l, int32_t r, int32_t t, int32_t b)
{
    test_obj *o = obj_by_id(id);
    o->style_space_left = l; o->style_space_right = r;
    o->style_space_top = t; o->style_space_bottom = b;
}
void open_cfw_test_set_style_align(int id, int32_t align) { obj_by_id(id)->style_align = align; }
void open_cfw_test_set_style_translate(int id, int32_t tx, int32_t ty)
{ test_obj *o = obj_by_id(id); o->style_translate_x = tx; o->style_translate_y = ty; }
void open_cfw_test_set_style_base_dir(int id, int32_t dir) { obj_by_id(id)->style_base_dir = dir; }
void open_cfw_test_set_flags(int id, uint32_t flags) { obj_by_id(id)->flags = flags; }
void open_cfw_test_set_scroll(int id, int32_t sx, int32_t sy)
{ test_obj *o = obj_by_id(id); o->scroll_x = sx; o->scroll_y = sy; }
void open_cfw_test_set_layout_positioned(int id, int v) { obj_by_id(id)->is_layout_positioned = v; }
void open_cfw_test_set_self_size(int id, int32_t w, int32_t h)
{ test_obj *o = obj_by_id(id); o->self_size_x = w; o->self_size_y = h; }
void open_cfw_test_link_parent(int child_id, int parent_id)
{ obj_by_id(child_id)->parent = (parent_id < 0) ? NULL : obj_by_id(parent_id); }
void open_cfw_test_set_children(int parent_id, int child_a, int child_b)
{
    test_obj *parent = obj_by_id(parent_id);
    parent->spec_attr = &g_spec_attr[parent_id];
    g_children[parent_id][0] = (child_a < 0) ? NULL : obj_by_id(child_a);
    g_children[parent_id][1] = (child_b < 0) ? NULL : obj_by_id(child_b);
    g_children[parent_id][2] = NULL;
}

int32_t open_cfw_test_get_coord(int id, int field)
{
    test_obj *o = obj_by_id(id);
    switch (field) {
        case 0: return o->x1;
        case 1: return o->y1;
        case 2: return o->x2;
        default: return o->y2;
    }
}
int open_cfw_test_get_invalidate_calls(int id) { return obj_by_id(id)->invalidate_calls; }
int open_cfw_test_get_scrollbar_invalidate_calls(int id) { return obj_by_id(id)->scrollbar_invalidate_calls; }
int open_cfw_test_get_send_event_calls(int id) { return obj_by_id(id)->send_event_calls; }
uint32_t open_cfw_test_get_last_event_code(int id) { return obj_by_id(id)->last_event_code; }
int open_cfw_test_get_layout_dirty_calls(int id) { return obj_by_id(id)->layout_dirty_calls; }
int32_t open_cfw_test_get_self_size_probe_x(void) { return g_self_size_probe_x; }
int32_t open_cfw_test_get_self_size_probe_y(void) { return g_self_size_probe_y; }
int open_cfw_test_get_log_calls(void) { return g_log_calls; }
int open_cfw_test_get_last_log_line(void) { return g_last_log_line; }
const char *open_cfw_test_get_last_log_func(void) { return g_last_log_func; }
const char *open_cfw_test_get_last_log_file(void) { return g_last_log_file; }
int open_cfw_test_get_last_log_level(void) { return g_last_log_level; }

static open_cfw_lv_area g_last_area;
int32_t open_cfw_test_get_last_area(int field)
{
    switch (field) {
        case 0: return g_last_area.x1;
        case 1: return g_last_area.y1;
        case 2: return g_last_area.x2;
        default: return g_last_area.y2;
    }
}

/* ---- calls under test -------------------------------------------------*/

int32_t open_cfw_test_call_get_width(int id) { return open_cfw_lvgl_obj_pos_get_width(lv_obj_by_id(id)); }
int32_t open_cfw_test_call_get_height(int id) { return open_cfw_lvgl_obj_pos_get_height(lv_obj_by_id(id)); }
int32_t open_cfw_test_call_get_content_width(int id) { return open_cfw_lvgl_obj_pos_get_content_width(lv_obj_by_id(id)); }
int32_t open_cfw_test_call_get_content_height(int id) { return open_cfw_lvgl_obj_pos_get_content_height(lv_obj_by_id(id)); }
void open_cfw_test_call_get_content_coords(int id)
{ open_cfw_lvgl_obj_pos_get_content_coords(lv_obj_by_id(id), &g_last_area); }
int32_t open_cfw_test_call_get_self_width(int id) { return open_cfw_lvgl_obj_pos_get_self_width(lv_obj_by_id(id)); }
int32_t open_cfw_test_call_get_self_height(int id) { return open_cfw_lvgl_obj_pos_get_self_height(lv_obj_by_id(id)); }
int open_cfw_test_call_refresh_self_size(int id) { return open_cfw_lvgl_obj_pos_refresh_self_size(lv_obj_by_id(id)); }
void open_cfw_test_call_move_children_by(int id, int32_t dx, int32_t dy, int ignore_floating)
{ open_cfw_lvgl_obj_pos_move_children_by(lv_obj_by_id(id), dx, dy, ignore_floating); }
void open_cfw_test_call_move_to(int id, int32_t x, int32_t y)
{ open_cfw_lvgl_obj_pos_move_to(lv_obj_by_id(id), x, y); }
void open_cfw_test_call_refr_pos(int id) { open_cfw_lvgl_obj_pos_refr_pos(lv_obj_by_id(id)); }

/* NULL-obj assert scenarios: returns 1 if the retained LV_ASSERT_NULL path
 * fired (log_add called, longjmp escaped the `while(1);`), 0 otherwise. */
int open_cfw_test_call_assert_scenario(int which)
{
    if (setjmp(g_assert_jmp) != 0) {
        return 1;
    }
    switch (which) {
        case 0: open_cfw_lvgl_obj_pos_get_width(NULL); break;
        case 1: open_cfw_lvgl_obj_pos_get_height(NULL); break;
        case 2: open_cfw_lvgl_obj_pos_get_content_width(NULL); break;
        case 3: open_cfw_lvgl_obj_pos_get_content_height(NULL); break;
        default: open_cfw_lvgl_obj_pos_get_content_coords(NULL, &g_last_area); break;
    }
    return 0;
}
