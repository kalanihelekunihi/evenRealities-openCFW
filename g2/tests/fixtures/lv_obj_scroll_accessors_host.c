#include <stdint.h>
#include <string.h>

/* Test hooks for the two retained cross-boundary calls, installed before the
 * production translation unit is pasted in below (see
 * `lv_obj_scroll_accessors.c`'s `#ifndef`-guarded macros). */
static void open_cfw_test_allocate_spec_attr(void *obj);
static void *open_cfw_test_anim_get(const void *var, const void *exec_cb);

#define OPEN_CFW_LV_OBJ_ALLOCATE_SPEC_ATTR(obj) open_cfw_test_allocate_spec_attr(obj)
#define OPEN_CFW_LV_ANIM_GET(var, exec_cb) open_cfw_test_anim_get(var, exec_cb)

#include "../../components/apollo_main/core_overlay/lv_obj_scroll_accessors.c"

static unsigned open_cfw_test_allocate_calls;
static open_cfw_lv_obj_view_t *open_cfw_test_allocate_last_obj;
static open_cfw_lv_obj_spec_attr_view_t open_cfw_test_spec_attr_storage;

static void open_cfw_test_allocate_spec_attr(void *obj)
{
    open_cfw_lv_obj_view_t *view = (open_cfw_lv_obj_view_t *)obj;

    open_cfw_test_allocate_calls += 1U;
    open_cfw_test_allocate_last_obj = view;
    if (view->spec_attr == NULL) {
        memset(&open_cfw_test_spec_attr_storage, 0, sizeof(open_cfw_test_spec_attr_storage));
        view->spec_attr = &open_cfw_test_spec_attr_storage;
    }
}

static unsigned open_cfw_test_anim_get_calls;
static const void *open_cfw_test_anim_get_last_var;
static const void *open_cfw_test_anim_get_last_cb;
static const void *open_cfw_test_anim_get_first_cb;
static const unsigned char *open_cfw_test_anim_x_result;
static const unsigned char *open_cfw_test_anim_y_result;

static void *open_cfw_test_anim_get(const void *var, const void *exec_cb)
{
    open_cfw_test_anim_get_calls += 1U;
    if (open_cfw_test_anim_get_calls == 1U) {
        open_cfw_test_anim_get_first_cb = exec_cb;
    }
    open_cfw_test_anim_get_last_var = var;
    open_cfw_test_anim_get_last_cb = exec_cb;
    if (exec_cb == OPEN_CFW_LV_OBJ_SCROLL_X_ANIM_CB) {
        return (void *)(uintptr_t)open_cfw_test_anim_x_result;
    }
    if (exec_cb == OPEN_CFW_LV_OBJ_SCROLL_Y_ANIM_CB) {
        return (void *)(uintptr_t)open_cfw_test_anim_y_result;
    }
    return NULL;
}

/* ---- test-facing surface ---- */

void open_cfw_test_lv_obj_scroll_reset(void)
{
    open_cfw_test_allocate_calls = 0U;
    open_cfw_test_allocate_last_obj = NULL;
    memset(&open_cfw_test_spec_attr_storage, 0, sizeof(open_cfw_test_spec_attr_storage));
    open_cfw_test_anim_get_calls = 0U;
    open_cfw_test_anim_get_last_var = NULL;
    open_cfw_test_anim_get_last_cb = NULL;
    open_cfw_test_anim_get_first_cb = NULL;
    open_cfw_test_anim_x_result = NULL;
    open_cfw_test_anim_y_result = NULL;
}

open_cfw_lv_obj_view_t *open_cfw_test_lv_obj_scroll_make_obj_no_spec_attr(void)
{
    static open_cfw_lv_obj_view_t obj;
    memset(&obj, 0, sizeof(obj));
    obj.spec_attr = NULL;
    return &obj;
}

open_cfw_lv_obj_view_t *open_cfw_test_lv_obj_scroll_make_obj_with_spec_attr(
    int32_t scroll_x, int32_t scroll_y, uint16_t flags
)
{
    static open_cfw_lv_obj_view_t obj;
    memset(&obj, 0, sizeof(obj));
    memset(&open_cfw_test_spec_attr_storage, 0, sizeof(open_cfw_test_spec_attr_storage));
    open_cfw_test_spec_attr_storage.scroll_x = scroll_x;
    open_cfw_test_spec_attr_storage.scroll_y = scroll_y;
    open_cfw_test_spec_attr_storage.flags = flags;
    obj.spec_attr = &open_cfw_test_spec_attr_storage;
    return &obj;
}

uint16_t open_cfw_test_lv_obj_scroll_flags(void)
{
    return open_cfw_test_spec_attr_storage.flags;
}

unsigned open_cfw_test_lv_obj_scroll_allocate_calls(void)
{
    return open_cfw_test_allocate_calls;
}

int open_cfw_test_lv_obj_scroll_allocate_last_obj_matches(const void *obj)
{
    return open_cfw_test_allocate_last_obj == obj;
}

void open_cfw_test_lv_obj_scroll_set_anim_results(
    int32_t x_end_value, int have_x, int32_t y_end_value, int have_y
)
{
    static unsigned char x_storage[0x30];
    static unsigned char y_storage[0x30];

    if (have_x) {
        memset(x_storage, 0, sizeof(x_storage));
        memcpy(x_storage + OPEN_CFW_LV_ANIM_END_VALUE_OFFSET, &x_end_value, sizeof(x_end_value));
        open_cfw_test_anim_x_result = x_storage;
    } else {
        open_cfw_test_anim_x_result = NULL;
    }
    if (have_y) {
        memset(y_storage, 0, sizeof(y_storage));
        memcpy(y_storage + OPEN_CFW_LV_ANIM_END_VALUE_OFFSET, &y_end_value, sizeof(y_end_value));
        open_cfw_test_anim_y_result = y_storage;
    } else {
        open_cfw_test_anim_y_result = NULL;
    }
}

unsigned open_cfw_test_lv_obj_scroll_anim_get_calls(void)
{
    return open_cfw_test_anim_get_calls;
}

const void *open_cfw_test_lv_obj_scroll_anim_get_last_cb(void)
{
    return open_cfw_test_anim_get_last_cb;
}

const void *open_cfw_test_lv_obj_scroll_anim_get_first_cb(void)
{
    return open_cfw_test_anim_get_first_cb;
}

int open_cfw_test_lv_obj_scroll_anim_get_last_var_matches(const void *obj)
{
    return open_cfw_test_anim_get_last_var == obj;
}

const void *open_cfw_test_lv_obj_scroll_x_anim_cb(void)
{
    return OPEN_CFW_LV_OBJ_SCROLL_X_ANIM_CB;
}

const void *open_cfw_test_lv_obj_scroll_y_anim_cb(void)
{
    return OPEN_CFW_LV_OBJ_SCROLL_Y_ANIM_CB;
}

/* ---- candidates under test ---- */

int32_t open_cfw_test_get_scroll_x(open_cfw_lv_obj_view_t *obj)
{
    return open_cfw_lv_obj_get_scroll_x(obj);
}

int32_t open_cfw_test_get_scroll_y(open_cfw_lv_obj_view_t *obj)
{
    return open_cfw_lv_obj_get_scroll_y(obj);
}

int32_t open_cfw_test_get_scroll_top(open_cfw_lv_obj_view_t *obj)
{
    return open_cfw_lv_obj_get_scroll_top(obj);
}

uint8_t open_cfw_test_get_scrollbar_mode(open_cfw_lv_obj_view_t *obj)
{
    return open_cfw_lv_obj_get_scrollbar_mode(obj);
}

uint16_t open_cfw_test_get_scroll_dir(open_cfw_lv_obj_view_t *obj)
{
    return open_cfw_lv_obj_get_scroll_dir(obj);
}

uint8_t open_cfw_test_get_scroll_snap_x(open_cfw_lv_obj_view_t *obj)
{
    return open_cfw_lv_obj_get_scroll_snap_x(obj);
}

uint8_t open_cfw_test_get_scroll_snap_y(open_cfw_lv_obj_view_t *obj)
{
    return open_cfw_lv_obj_get_scroll_snap_y(obj);
}

void open_cfw_test_set_scroll_snap_y(open_cfw_lv_obj_view_t *obj, uint8_t align)
{
    open_cfw_lv_obj_set_scroll_snap_y(obj, align);
}

void open_cfw_test_get_scroll_end(open_cfw_lv_obj_view_t *obj, int32_t *end)
{
    open_cfw_lv_obj_get_scroll_end(obj, end);
}

/* ---- independent oracle (hand-derived from the LVGL bitfield layout, not
 * from the candidate implementation) ---- */

int32_t open_cfw_oracle_get_scroll_x(const open_cfw_lv_obj_spec_attr_view_t *spec_attr)
{
    return spec_attr == NULL ? 0 : -spec_attr->scroll_x;
}

int32_t open_cfw_oracle_get_scroll_y(const open_cfw_lv_obj_spec_attr_view_t *spec_attr)
{
    return spec_attr == NULL ? 0 : -spec_attr->scroll_y;
}

uint8_t open_cfw_oracle_get_scrollbar_mode(const open_cfw_lv_obj_spec_attr_view_t *spec_attr)
{
    return spec_attr == NULL ? 3U : (uint8_t)(spec_attr->flags & 0x3U);
}

uint16_t open_cfw_oracle_get_scroll_dir(const open_cfw_lv_obj_spec_attr_view_t *spec_attr)
{
    return spec_attr == NULL ? 0x0FU : (uint16_t)((spec_attr->flags >> 6) & 0x0FU);
}

uint8_t open_cfw_oracle_get_scroll_snap_x(const open_cfw_lv_obj_spec_attr_view_t *spec_attr)
{
    return spec_attr == NULL ? 0U : (uint8_t)((spec_attr->flags >> 2) & 0x3U);
}

uint8_t open_cfw_oracle_get_scroll_snap_y(const open_cfw_lv_obj_spec_attr_view_t *spec_attr)
{
    return spec_attr == NULL ? 0U : (uint8_t)((spec_attr->flags >> 4) & 0x3U);
}
