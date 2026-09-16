/*
 * SPDX-License-Identifier: MIT
 *
 * Host substitution for the AM-040 LVGL layout/grid tranche: captures the
 * arguments forwarded to the shared style-lookup core and to every
 * retained-stock provider instead of calling the fixed stock addresses,
 * and translates test object ids to host buffers for the ports' own
 * field reads. Production macros in the included sources are overridden
 * here before inclusion.
 */

#include <stddef.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>

/* ---- object id translation ---- */

#define OPEN_CFW_TEST_GRID_MAX_OBJECTS 24

static void *open_cfw_test_grid_objects[OPEN_CFW_TEST_GRID_MAX_OBJECTS];
static unsigned int open_cfw_test_grid_object_ids[OPEN_CFW_TEST_GRID_MAX_OBJECTS];
static unsigned char open_cfw_test_grid_zero_guard[64];
unsigned int open_cfw_test_grid_misses;

static const unsigned char *stub_obj_bytes(unsigned int id)
{
    unsigned int i;
    for (i = 0U; i < OPEN_CFW_TEST_GRID_MAX_OBJECTS; i += 1U) {
        if (open_cfw_test_grid_object_ids[i] == id &&
            open_cfw_test_grid_objects[i] != 0) {
            return (const unsigned char *)open_cfw_test_grid_objects[i];
        }
    }
    open_cfw_test_grid_misses += 1U;
    return open_cfw_test_grid_zero_guard;
}

static unsigned char *stub_obj_bytes_mut(unsigned int id)
{
    return (unsigned char *)stub_obj_bytes(id);
}

#define OPEN_CFW_LVGL_OBJ_BYTES(obj) stub_obj_bytes((unsigned int)(obj))
#define OPEN_CFW_LVGL_OBJ_BYTES_MUT(obj) stub_obj_bytes_mut((unsigned int)(obj))

/* ---- shared style-lookup core ---- */

unsigned int open_cfw_test_grid_core_calls;
unsigned int open_cfw_test_grid_core_obj;
unsigned int open_cfw_test_grid_core_part;
unsigned int open_cfw_test_grid_core_prop;
unsigned int open_cfw_test_grid_prop_value[256];

static unsigned int stub_core_fn(
    unsigned int obj,
    unsigned int part,
    unsigned int property
)
{
    open_cfw_test_grid_core_calls += 1U;
    open_cfw_test_grid_core_obj = obj;
    open_cfw_test_grid_core_part = part;
    open_cfw_test_grid_core_prop = property;
    return open_cfw_test_grid_prop_value[property & 0xFFU];
}

#define OPEN_CFW_LVGL_LAYOUT_GETTER_CORE(obj, part, property) \
    stub_core_fn((obj), (part), (property))

/* ---- retained provider stubs (prototypes before inclusion) ---- */

static int stub_width_fn(unsigned int obj);
static int stub_height_fn(unsigned int obj);
static int stub_scroll_x_fn(unsigned int obj);
static int stub_scroll_y_fn(unsigned int obj);
static void stub_refr_fn(unsigned int obj);
static void stub_event_fn(unsigned int obj, unsigned int code, unsigned int param);
static unsigned int stub_child_fn(unsigned int obj, unsigned int idx);
static int stub_content_w_fn(unsigned int obj);
static int stub_content_h_fn(unsigned int obj);
static void *stub_memset_fn(void *dst, unsigned int value, unsigned int len);
static void stub_free_fn(void *ptr);
static void stub_calc_cols_fn(unsigned int cont, void *calc);
static void stub_calc_rows_fn(unsigned int cont, void *calc);
static void stub_repos_fn(unsigned int item, void *calc, void *hint);
static int stub_align_fn(int cont_size, unsigned int auto_size, unsigned int align,
    unsigned int gap, unsigned int track_num, void *sizes, void *positions,
    unsigned int reverse);
static unsigned int stub_parent_fn(unsigned int obj);
static int stub_has_flag_fn(unsigned int obj, unsigned int mask);
static unsigned int stub_child_count_fn(unsigned int obj);
static void *stub_malloc_fn(unsigned int size);
static void *stub_memcpy_fn(void *dst, const void *src, unsigned int len);
static void stub_invalidate_fn(unsigned int obj);
static void stub_area_set_w_fn(void *area, int value);
static void stub_area_set_h_fn(void *area, int value);
static int stub_area_get_w_fn(const void *area);
static int stub_area_get_h_fn(const void *area);
static void stub_move_children_fn(unsigned int obj, int dx, int dy,
    unsigned int ignore);
static void stub_log_warn_fn(int level, const char *file, int line,
    const char *func, const char *format);

#define OPEN_CFW_LVGL_RETAINED_OBJ_GET_WIDTH(obj) stub_width_fn(obj)
#define OPEN_CFW_LVGL_RETAINED_OBJ_GET_HEIGHT(obj) stub_height_fn(obj)
#define OPEN_CFW_LVGL_RETAINED_OBJ_GET_SCROLL_X(obj) stub_scroll_x_fn(obj)
#define OPEN_CFW_LVGL_RETAINED_OBJ_GET_SCROLL_Y(obj) stub_scroll_y_fn(obj)
#define OPEN_CFW_LVGL_RETAINED_OBJ_REFR_SIZE(obj) stub_refr_fn(obj)
#define OPEN_CFW_LVGL_RETAINED_OBJ_SEND_EVENT(obj, code, param) \
    stub_event_fn((obj), (code), (param))
#define OPEN_CFW_LVGL_RETAINED_OBJ_GET_CHILD(obj, idx) stub_child_fn((obj), (idx))
#define OPEN_CFW_LVGL_RETAINED_OBJ_GET_CONTENT_WIDTH(obj) stub_content_w_fn(obj)
#define OPEN_CFW_LVGL_RETAINED_OBJ_GET_CONTENT_HEIGHT(obj) stub_content_h_fn(obj)
#define OPEN_CFW_LVGL_RETAINED_MEMSET(dst, value, len) \
    stub_memset_fn((dst), (value), (len))
#define OPEN_CFW_LVGL_RETAINED_FREE(ptr) stub_free_fn(ptr)
#define OPEN_CFW_LVGL_RETAINED_GRID_CALC_COLS(cont, calc) \
    stub_calc_cols_fn((cont), (calc))
#define OPEN_CFW_LVGL_RETAINED_GRID_CALC_ROWS(cont, calc) \
    stub_calc_rows_fn((cont), (calc))
#define OPEN_CFW_LVGL_RETAINED_GRID_ITEM_REPOS(item, calc, hint) \
    stub_repos_fn((item), (calc), (hint))
#define OPEN_CFW_LVGL_RETAINED_GRID_ALIGN(cont_size, auto_size, align, gap, track_num, sizes, positions, reverse) \
    stub_align_fn((cont_size), (auto_size), (align), (gap), (track_num), (sizes), (positions), (reverse))

#define OPEN_CFW_LVGL_RETAINED_OBJ_GET_PARENT(obj) stub_parent_fn(obj)
#define OPEN_CFW_LVGL_RETAINED_OBJ_HAS_FLAG_ANY(obj, mask) \
    stub_has_flag_fn((obj), (mask))
#define OPEN_CFW_LVGL_RETAINED_OBJ_GET_CHILD_COUNT(obj) stub_child_count_fn(obj)
#define OPEN_CFW_LVGL_RETAINED_MALLOC(size) stub_malloc_fn(size)
#define OPEN_CFW_LVGL_RETAINED_MEMCPY(dst, src, len) \
    stub_memcpy_fn((dst), (src), (len))
#define OPEN_CFW_LVGL_RETAINED_OBJ_INVALIDATE(obj) stub_invalidate_fn(obj)
#define OPEN_CFW_LVGL_RETAINED_AREA_SET_WIDTH(area, value) \
    stub_area_set_w_fn((area), (value))
#define OPEN_CFW_LVGL_RETAINED_AREA_SET_HEIGHT(area, value) \
    stub_area_set_h_fn((area), (value))
#define OPEN_CFW_LVGL_RETAINED_AREA_GET_WIDTH(area) stub_area_get_w_fn(area)
#define OPEN_CFW_LVGL_RETAINED_AREA_GET_HEIGHT(area) stub_area_get_h_fn(area)
#define OPEN_CFW_LVGL_RETAINED_OBJ_MOVE_CHILDREN_BY(obj, dx, dy, ignore) \
    stub_move_children_fn((obj), (dx), (dy), (ignore))
#define OPEN_CFW_LVGL_RETAINED_LOG_WARN(file, line, func, format) \
    stub_log_warn_fn(2, (file), (line), (func), (format))
static const int *test_col_templ_fn(unsigned int obj);
static const int *test_row_templ_fn(unsigned int obj);
#define OPEN_CFW_LVGL_GRID_COL_TEMPL(cont) test_col_templ_fn(cont)
#define OPEN_CFW_LVGL_GRID_ROW_TEMPL(cont) test_row_templ_fn(cont)

#define OPEN_CFW_LVGL_LAYOUT_REGISTRY_ANCHOR 0xA000U

#include "../../components/apollo_main/core_overlay/lvgl_layout_style_getters.c"
#include "../../components/apollo_main/core_overlay/lvgl_grid_engine.c"

/* ---- stub state ---- */

const char *open_cfw_test_grid_expected_warn_file =
    OPEN_CFW_LVGL_GRID_WARN_FILE;
const char *open_cfw_test_grid_expected_calc_cols_func =
    OPEN_CFW_LVGL_GRID_CALC_COLS_FUNC;
const char *open_cfw_test_grid_expected_calc_rows_func =
    OPEN_CFW_LVGL_GRID_CALC_ROWS_FUNC;
const char *open_cfw_test_grid_expected_calc_cols_format =
    OPEN_CFW_LVGL_GRID_CALC_COLS_WARN_FORMAT;
const char *open_cfw_test_grid_expected_calc_rows_format =
    OPEN_CFW_LVGL_GRID_CALC_ROWS_WARN_FORMAT;

unsigned int open_cfw_test_grid_width_calls;
unsigned int open_cfw_test_grid_width_obj;
int open_cfw_test_grid_width_value;
unsigned int open_cfw_test_grid_height_calls;
unsigned int open_cfw_test_grid_height_obj;
int open_cfw_test_grid_height_value;
unsigned int open_cfw_test_grid_scroll_x_calls;
int open_cfw_test_grid_scroll_x_value;
unsigned int open_cfw_test_grid_scroll_y_calls;
int open_cfw_test_grid_scroll_y_value;
unsigned int open_cfw_test_grid_refr_calls;
unsigned int open_cfw_test_grid_refr_obj;
unsigned int open_cfw_test_grid_event_calls;
unsigned int open_cfw_test_grid_event_obj;
unsigned int open_cfw_test_grid_event_code;
unsigned int open_cfw_test_grid_event_param;
unsigned int open_cfw_test_grid_child_calls;
unsigned int open_cfw_test_grid_child_obj;
unsigned int open_cfw_test_grid_child_idx;
unsigned int open_cfw_test_grid_child_value;
unsigned int open_cfw_test_grid_content_w_calls;
int open_cfw_test_grid_content_w_value;
unsigned int open_cfw_test_grid_content_h_calls;
int open_cfw_test_grid_content_h_value;
unsigned int open_cfw_test_grid_memset_calls;
void *open_cfw_test_grid_memset_dst;
unsigned int open_cfw_test_grid_memset_value;
unsigned int open_cfw_test_grid_memset_len;
unsigned int open_cfw_test_grid_free_count;
void *open_cfw_test_grid_free_ptrs[8];
unsigned int open_cfw_test_grid_cols_calls;
unsigned int open_cfw_test_grid_cols_cont;
unsigned int open_cfw_test_grid_cols_num;
unsigned int open_cfw_test_grid_rows_calls;
unsigned int open_cfw_test_grid_rows_cont;
unsigned int open_cfw_test_grid_rows_num;
unsigned int open_cfw_test_grid_repos_count;
unsigned int open_cfw_test_grid_repos_items[8];
int open_cfw_test_grid_repos_hint_x[8];
int open_cfw_test_grid_repos_hint_y[8];
unsigned int open_cfw_test_grid_align_calls;
int open_cfw_test_grid_align_size[2];
unsigned int open_cfw_test_grid_align_auto[2];
unsigned int open_cfw_test_grid_align_align[2];
unsigned int open_cfw_test_grid_align_gap[2];
unsigned int open_cfw_test_grid_align_num[2];
void *open_cfw_test_grid_align_sizes[2];
void *open_cfw_test_grid_align_positions[2];
unsigned int open_cfw_test_grid_align_reverse[2];
int open_cfw_test_grid_align_value;

unsigned int open_cfw_test_grid_child_list[8];
unsigned int open_cfw_test_grid_child_list_len;
unsigned int open_cfw_test_grid_width_ids[8];
int open_cfw_test_grid_width_vals[8];
unsigned int open_cfw_test_grid_width_list_len;
unsigned int open_cfw_test_grid_height_ids[8];
int open_cfw_test_grid_height_vals[8];
unsigned int open_cfw_test_grid_height_list_len;

static int stub_width_fn(unsigned int obj)
{
    unsigned int i;
    open_cfw_test_grid_width_calls += 1U;
    open_cfw_test_grid_width_obj = obj;
    for (i = 0U; i < open_cfw_test_grid_width_list_len && i < 8U; i += 1U) {
        if (open_cfw_test_grid_width_ids[i] == obj) {
            return open_cfw_test_grid_width_vals[i];
        }
    }
    return open_cfw_test_grid_width_value;
}

static int stub_height_fn(unsigned int obj)
{
    unsigned int i;
    open_cfw_test_grid_height_calls += 1U;
    open_cfw_test_grid_height_obj = obj;
    for (i = 0U; i < open_cfw_test_grid_height_list_len && i < 8U; i += 1U) {
        if (open_cfw_test_grid_height_ids[i] == obj) {
            return open_cfw_test_grid_height_vals[i];
        }
    }
    return open_cfw_test_grid_height_value;
}

static int stub_scroll_x_fn(unsigned int obj)
{
    (void)obj;
    open_cfw_test_grid_scroll_x_calls += 1U;
    return open_cfw_test_grid_scroll_x_value;
}

static int stub_scroll_y_fn(unsigned int obj)
{
    (void)obj;
    open_cfw_test_grid_scroll_y_calls += 1U;
    return open_cfw_test_grid_scroll_y_value;
}

static void stub_refr_fn(unsigned int obj)
{
    open_cfw_test_grid_refr_calls += 1U;
    open_cfw_test_grid_refr_obj = obj;
}

static void stub_event_fn(unsigned int obj, unsigned int code, unsigned int param)
{
    open_cfw_test_grid_event_calls += 1U;
    open_cfw_test_grid_event_obj = obj;
    open_cfw_test_grid_event_code = code;
    open_cfw_test_grid_event_param = param;
}

static unsigned int stub_child_fn(unsigned int obj, unsigned int idx)
{
    open_cfw_test_grid_child_calls += 1U;
    open_cfw_test_grid_child_obj = obj;
    open_cfw_test_grid_child_idx = idx;
    if (idx < open_cfw_test_grid_child_list_len && idx < 8U) {
        return open_cfw_test_grid_child_list[idx];
    }
    return open_cfw_test_grid_child_value;
}

static int stub_content_w_fn(unsigned int obj)
{
    (void)obj;
    open_cfw_test_grid_content_w_calls += 1U;
    return open_cfw_test_grid_content_w_value;
}

static int stub_content_h_fn(unsigned int obj)
{
    (void)obj;
    open_cfw_test_grid_content_h_calls += 1U;
    return open_cfw_test_grid_content_h_value;
}

static void *stub_memset_fn(void *dst, unsigned int value, unsigned int len)
{
    open_cfw_test_grid_memset_calls += 1U;
    open_cfw_test_grid_memset_dst = dst;
    open_cfw_test_grid_memset_value = value;
    open_cfw_test_grid_memset_len = len;
    memset(dst, (int)(value & 0xFFU), (size_t)len);
    return dst;
}

static void stub_free_fn(void *ptr)
{
    if (open_cfw_test_grid_free_count < 8U) {
        open_cfw_test_grid_free_ptrs[open_cfw_test_grid_free_count] = ptr;
    }
    open_cfw_test_grid_free_count += 1U;
}

static void stub_calc_cols_fn(unsigned int cont, void *calc)
{
    open_cfw_test_grid_cols_calls += 1U;
    open_cfw_test_grid_cols_cont = cont;
    ((open_cfw_lvgl_grid_calc_t *)calc)->col_num = open_cfw_test_grid_cols_num;
}

static void stub_calc_rows_fn(unsigned int cont, void *calc)
{
    open_cfw_test_grid_rows_calls += 1U;
    open_cfw_test_grid_rows_cont = cont;
    ((open_cfw_lvgl_grid_calc_t *)calc)->row_num = open_cfw_test_grid_rows_num;
}

static void stub_repos_fn(unsigned int item, void *calc, void *hint)
{
    unsigned int n = open_cfw_test_grid_repos_count;
    (void)calc;
    if (n < 8U) {
        open_cfw_test_grid_repos_items[n] = item;
        open_cfw_test_grid_repos_hint_x[n] =
            ((open_cfw_lvgl_grid_hint_t *)hint)->grid_abs_x;
        open_cfw_test_grid_repos_hint_y[n] =
            ((open_cfw_lvgl_grid_hint_t *)hint)->grid_abs_y;
    }
    open_cfw_test_grid_repos_count += 1U;
}

static int stub_align_fn(int cont_size, unsigned int auto_size, unsigned int align,
    unsigned int gap, unsigned int track_num, void *sizes, void *positions,
    unsigned int reverse)
{
    unsigned int n = open_cfw_test_grid_align_calls;
    if (n < 2U) {
        open_cfw_test_grid_align_size[n] = cont_size;
        open_cfw_test_grid_align_auto[n] = auto_size;
        open_cfw_test_grid_align_align[n] = align;
        open_cfw_test_grid_align_gap[n] = gap;
        open_cfw_test_grid_align_num[n] = track_num;
        open_cfw_test_grid_align_sizes[n] = sizes;
        open_cfw_test_grid_align_positions[n] = positions;
        open_cfw_test_grid_align_reverse[n] = reverse;
    }
    open_cfw_test_grid_align_calls += 1U;
    return open_cfw_test_grid_align_value;
}

unsigned int open_cfw_test_grid_parent_value;
unsigned int open_cfw_test_grid_has_flag_value;
unsigned int open_cfw_test_grid_child_count_value;
unsigned int open_cfw_test_grid_malloc_count;
void *open_cfw_test_grid_malloc_ptrs[10];
unsigned int open_cfw_test_grid_memcpy_calls;
unsigned int open_cfw_test_grid_invalidate_calls;
unsigned int open_cfw_test_grid_invalidate_obj;
unsigned int open_cfw_test_grid_area_set_w_calls;
int open_cfw_test_grid_area_set_w_value;
unsigned int open_cfw_test_grid_area_set_h_calls;
int open_cfw_test_grid_area_set_h_value;
unsigned int open_cfw_test_grid_move_children_calls;
unsigned int open_cfw_test_grid_move_children_obj;
int open_cfw_test_grid_move_children_dx;
int open_cfw_test_grid_move_children_dy;
unsigned int open_cfw_test_grid_move_children_ignore;
unsigned int open_cfw_test_grid_log_calls;
int open_cfw_test_grid_log_level;
int open_cfw_test_grid_log_line;
const char *open_cfw_test_grid_log_file;
const char *open_cfw_test_grid_log_func;
const char *open_cfw_test_grid_log_format;

static unsigned int stub_parent_fn(unsigned int obj)
{
    (void)obj;
    return open_cfw_test_grid_parent_value;
}

static int stub_has_flag_fn(unsigned int obj, unsigned int mask)
{
    (void)obj;
    (void)mask;
    return (int)open_cfw_test_grid_has_flag_value;
}

static unsigned int stub_child_count_fn(unsigned int obj)
{
    (void)obj;
    return open_cfw_test_grid_child_count_value;
}

static void *stub_malloc_fn(unsigned int size)
{
    void *ptr = malloc((size_t)size == 0U ? 1U : (size_t)size);
    if (open_cfw_test_grid_malloc_count < 10U) {
        open_cfw_test_grid_malloc_ptrs[open_cfw_test_grid_malloc_count] = ptr;
    }
    open_cfw_test_grid_malloc_count += 1U;
    return ptr;
}

static void *stub_memcpy_fn(void *dst, const void *src, unsigned int len)
{
    open_cfw_test_grid_memcpy_calls += 1U;
    memcpy(dst, src, (size_t)len);
    return dst;
}

static void stub_invalidate_fn(unsigned int obj)
{
    open_cfw_test_grid_invalidate_calls += 1U;
    open_cfw_test_grid_invalidate_obj = obj;
}

/* Models upstream `lv_area_get_width/height` (x2-x1+1); the port only
 * forwards the pointer, so the stub defines the observed semantic. */
static int stub_area_get_w_fn(const void *area)
{
    const int *a = (const int *)area;
    return a[2] - a[0] + 1;
}

static int stub_area_get_h_fn(const void *area)
{
    const int *a = (const int *)area;
    return a[3] - a[1] + 1;
}

/* Models upstream `lv_area_set_width/height` (x2=x1+w-1). */
static void stub_area_set_w_fn(void *area, int value)
{
    int *a = (int *)area;
    open_cfw_test_grid_area_set_w_calls += 1U;
    open_cfw_test_grid_area_set_w_value = value;
    a[2] = a[0] + value - 1;
}

static void stub_area_set_h_fn(void *area, int value)
{
    int *a = (int *)area;
    open_cfw_test_grid_area_set_h_calls += 1U;
    open_cfw_test_grid_area_set_h_value = value;
    a[3] = a[1] + value - 1;
}

static void stub_move_children_fn(unsigned int obj, int dx, int dy,
    unsigned int ignore)
{
    open_cfw_test_grid_move_children_calls += 1U;
    open_cfw_test_grid_move_children_obj = obj;
    open_cfw_test_grid_move_children_dx = dx;
    open_cfw_test_grid_move_children_dy = dy;
    open_cfw_test_grid_move_children_ignore = ignore;
}

static void stub_log_warn_fn(int level, const char *file, int line,
    const char *func, const char *format)
{
    open_cfw_test_grid_log_calls += 1U;
    open_cfw_test_grid_log_level = level;
    open_cfw_test_grid_log_line = line;
    open_cfw_test_grid_log_file = file;
    open_cfw_test_grid_log_func = func;
    open_cfw_test_grid_log_format = format;
}

const int *open_cfw_test_grid_col_templ_cont;
const int *open_cfw_test_grid_col_templ_parent;
const int *open_cfw_test_grid_row_templ_cont;
const int *open_cfw_test_grid_row_templ_parent;

static const int *test_col_templ_fn(unsigned int obj)
{
    if (obj == open_cfw_test_grid_parent_value) {
        return open_cfw_test_grid_col_templ_parent;
    }
    return open_cfw_test_grid_col_templ_cont;
}

static const int *test_row_templ_fn(unsigned int obj)
{
    if (obj == open_cfw_test_grid_parent_value) {
        return open_cfw_test_grid_row_templ_parent;
    }
    return open_cfw_test_grid_row_templ_cont;
}

void open_cfw_test_grid_reset(void)
{
    unsigned int i;
    open_cfw_test_grid_misses = 0U;
    open_cfw_test_grid_core_calls = 0U;
    open_cfw_test_grid_core_obj = 0U;
    open_cfw_test_grid_core_part = 0U;
    open_cfw_test_grid_core_prop = 0U;
    for (i = 0U; i < 256U; i += 1U) {
        open_cfw_test_grid_prop_value[i] = 0U;
    }
    open_cfw_test_grid_width_calls = 0U;
    open_cfw_test_grid_height_calls = 0U;
    open_cfw_test_grid_scroll_x_calls = 0U;
    open_cfw_test_grid_scroll_y_calls = 0U;
    open_cfw_test_grid_refr_calls = 0U;
    open_cfw_test_grid_refr_obj = 0U;
    open_cfw_test_grid_event_calls = 0U;
    open_cfw_test_grid_event_obj = 0U;
    open_cfw_test_grid_event_code = 0U;
    open_cfw_test_grid_event_param = 0U;
    open_cfw_test_grid_child_calls = 0U;
    open_cfw_test_grid_content_w_calls = 0U;
    open_cfw_test_grid_content_h_calls = 0U;
    open_cfw_test_grid_memset_calls = 0U;
    open_cfw_test_grid_memset_dst = 0;
    open_cfw_test_grid_memset_value = 0U;
    open_cfw_test_grid_memset_len = 0U;
    open_cfw_test_grid_free_count = 0U;
    open_cfw_test_grid_cols_calls = 0U;
    open_cfw_test_grid_rows_calls = 0U;
    open_cfw_test_grid_repos_count = 0U;
    open_cfw_test_grid_align_calls = 0U;
    open_cfw_test_grid_parent_value = 0U;
    open_cfw_test_grid_has_flag_value = 0U;
    open_cfw_test_grid_child_count_value = 0U;
    open_cfw_test_grid_malloc_count = 0U;
    open_cfw_test_grid_memcpy_calls = 0U;
    open_cfw_test_grid_invalidate_calls = 0U;
    open_cfw_test_grid_invalidate_obj = 0U;
    open_cfw_test_grid_area_set_w_calls = 0U;
    open_cfw_test_grid_area_set_w_value = 0;
    open_cfw_test_grid_area_set_h_calls = 0U;
    open_cfw_test_grid_area_set_h_value = 0;
    open_cfw_test_grid_move_children_calls = 0U;
    open_cfw_test_grid_move_children_obj = 0U;
    open_cfw_test_grid_move_children_dx = 0;
    open_cfw_test_grid_move_children_dy = 0;
    open_cfw_test_grid_move_children_ignore = 0U;
    open_cfw_test_grid_log_calls = 0U;
    open_cfw_test_grid_log_level = 0;
    open_cfw_test_grid_log_line = 0;
    open_cfw_test_grid_log_file = 0;
    open_cfw_test_grid_log_func = 0;
    open_cfw_test_grid_log_format = 0;
    open_cfw_test_grid_child_list_len = 0U;
    open_cfw_test_grid_width_list_len = 0U;
    open_cfw_test_grid_height_list_len = 0U;
    open_cfw_test_grid_col_templ_cont = 0;
    open_cfw_test_grid_col_templ_parent = 0;
    open_cfw_test_grid_row_templ_cont = 0;
    open_cfw_test_grid_row_templ_parent = 0;
    for (i = 0U; i < OPEN_CFW_TEST_GRID_MAX_OBJECTS; i += 1U) {
        open_cfw_test_grid_object_ids[i] = 0U;
        open_cfw_test_grid_objects[i] = 0;
    }
}

void open_cfw_test_grid_register(unsigned int id, void *ptr)
{
    unsigned int i;
    for (i = 0U; i < OPEN_CFW_TEST_GRID_MAX_OBJECTS; i += 1U) {
        if (open_cfw_test_grid_objects[i] == 0) {
            open_cfw_test_grid_object_ids[i] = id;
            open_cfw_test_grid_objects[i] = ptr;
            return;
        }
    }
}
