/*
 * SPDX-License-Identifier: MIT
 *
 * Clean-room reconstruction of app/gui/health/ui_health_page.c from the
 * authenticated G2 2.2.6.10 control-flow and data contract.  Diagnostic
 * EasyLogger calls are intentionally omitted; page lifecycle, navigation,
 * deferred input, health-data formatting, LVGL construction, refresh, and
 * teardown remain functional.
 */

#include <stddef.h>
#include <stdint.h>

#define OPEN_CFW_HEALTH_PAGE_COUNT 2u
#define OPEN_CFW_HEALTH_EVENT_CLICK 0x0au
#define OPEN_CFW_HEALTH_EVENT_SCROLL_UP 0x44u
#define OPEN_CFW_HEALTH_EVENT_SCROLL_DOWN 0x45u
#define OPEN_CFW_HEALTH_EVENT_REFRESH 0x47u
#define OPEN_CFW_HEALTH_EVENT_EXIT 0x48u
#define OPEN_CFW_HEALTH_EVENT_MINIMIZE 0x49u
#define OPEN_CFW_HEALTH_PACKET_BYTES 6u
#define OPEN_CFW_HEALTH_ANIMATION_MS 250u
#define OPEN_CFW_HEALTH_COLOR_WHITE 0x00ffffffu
#define OPEN_CFW_HEALTH_COLOR_OFF 0x00444444u
#define OPEN_CFW_HEALTH_COLOR_BLACK 0u
#define OPEN_CFW_HEALTH_LV_SIZE_CONTENT 0x3fffffffu
#define OPEN_CFW_HEALTH_PAGE_WIDTH 0x240
#define OPEN_CFW_HEALTH_PAGE_HEIGHT 0x100

struct open_cfw_health_page_point {
    int32_t x;
    int32_t y;
};

struct open_cfw_health_page_event_context {
    uint8_t reserved[16];
    const struct open_cfw_health_page_point *point;
};

struct open_cfw_health_anim {
    uintptr_t object;
    uintptr_t exec_callback;
    uint32_t reserved_08[2];
    uintptr_t ready_callback;
    uint32_t reserved_14[3];
    uintptr_t path_callback;
    uint32_t reserved_24[3];
    uint32_t duration;
    uint32_t reserved_34[7];
};

#ifndef OPEN_CFW_HEALTH_WIDGET_INITIALIZED
#define OPEN_CFW_HEALTH_WIDGET_INITIALIZED \
    (*(volatile uint32_t *)(uintptr_t)0x20074c0cu)
#endif
#ifndef OPEN_CFW_HEALTH_FIFO
#define OPEN_CFW_HEALTH_FIFO (*(void *volatile *)(uintptr_t)0x20074c10u)
#endif
#ifndef OPEN_CFW_HEALTH_ANIMATING
#define OPEN_CFW_HEALTH_ANIMATING (*(volatile uint32_t *)(uintptr_t)0x20074c14u)
#endif
#ifndef OPEN_CFW_HEALTH_CURRENT_PAGE
#define OPEN_CFW_HEALTH_CURRENT_PAGE (*(volatile uint32_t *)(uintptr_t)0x20074c18u)
#endif
#ifndef OPEN_CFW_HEALTH_EXT_INITIALIZED
#define OPEN_CFW_HEALTH_EXT_INITIALIZED (*(volatile uint32_t *)(uintptr_t)0x20074c1cu)
#endif
#ifndef OPEN_CFW_HEALTH_SELECTED_PAGE
#define OPEN_CFW_HEALTH_SELECTED_PAGE (*(volatile uint32_t *)(uintptr_t)0x20074c20u)
#endif
#ifndef OPEN_CFW_HEALTH_SUMMARY_ROOT
#define OPEN_CFW_HEALTH_SUMMARY_ROOT (*(volatile uintptr_t *)(uintptr_t)0x20074c24u)
#endif
#ifndef OPEN_CFW_HEALTH_SCROLL_CONTAINER
#define OPEN_CFW_HEALTH_SCROLL_CONTAINER (*(volatile uintptr_t *)(uintptr_t)0x20074c6cu)
#endif
#ifndef OPEN_CFW_HEALTH_PAGE_ROOTS
#define OPEN_CFW_HEALTH_PAGE_ROOTS ((volatile uintptr_t *)(uintptr_t)0x20074190u)
#endif
#ifndef OPEN_CFW_HEALTH_INDICATORS
#define OPEN_CFW_HEALTH_INDICATORS ((volatile uintptr_t *)(uintptr_t)0x20074198u)
#endif
#ifndef OPEN_CFW_HEALTH_PAGE_DESCRIPTORS
#define OPEN_CFW_HEALTH_PAGE_DESCRIPTORS ((volatile uintptr_t *)(uintptr_t)0x200734bcu)
#endif
#ifndef OPEN_CFW_HEALTH_WIDGET_HANDLES
#define OPEN_CFW_HEALTH_WIDGET_HANDLES ((volatile uintptr_t *)(uintptr_t)0x20074c28u)
#endif
#ifndef OPEN_CFW_HEALTH_DATA
#define OPEN_CFW_HEALTH_DATA ((volatile uint8_t *)(uintptr_t)0x200f41b4u)
#endif
#ifndef OPEN_CFW_HEALTH_FONT
#define OPEN_CFW_HEALTH_FONT (*(const void *volatile *)(uintptr_t)0x200746dcu)
#endif

#ifndef OPEN_CFW_HEALTH_MEMSET
void *open_cfw_retained_health_page_memset(void *, int, size_t);
#define OPEN_CFW_HEALTH_MEMSET(p, v, n) \
    open_cfw_retained_health_page_memset((p), (v), (n))
#endif
#ifndef OPEN_CFW_HEALTH_OBJECT_CREATE
uintptr_t open_cfw_retained_health_page_object_create(uintptr_t);
#define OPEN_CFW_HEALTH_OBJECT_CREATE(p) \
    open_cfw_retained_health_page_object_create((p))
#endif
#ifndef OPEN_CFW_HEALTH_SET_SIZE
void open_cfw_retained_health_page_set_size(uintptr_t, int32_t, int32_t);
#define OPEN_CFW_HEALTH_SET_SIZE(...) \
    open_cfw_retained_health_page_set_size(__VA_ARGS__)
#endif
#ifndef OPEN_CFW_HEALTH_SET_WIDTH
void open_cfw_retained_health_page_set_width(uintptr_t, int32_t);
#define OPEN_CFW_HEALTH_SET_WIDTH(...) \
    open_cfw_retained_health_page_set_width(__VA_ARGS__)
#endif
#ifndef OPEN_CFW_HEALTH_SET_HEIGHT
void open_cfw_retained_health_page_set_height(uintptr_t, int32_t);
#define OPEN_CFW_HEALTH_SET_HEIGHT(...) \
    open_cfw_retained_health_page_set_height(__VA_ARGS__)
#endif
#ifndef OPEN_CFW_HEALTH_SET_POS
void open_cfw_retained_health_page_set_pos(uintptr_t, int32_t, int32_t);
#define OPEN_CFW_HEALTH_SET_POS(...) \
    open_cfw_retained_health_page_set_pos(__VA_ARGS__)
#endif
#ifndef OPEN_CFW_HEALTH_SET_X
void open_cfw_retained_health_page_set_x(uintptr_t, int32_t);
#define OPEN_CFW_HEALTH_SET_X(...) open_cfw_retained_health_page_set_x(__VA_ARGS__)
#endif
#ifndef OPEN_CFW_HEALTH_GET_X
int32_t open_cfw_retained_health_page_get_x(uintptr_t);
#define OPEN_CFW_HEALTH_GET_X(o) open_cfw_retained_health_page_get_x((o))
#endif
#ifndef OPEN_CFW_HEALTH_ALIGN
void open_cfw_retained_health_page_align(uintptr_t, uint32_t, int32_t, int32_t);
#define OPEN_CFW_HEALTH_ALIGN(...) open_cfw_retained_health_page_align(__VA_ARGS__)
#endif
#ifndef OPEN_CFW_HEALTH_ALIGN_TO
void open_cfw_retained_health_page_align_to(
    uintptr_t, uintptr_t, uint32_t, int32_t, int32_t);
#define OPEN_CFW_HEALTH_ALIGN_TO(...) \
    open_cfw_retained_health_page_align_to(__VA_ARGS__)
#endif
#ifndef OPEN_CFW_HEALTH_ADD_FLAGS
void open_cfw_retained_health_page_add_flags(uintptr_t, uint32_t);
#define OPEN_CFW_HEALTH_ADD_FLAGS(...) \
    open_cfw_retained_health_page_add_flags(__VA_ARGS__)
#endif
#ifndef OPEN_CFW_HEALTH_CLEAR_FLAGS
void open_cfw_retained_health_page_clear_flags(uintptr_t, uint32_t);
#define OPEN_CFW_HEALTH_CLEAR_FLAGS(...) \
    open_cfw_retained_health_page_clear_flags(__VA_ARGS__)
#endif
#ifndef OPEN_CFW_HEALTH_SET_LAYOUT
void open_cfw_retained_health_page_set_layout(uintptr_t, uint32_t);
#define OPEN_CFW_HEALTH_SET_LAYOUT(...) \
    open_cfw_retained_health_page_set_layout(__VA_ARGS__)
#endif
#ifndef OPEN_CFW_HEALTH_SET_SCROLLBAR
void open_cfw_retained_health_page_set_scrollbar(uintptr_t, uint32_t);
#define OPEN_CFW_HEALTH_SET_SCROLLBAR(...) \
    open_cfw_retained_health_page_set_scrollbar(__VA_ARGS__)
#endif
#ifndef OPEN_CFW_HEALTH_COLOR
uint32_t open_cfw_retained_health_page_color(uint32_t);
#define OPEN_CFW_HEALTH_COLOR(v) open_cfw_retained_health_page_color((v))
#endif
#ifndef OPEN_CFW_HEALTH_SET_BG_COLOR
void open_cfw_retained_health_page_set_bg_color(uintptr_t, uint32_t, uint32_t);
#define OPEN_CFW_HEALTH_SET_BG_COLOR(...) \
    open_cfw_retained_health_page_set_bg_color(__VA_ARGS__)
#endif
#ifndef OPEN_CFW_HEALTH_SET_BG_OPACITY
void open_cfw_retained_health_page_set_bg_opacity(uintptr_t, uint32_t, uint32_t);
#define OPEN_CFW_HEALTH_SET_BG_OPACITY(...) \
    open_cfw_retained_health_page_set_bg_opacity(__VA_ARGS__)
#endif
#ifndef OPEN_CFW_HEALTH_SET_TEXT_COLOR
void open_cfw_retained_health_page_set_text_color(uintptr_t, uint32_t, uint32_t);
#define OPEN_CFW_HEALTH_SET_TEXT_COLOR(...) \
    open_cfw_retained_health_page_set_text_color(__VA_ARGS__)
#endif
#ifndef OPEN_CFW_HEALTH_SET_TEXT_ALIGN
void open_cfw_retained_health_page_set_text_align(uintptr_t, uint32_t, uint32_t);
#define OPEN_CFW_HEALTH_SET_TEXT_ALIGN(...) \
    open_cfw_retained_health_page_set_text_align(__VA_ARGS__)
#endif
#ifndef OPEN_CFW_HEALTH_SET_FONT
void open_cfw_retained_health_page_set_font(uintptr_t, const void *, uint32_t);
#define OPEN_CFW_HEALTH_SET_FONT(...) \
    open_cfw_retained_health_page_set_font(__VA_ARGS__)
#endif
#ifndef OPEN_CFW_HEALTH_DELETE_CHILDREN
void open_cfw_retained_health_page_delete_children(uintptr_t);
#define OPEN_CFW_HEALTH_DELETE_CHILDREN(o) \
    open_cfw_retained_health_page_delete_children((o))
#endif
#ifndef OPEN_CFW_HEALTH_IMAGE_CREATE
uintptr_t open_cfw_retained_health_page_image_create(uintptr_t);
#define OPEN_CFW_HEALTH_IMAGE_CREATE(p) \
    open_cfw_retained_health_page_image_create((p))
#endif
#ifndef OPEN_CFW_HEALTH_IMAGE_SET_SOURCE
void open_cfw_retained_health_page_image_set_source(uintptr_t, const void *);
#define OPEN_CFW_HEALTH_IMAGE_SET_SOURCE(...) \
    open_cfw_retained_health_page_image_set_source(__VA_ARGS__)
#endif
#ifndef OPEN_CFW_HEALTH_LABEL_CREATE
uintptr_t open_cfw_retained_health_page_label_create(uintptr_t);
#define OPEN_CFW_HEALTH_LABEL_CREATE(p) \
    open_cfw_retained_health_page_label_create((p))
#endif
#ifndef OPEN_CFW_HEALTH_LABEL_SET_TEXT
void open_cfw_retained_health_page_label_set_text(uintptr_t, const char *);
#define OPEN_CFW_HEALTH_LABEL_SET_TEXT(...) \
    open_cfw_retained_health_page_label_set_text(__VA_ARGS__)
#endif
#ifndef OPEN_CFW_HEALTH_TRANSLATION_ID
uint32_t open_cfw_retained_health_page_translation_id(const char *);
#define OPEN_CFW_HEALTH_TRANSLATION_ID(s) \
    open_cfw_retained_health_page_translation_id((s))
#endif
#ifndef OPEN_CFW_HEALTH_TRANSLATION
const char *open_cfw_retained_health_page_translation(const char *, uint32_t);
#define OPEN_CFW_HEALTH_TRANSLATION(s, id) \
    open_cfw_retained_health_page_translation((s), (id))
#endif
#ifndef OPEN_CFW_HEALTH_FORMAT
int open_cfw_retained_health_page_format(char *, const char *, ...);
#define OPEN_CFW_HEALTH_FORMAT(...) \
    open_cfw_retained_health_page_format(__VA_ARGS__)
#endif
#ifndef OPEN_CFW_HEALTH_FIFO_CREATE
void *open_cfw_retained_health_page_fifo_create(void);
#define OPEN_CFW_HEALTH_FIFO_CREATE() open_cfw_retained_health_page_fifo_create()
#endif
#ifndef OPEN_CFW_HEALTH_FIFO_DELETE
void open_cfw_retained_health_page_fifo_delete(void *);
#define OPEN_CFW_HEALTH_FIFO_DELETE(f) open_cfw_retained_health_page_fifo_delete((f))
#endif
#ifndef OPEN_CFW_HEALTH_FIFO_EMPTY
uint32_t open_cfw_retained_health_page_fifo_empty(void *);
#define OPEN_CFW_HEALTH_FIFO_EMPTY(f) open_cfw_retained_health_page_fifo_empty((f))
#endif
#ifndef OPEN_CFW_HEALTH_FIFO_PUSH
int32_t open_cfw_retained_health_page_fifo_push(void *, const void *, uint32_t);
#define OPEN_CFW_HEALTH_FIFO_PUSH(...) \
    open_cfw_retained_health_page_fifo_push(__VA_ARGS__)
#endif
#ifndef OPEN_CFW_HEALTH_FIFO_POP
int32_t open_cfw_retained_health_page_fifo_pop(void *, void *, uint32_t);
#define OPEN_CFW_HEALTH_FIFO_POP(...) \
    open_cfw_retained_health_page_fifo_pop(__VA_ARGS__)
#endif
#ifndef OPEN_CFW_HEALTH_ANIM_INIT
void open_cfw_retained_health_page_anim_init(void *);
#define OPEN_CFW_HEALTH_ANIM_INIT(a) open_cfw_retained_health_page_anim_init((a))
#endif
#ifndef OPEN_CFW_HEALTH_ANIM_SET_VALUES
void open_cfw_retained_health_page_anim_set_values(void *, int32_t, int32_t);
#define OPEN_CFW_HEALTH_ANIM_SET_VALUES(...) \
    open_cfw_retained_health_page_anim_set_values(__VA_ARGS__)
#endif
#ifndef OPEN_CFW_HEALTH_ANIM_START
void open_cfw_retained_health_page_anim_start(void *);
#define OPEN_CFW_HEALTH_ANIM_START(a) open_cfw_retained_health_page_anim_start((a))
#endif
#ifndef OPEN_CFW_HEALTH_NOTIFY_PAGE
uint32_t open_cfw_retained_health_page_notify_page(uint32_t);
#define OPEN_CFW_HEALTH_NOTIFY_PAGE(v) \
    open_cfw_retained_health_page_notify_page((v))
#endif
#ifndef OPEN_CFW_HEALTH_SEND_PAGE_ACTION
uint32_t open_cfw_retained_health_page_send_action(
    uint32_t, const void *, uint32_t, uint32_t);
#define OPEN_CFW_HEALTH_SEND_PAGE_ACTION(...) \
    open_cfw_retained_health_page_send_action(__VA_ARGS__)
#endif
#ifndef OPEN_CFW_HEALTH_POST_EXIT
void open_cfw_retained_health_page_post_exit(void);
#define OPEN_CFW_HEALTH_POST_EXIT() open_cfw_retained_health_page_post_exit()
#endif
#ifndef OPEN_CFW_HEALTH_POST_EVENT
uint32_t open_cfw_retained_health_page_post_event(
    uint32_t, const void *, uint32_t, uint32_t);
#define OPEN_CFW_HEALTH_POST_EVENT(...) \
    open_cfw_retained_health_page_post_event(__VA_ARGS__)
#endif
#ifndef OPEN_CFW_HEALTH_MINIMIZE
void open_cfw_retained_health_page_minimize(void);
#define OPEN_CFW_HEALTH_MINIMIZE() open_cfw_retained_health_page_minimize()
#endif
#ifndef OPEN_CFW_HEALTH_COMMON_DATA
void open_cfw_retained_health_page_common_data(const uint8_t *, uint32_t);
#define OPEN_CFW_HEALTH_COMMON_DATA(...) \
    open_cfw_retained_health_page_common_data(__VA_ARGS__)
#endif
#ifndef OPEN_CFW_HEALTH_LOCK
uint32_t open_cfw_health_lock_storage(void);
#define OPEN_CFW_HEALTH_LOCK() open_cfw_health_lock_storage()
#endif
#ifndef OPEN_CFW_HEALTH_UNLOCK
void open_cfw_health_unlock_storage(void);
#define OPEN_CFW_HEALTH_UNLOCK() open_cfw_health_unlock_storage()
#endif

#define OPEN_CFW_HEALTH_ASSET_SCORE ((const void *)(uintptr_t)0x007747acu)
#define OPEN_CFW_HEALTH_ASSET_STEPS ((const void *)(uintptr_t)0x0076bd34u)
#define OPEN_CFW_HEALTH_ASSET_CALORIES ((const void *)(uintptr_t)0x00769facu)
#define OPEN_CFW_HEALTH_ASSET_ACTIVE ((const void *)(uintptr_t)0x00771dc8u)
#define OPEN_CFW_HEALTH_ASSET_HEART ((const void *)(uintptr_t)0x0076bddcu)
#define OPEN_CFW_HEALTH_ASSET_PERCENT ((const void *)(uintptr_t)0x00771e54u)

/* The isolated production leaf uses placement-pinned Thumb callbacks.  The
 * all-functions/host build keeps ordinary C function pointers so its behavior
 * remains directly executable under the host harness. */
#if defined(OPEN_CFW_HEALTH_PAGE_ANIMATE_ONLY)
#define OPEN_CFW_HEALTH_ANIM_EXEC_CALLBACK ((uintptr_t)0x00487d01u)
#define OPEN_CFW_HEALTH_ANIM_READY_CALLBACK ((uintptr_t)0x00487c5du)
#else
#define OPEN_CFW_HEALTH_ANIM_EXEC_CALLBACK \
    ((uintptr_t)&open_cfw_health_page_anim_exec)
#define OPEN_CFW_HEALTH_ANIM_READY_CALLBACK \
    ((uintptr_t)&open_cfw_health_page_widget_event)
#endif

void open_cfw_health_page_update_indicator(uint32_t);
uint32_t open_cfw_health_page_switch(uint32_t);
int32_t open_cfw_health_page_widget_event(void);
void open_cfw_health_page_anim_exec(uintptr_t, int32_t);
void open_cfw_health_page_animate(uintptr_t, int32_t, uint32_t);
uint32_t open_cfw_health_page_reflash(void);
void open_cfw_health_page_build_summary(uint32_t);
uint32_t open_cfw_health_page_input_event(uint32_t, const void *);
uint32_t open_cfw_health_page_external_event(const uint8_t *, uint32_t);
void open_cfw_health_page_build_detail(uintptr_t);
int32_t open_cfw_health_page_init(uintptr_t);
uint32_t open_cfw_health_page_deinit(void);

static __attribute__((unused)) uint32_t open_cfw_health_u32(uint32_t offset)
{
    const volatile uint32_t *value =
        (const volatile uint32_t *)(const volatile void *)(OPEN_CFW_HEALTH_DATA + offset);
    return *value;
}

static __attribute__((unused)) float open_cfw_health_float(uint32_t offset)
{
    const volatile float *value =
        (const volatile float *)(const volatile void *)(OPEN_CFW_HEALTH_DATA + offset);
    return *value;
}

static __attribute__((unused)) uint32_t open_cfw_health_round_nonnegative(float value)
{
    if (!(value > 0.0f)) {
        return 0u;
    }
    if (value >= 4294967040.0f) {
        return UINT32_MAX;
    }
    return (uint32_t)value;
}

static __attribute__((unused)) uint32_t open_cfw_health_progress(
    float value,
    uint32_t goal,
    uint32_t width
)
{
    float ratio;
    uint32_t result;

    if (!(value > 0.0f) || goal == 0u) {
        return 0u;
    }
    ratio = value >= (float)goal ? 1.0f : value / (float)goal;
    result = (uint32_t)(ratio * (float)width + 1.0f);
    result = (result / 3u) * 3u;
    return result > width ? width : result;
}

static __attribute__((unused)) const char *open_cfw_health_tr(const char *id)
{
    return OPEN_CFW_HEALTH_TRANSLATION(id, OPEN_CFW_HEALTH_TRANSLATION_ID(id));
}

static __attribute__((unused, always_inline)) inline uintptr_t open_cfw_health_make_label(
    uintptr_t parent,
    const char *text,
    int32_t width,
    uint32_t align,
    int32_t x,
    int32_t y
)
{
    uintptr_t label = OPEN_CFW_HEALTH_LABEL_CREATE(parent);
    if (label == 0u) {
        return 0u;
    }
    OPEN_CFW_HEALTH_SET_WIDTH(label, width);
    OPEN_CFW_HEALTH_SET_HEIGHT(label, OPEN_CFW_HEALTH_LV_SIZE_CONTENT);
    OPEN_CFW_HEALTH_ALIGN(label, align, x, y);
    OPEN_CFW_HEALTH_LABEL_SET_TEXT(label, text);
    OPEN_CFW_HEALTH_SET_TEXT_COLOR(
        label,
        OPEN_CFW_HEALTH_COLOR(OPEN_CFW_HEALTH_COLOR_WHITE),
        0u
    );
    OPEN_CFW_HEALTH_SET_FONT(label, OPEN_CFW_HEALTH_FONT, 0u);
    return label;
}

static __attribute__((unused, always_inline)) inline uintptr_t open_cfw_health_make_metric(
    uintptr_t parent,
    const void *asset,
    const char *text,
    int32_t y,
    uint32_t slot
)
{
    uintptr_t image = OPEN_CFW_HEALTH_IMAGE_CREATE(parent);
    uintptr_t label;

    if (image != 0u) {
        OPEN_CFW_HEALTH_IMAGE_SET_SOURCE(image, asset);
        OPEN_CFW_HEALTH_SET_SIZE(image, 24, 24);
        OPEN_CFW_HEALTH_ALIGN(image, 0x13u, 8, y);
    }
    label = open_cfw_health_make_label(parent, text, 0x1f8, 0x13u, 40, y);
    OPEN_CFW_HEALTH_WIDGET_HANDLES[slot * 2u] = image;
    OPEN_CFW_HEALTH_WIDGET_HANDLES[slot * 2u + 1u] = label;
    return label;
}

static __attribute__((unused)) void open_cfw_health_format_summary(
    char *buffer,
    size_t size,
    uint32_t page
)
{
    uint32_t score;
    uint32_t steps;
    uint32_t calories;
    uint32_t bpm;

    (void)size;
    (void)OPEN_CFW_HEALTH_LOCK();
    score = open_cfw_health_round_nonnegative(open_cfw_health_float(0xb4u));
    steps = open_cfw_health_round_nonnegative(open_cfw_health_float(0x0cu));
    calories = open_cfw_health_round_nonnegative(open_cfw_health_float(0x24u));
    bpm = open_cfw_health_round_nonnegative(open_cfw_health_float(0x54u));
    OPEN_CFW_HEALTH_UNLOCK();

    if (page == 0u) {
        (void)OPEN_CFW_HEALTH_FORMAT(
            buffer,
            "%s %d  %s %d",
            open_cfw_health_tr("ID_DASHBOARD_HEALTH_PRODUCTIVITY_SCORE"),
            score,
            open_cfw_health_tr("ID_DASHBOARD_HEALTH_STEPS"),
            steps
        );
    } else {
        (void)OPEN_CFW_HEALTH_FORMAT(
            buffer,
            "%s %d  %s %d",
            open_cfw_health_tr("ID_DASHBOARD_HEALTH_CALORIES"),
            calories,
            open_cfw_health_tr("ID_DASHBOARD_HEALTH_BPM"),
            bpm
        );
    }
}

#if !defined(OPEN_CFW_HEALTH_PAGE_INDICATOR_ONLY) && \
    !defined(OPEN_CFW_HEALTH_PAGE_SWITCH_ONLY) && \
    !defined(OPEN_CFW_HEALTH_PAGE_WIDGET_EVENT_ONLY) && \
    !defined(OPEN_CFW_HEALTH_PAGE_ANIM_EXEC_ONLY) && \
    !defined(OPEN_CFW_HEALTH_PAGE_ANIMATE_ONLY) && \
    !defined(OPEN_CFW_HEALTH_PAGE_REFLASH_ONLY) && \
    !defined(OPEN_CFW_HEALTH_PAGE_SUMMARY_ONLY) && \
    !defined(OPEN_CFW_HEALTH_PAGE_INPUT_ONLY) && \
    !defined(OPEN_CFW_HEALTH_PAGE_EXTERNAL_ONLY) && \
    !defined(OPEN_CFW_HEALTH_PAGE_DETAIL_ONLY) && \
    !defined(OPEN_CFW_HEALTH_PAGE_INIT_ONLY) && \
    !defined(OPEN_CFW_HEALTH_PAGE_DEINIT_ONLY)
#define OPEN_CFW_HEALTH_PAGE_BUILD_ALL 1
#endif

#if defined(OPEN_CFW_HEALTH_PAGE_BUILD_ALL) || \
    defined(OPEN_CFW_HEALTH_PAGE_INDICATOR_ONLY)
__attribute__((used, noinline))
void open_cfw_health_page_update_indicator(uint32_t page)
{
    uint32_t index;

    if (page >= OPEN_CFW_HEALTH_PAGE_COUNT) {
        return;
    }
    for (index = 0u; index < OPEN_CFW_HEALTH_PAGE_COUNT; ++index) {
        uintptr_t indicator = OPEN_CFW_HEALTH_INDICATORS[index];
        if (indicator != 0u) {
            OPEN_CFW_HEALTH_SET_BG_COLOR(
                indicator,
                OPEN_CFW_HEALTH_COLOR(
                    index == page ? OPEN_CFW_HEALTH_COLOR_WHITE :
                                    OPEN_CFW_HEALTH_COLOR_OFF
                ),
                0u
            );
        }
    }
}
#endif

#if defined(OPEN_CFW_HEALTH_PAGE_BUILD_ALL) || \
    defined(OPEN_CFW_HEALTH_PAGE_SWITCH_ONLY)
__attribute__((used, noinline))
uint32_t open_cfw_health_page_switch(uint32_t page)
{
    if (
        OPEN_CFW_HEALTH_SCROLL_CONTAINER == 0u ||
        page >= OPEN_CFW_HEALTH_PAGE_COUNT ||
        OPEN_CFW_HEALTH_ANIMATING != 0u
    ) {
        return 0u;
    }
    if (page == OPEN_CFW_HEALTH_SELECTED_PAGE) {
        return 0u;
    }

    OPEN_CFW_HEALTH_SELECTED_PAGE = page;
    open_cfw_health_page_update_indicator(page);
    (void)OPEN_CFW_HEALTH_NOTIFY_PAGE(page + 1u);
    open_cfw_health_page_animate(
        OPEN_CFW_HEALTH_SCROLL_CONTAINER,
        (int32_t)(page << 8),
        OPEN_CFW_HEALTH_ANIMATION_MS
    );
    return 1u;
}
#endif

#if defined(OPEN_CFW_HEALTH_PAGE_BUILD_ALL) || \
    defined(OPEN_CFW_HEALTH_PAGE_WIDGET_EVENT_ONLY)
__attribute__((used, noinline))
int32_t open_cfw_health_page_widget_event(void)
{
    uint8_t event[5];

    OPEN_CFW_HEALTH_ANIMATING = 0u;
    if (
        OPEN_CFW_HEALTH_FIFO == NULL ||
        OPEN_CFW_HEALTH_FIFO_EMPTY(OPEN_CFW_HEALTH_FIFO) != 0u ||
        OPEN_CFW_HEALTH_FIFO_POP(
            OPEN_CFW_HEALTH_FIFO,
            event,
            (uint32_t)sizeof(event)
        ) != 0
    ) {
        return 0;
    }

    if (event[0] == OPEN_CFW_HEALTH_EVENT_CLICK ||
        event[0] == OPEN_CFW_HEALTH_EVENT_EXIT) {
        OPEN_CFW_HEALTH_POST_EXIT();
        (void)OPEN_CFW_HEALTH_POST_EVENT(5u, event, 5u, 0u);
    } else if (event[0] == OPEN_CFW_HEALTH_EVENT_SCROLL_UP) {
        if (OPEN_CFW_HEALTH_SELECTED_PAGE + 1u < OPEN_CFW_HEALTH_PAGE_COUNT) {
            (void)open_cfw_health_page_switch(OPEN_CFW_HEALTH_SELECTED_PAGE + 1u);
        }
    } else if (event[0] == OPEN_CFW_HEALTH_EVENT_SCROLL_DOWN) {
        if (OPEN_CFW_HEALTH_SELECTED_PAGE > 0u) {
            (void)open_cfw_health_page_switch(OPEN_CFW_HEALTH_SELECTED_PAGE - 1u);
        }
    } else if (event[0] == OPEN_CFW_HEALTH_EVENT_REFRESH) {
        (void)open_cfw_health_page_reflash();
    } else if (event[0] == OPEN_CFW_HEALTH_EVENT_MINIMIZE) {
        OPEN_CFW_HEALTH_MINIMIZE();
        OPEN_CFW_HEALTH_EXT_INITIALIZED = 0u;
        OPEN_CFW_HEALTH_ANIMATING = 0u;
    }
    return 0;
}
#endif

#if defined(OPEN_CFW_HEALTH_PAGE_BUILD_ALL) || \
    defined(OPEN_CFW_HEALTH_PAGE_ANIM_EXEC_ONLY)
__attribute__((used, noinline))
void open_cfw_health_page_anim_exec(uintptr_t object, int32_t value)
{
    if (object != 0u) {
        OPEN_CFW_HEALTH_SET_X(object, value);
    }
}
#endif

#if defined(OPEN_CFW_HEALTH_PAGE_BUILD_ALL) || \
    defined(OPEN_CFW_HEALTH_PAGE_ANIMATE_ONLY)
__attribute__((used, noinline))
void open_cfw_health_page_animate(
    uintptr_t object,
    int32_t target,
    uint32_t duration
)
{
    struct open_cfw_health_anim animation;
    int32_t current;

    if (object == 0u) {
        return;
    }
    current = OPEN_CFW_HEALTH_GET_X(object);
    if (current == target || duration == 0u) {
        OPEN_CFW_HEALTH_SET_X(object, target);
        OPEN_CFW_HEALTH_ANIMATING = 0u;
        (void)open_cfw_health_page_widget_event();
        return;
    }

    OPEN_CFW_HEALTH_MEMSET(&animation, 0, sizeof(animation));
    OPEN_CFW_HEALTH_ANIM_INIT(&animation);
    animation.object = object;
    animation.exec_callback = OPEN_CFW_HEALTH_ANIM_EXEC_CALLBACK;
    animation.ready_callback = OPEN_CFW_HEALTH_ANIM_READY_CALLBACK;
    animation.path_callback = (uintptr_t)0x00450673u;
    animation.duration = duration;
    OPEN_CFW_HEALTH_ANIMATING = 1u;
    OPEN_CFW_HEALTH_ANIM_SET_VALUES(&animation, current, target);
    OPEN_CFW_HEALTH_ANIM_START(&animation);
}
#endif

#if defined(OPEN_CFW_HEALTH_PAGE_BUILD_ALL) || \
    defined(OPEN_CFW_HEALTH_PAGE_REFLASH_ONLY)
__attribute__((used, noinline))
uint32_t open_cfw_health_page_reflash(void)
{
    uintptr_t page_root;
    uint8_t refresh[5];

    OPEN_CFW_HEALTH_MEMSET(refresh, 0, sizeof(refresh));
    refresh[0] = OPEN_CFW_HEALTH_EVENT_REFRESH;

    if (OPEN_CFW_HEALTH_WIDGET_INITIALIZED == 0u) {
        return 0u;
    }
    page_root = OPEN_CFW_HEALTH_PAGE_DESCRIPTORS[
        OPEN_CFW_HEALTH_CURRENT_PAGE * 2u + 1u
    ];
    if (page_root != 0u) {
        OPEN_CFW_HEALTH_DELETE_CHILDREN(page_root);
    }
    open_cfw_health_page_build_summary(OPEN_CFW_HEALTH_CURRENT_PAGE);

    if (
        OPEN_CFW_HEALTH_EXT_INITIALIZED != 0u &&
        OPEN_CFW_HEALTH_FIFO != NULL &&
        OPEN_CFW_HEALTH_SCROLL_CONTAINER != 0u
    ) {
        if (OPEN_CFW_HEALTH_ANIMATING == 0u) {
            OPEN_CFW_HEALTH_DELETE_CHILDREN(OPEN_CFW_HEALTH_SCROLL_CONTAINER);
            open_cfw_health_page_build_detail(OPEN_CFW_HEALTH_SCROLL_CONTAINER);
        } else {
            (void)OPEN_CFW_HEALTH_FIFO_PUSH(
                OPEN_CFW_HEALTH_FIFO,
                refresh,
                (uint32_t)sizeof(refresh)
            );
        }
    }
    return 0u;
}
#endif

#if defined(OPEN_CFW_HEALTH_PAGE_BUILD_ALL) || \
    defined(OPEN_CFW_HEALTH_PAGE_SUMMARY_ONLY)
__attribute__((used, noinline))
void open_cfw_health_page_build_summary(uint32_t page)
{
    uintptr_t parent;
    uintptr_t root;
    char text[64];

    if (page >= OPEN_CFW_HEALTH_PAGE_COUNT) {
        return;
    }
    OPEN_CFW_HEALTH_WIDGET_INITIALIZED = 1u;
    OPEN_CFW_HEALTH_CURRENT_PAGE = page;
    parent = OPEN_CFW_HEALTH_PAGE_DESCRIPTORS[page * 2u + 1u];
    if (parent == 0u) {
        return;
    }

    root = OPEN_CFW_HEALTH_OBJECT_CREATE(parent);
    OPEN_CFW_HEALTH_SUMMARY_ROOT = root;
    if (root == 0u) {
        return;
    }
    OPEN_CFW_HEALTH_SET_SIZE(root, 0x13b, 0x100);
    OPEN_CFW_HEALTH_SET_POS(root, 20, (int32_t)(page << 8));
    OPEN_CFW_HEALTH_CLEAR_FLAGS(root, 0x10u);
    OPEN_CFW_HEALTH_SET_LAYOUT(root, 0u);
    OPEN_CFW_HEALTH_SET_BG_COLOR(root, OPEN_CFW_HEALTH_COLOR(0u), 0u);

    OPEN_CFW_HEALTH_MEMSET(text, 0, sizeof(text));
    open_cfw_health_format_summary(text, sizeof(text), page);
    (void)open_cfw_health_make_label(root, text, 0x13b, 9u, 0, 28);
}
#endif

#if defined(OPEN_CFW_HEALTH_PAGE_BUILD_ALL) || \
    defined(OPEN_CFW_HEALTH_PAGE_INPUT_ONLY)
__attribute__((used, noinline))
uint32_t open_cfw_health_page_input_event(uint32_t event, const void *context)
{
    uint8_t packet[OPEN_CFW_HEALTH_PACKET_BYTES] = {0u, 0u, 0u, 0u, 0u, 0u};

    if (OPEN_CFW_HEALTH_ANIMATING != 0u) {
        return 0u;
    }
    packet[1] = (uint8_t)event;
    if (event == OPEN_CFW_HEALTH_EVENT_SCROLL_UP ||
        event == OPEN_CFW_HEALTH_EVENT_SCROLL_DOWN) {
        const struct open_cfw_health_page_event_context *value =
            (const struct open_cfw_health_page_event_context *)context;
        if (value != NULL && value->point != NULL) {
            packet[2] = (uint8_t)value->point->x;
            packet[3] = (uint8_t)((uint32_t)value->point->x >> 8);
            packet[4] = (uint8_t)value->point->y;
            packet[5] = (uint8_t)((uint32_t)value->point->y >> 8);
        }
    }
    if (
        event == OPEN_CFW_HEALTH_EVENT_CLICK ||
        event == OPEN_CFW_HEALTH_EVENT_SCROLL_UP ||
        event == OPEN_CFW_HEALTH_EVENT_SCROLL_DOWN ||
        event == OPEN_CFW_HEALTH_EVENT_EXIT ||
        event == OPEN_CFW_HEALTH_EVENT_MINIMIZE
    ) {
        return OPEN_CFW_HEALTH_SEND_PAGE_ACTION(1u, packet, sizeof(packet), 0u);
    }
    return 0u;
}
#endif

#if defined(OPEN_CFW_HEALTH_PAGE_BUILD_ALL) || \
    defined(OPEN_CFW_HEALTH_PAGE_EXTERNAL_ONLY)
__attribute__((used, noinline))
uint32_t open_cfw_health_page_external_event(const uint8_t *data, uint32_t length)
{
    uint8_t event;

    if (
        OPEN_CFW_HEALTH_EXT_INITIALIZED == 0u ||
        data == NULL ||
        length == 0u
    ) {
        return 0u;
    }
    if (data[0] == 1u) {
        if (length > 1u) {
            OPEN_CFW_HEALTH_COMMON_DATA(data + 1, length - 1u);
        }
        return 0u;
    }
    if (data[0] == 6u) {
        return open_cfw_health_page_reflash();
    }
    if (data[0] != 0u || length < 2u) {
        return 0u;
    }

    event = data[1];
    if (OPEN_CFW_HEALTH_ANIMATING != 0u) {
        if (OPEN_CFW_HEALTH_FIFO != NULL && length >= 6u) {
            (void)OPEN_CFW_HEALTH_FIFO_PUSH(OPEN_CFW_HEALTH_FIFO, data + 1, 5u);
        }
        return 0u;
    }

    if (event == OPEN_CFW_HEALTH_EVENT_CLICK ||
        event == OPEN_CFW_HEALTH_EVENT_EXIT) {
        OPEN_CFW_HEALTH_POST_EXIT();
        (void)OPEN_CFW_HEALTH_POST_EVENT(5u, data + 1, length - 1u, 0u);
    } else if (event == OPEN_CFW_HEALTH_EVENT_SCROLL_UP) {
        if (OPEN_CFW_HEALTH_SELECTED_PAGE + 1u < OPEN_CFW_HEALTH_PAGE_COUNT) {
            (void)open_cfw_health_page_switch(OPEN_CFW_HEALTH_SELECTED_PAGE + 1u);
        }
    } else if (event == OPEN_CFW_HEALTH_EVENT_SCROLL_DOWN) {
        if (OPEN_CFW_HEALTH_SELECTED_PAGE > 0u) {
            (void)open_cfw_health_page_switch(OPEN_CFW_HEALTH_SELECTED_PAGE - 1u);
        }
    } else if (event == OPEN_CFW_HEALTH_EVENT_REFRESH) {
        (void)open_cfw_health_page_reflash();
    } else if (event == OPEN_CFW_HEALTH_EVENT_MINIMIZE) {
        OPEN_CFW_HEALTH_MINIMIZE();
        OPEN_CFW_HEALTH_EXT_INITIALIZED = 0u;
        OPEN_CFW_HEALTH_ANIMATING = 0u;
    }
    return 0u;
}
#endif

#if defined(OPEN_CFW_HEALTH_PAGE_BUILD_ALL) || \
    defined(OPEN_CFW_HEALTH_PAGE_DETAIL_ONLY)
__attribute__((used, noinline))
void open_cfw_health_page_build_detail(uintptr_t parent)
{
    uintptr_t scroll;
    uintptr_t page;
    uintptr_t indicator_bar;
    uint32_t index;
    uint32_t score;
    uint32_t steps;
    uint32_t calories;
    uint32_t minutes;
    uint32_t bpm;
    uint32_t average;
    uint32_t percent;
    uint32_t steps_goal;
    uint32_t calories_goal;
    char text[64];

    if (parent == 0u) {
        return;
    }
    OPEN_CFW_HEALTH_MEMSET(text, 0, sizeof(text));
    scroll = OPEN_CFW_HEALTH_OBJECT_CREATE(parent);
    OPEN_CFW_HEALTH_SCROLL_CONTAINER = scroll;
    if (scroll == 0u) {
        return;
    }
    OPEN_CFW_HEALTH_SET_SIZE(scroll, OPEN_CFW_HEALTH_PAGE_WIDTH, OPEN_CFW_HEALTH_PAGE_HEIGHT);
    OPEN_CFW_HEALTH_SET_POS(scroll, 0, 0);
    OPEN_CFW_HEALTH_ADD_FLAGS(scroll, 0x10u);
    OPEN_CFW_HEALTH_CLEAR_FLAGS(scroll, 0x10u);
    OPEN_CFW_HEALTH_SET_SCROLLBAR(scroll, 0u);
    OPEN_CFW_HEALTH_SET_BG_COLOR(scroll, OPEN_CFW_HEALTH_COLOR(0u), 0u);
    OPEN_CFW_HEALTH_SET_BG_OPACITY(scroll, 0u, 0u);

    for (index = 0u; index < OPEN_CFW_HEALTH_PAGE_COUNT; ++index) {
        page = OPEN_CFW_HEALTH_OBJECT_CREATE(scroll);
        OPEN_CFW_HEALTH_PAGE_ROOTS[index] = page;
        OPEN_CFW_HEALTH_SET_SIZE(page, 0x218, OPEN_CFW_HEALTH_PAGE_HEIGHT);
        OPEN_CFW_HEALTH_SET_POS(page, 20, (int32_t)(index << 8));
        OPEN_CFW_HEALTH_CLEAR_FLAGS(page, 0x10u);
        OPEN_CFW_HEALTH_SET_BG_COLOR(page, OPEN_CFW_HEALTH_COLOR(0u), 0u);
        OPEN_CFW_HEALTH_SET_BG_OPACITY(page, 0u, 0u);
    }

    (void)OPEN_CFW_HEALTH_LOCK();
    score = open_cfw_health_round_nonnegative(open_cfw_health_float(0xb4u));
    steps = open_cfw_health_round_nonnegative(open_cfw_health_float(0x0cu));
    calories = open_cfw_health_round_nonnegative(open_cfw_health_float(0x24u));
    minutes = open_cfw_health_u32(0x44u) / 60u;
    bpm = open_cfw_health_round_nonnegative(open_cfw_health_float(0x54u));
    average = open_cfw_health_round_nonnegative(open_cfw_health_float(0x58u));
    percent = open_cfw_health_round_nonnegative(open_cfw_health_float(0x6cu));
    steps_goal = open_cfw_health_u32(0x08u);
    calories_goal = open_cfw_health_u32(0x20u);
    OPEN_CFW_HEALTH_UNLOCK();

    (void)OPEN_CFW_HEALTH_FORMAT(
        text,
        score == 0u ? "%s -" : "%s %d",
        open_cfw_health_tr("ID_DASHBOARD_HEALTH_PRODUCTIVITY_SCORE"),
        score
    );
    (void)open_cfw_health_make_metric(
        OPEN_CFW_HEALTH_PAGE_ROOTS[0], OPEN_CFW_HEALTH_ASSET_SCORE, text, 8, 0u);
    (void)OPEN_CFW_HEALTH_FORMAT(
        text,
        steps == 0u ? "%s -" : "%s %d",
        open_cfw_health_tr("ID_DASHBOARD_HEALTH_STEPS"),
        steps
    );
    (void)open_cfw_health_make_metric(
        OPEN_CFW_HEALTH_PAGE_ROOTS[0], OPEN_CFW_HEALTH_ASSET_STEPS, text, 53, 1u);
    (void)OPEN_CFW_HEALTH_FORMAT(
        text,
        calories == 0u ? "%s -" : "%s %d",
        open_cfw_health_tr("ID_DASHBOARD_HEALTH_CALORIES"),
        calories
    );
    (void)open_cfw_health_make_metric(
        OPEN_CFW_HEALTH_PAGE_ROOTS[0], OPEN_CFW_HEALTH_ASSET_CALORIES, text, 115, 2u);
    if (minutes == 0u) {
        (void)OPEN_CFW_HEALTH_FORMAT(
            text, "-%s", open_cfw_health_tr("ID_DASHBOARD_HEALTH_MIN"));
    } else {
        (void)OPEN_CFW_HEALTH_FORMAT(
            text, "%d%s", minutes, open_cfw_health_tr("ID_DASHBOARD_HEALTH_MIN"));
    }
    (void)open_cfw_health_make_metric(
        OPEN_CFW_HEALTH_PAGE_ROOTS[1], OPEN_CFW_HEALTH_ASSET_ACTIVE, text, 8, 3u);
    if (bpm == 0u) {
        (void)OPEN_CFW_HEALTH_FORMAT(
            text, "-%s", open_cfw_health_tr("ID_DASHBOARD_HEALTH_BPM"));
    } else {
        (void)OPEN_CFW_HEALTH_FORMAT(
            text, "%d%s", bpm, open_cfw_health_tr("ID_DASHBOARD_HEALTH_BPM"));
    }
    (void)open_cfw_health_make_metric(
        OPEN_CFW_HEALTH_PAGE_ROOTS[1], OPEN_CFW_HEALTH_ASSET_HEART, text, 80, 4u);
    if (average == 0u) {
        (void)OPEN_CFW_HEALTH_FORMAT(
            text, "%s -", open_cfw_health_tr("ID_DASHBOARD_HEALTH_AVG"));
    } else {
        (void)OPEN_CFW_HEALTH_FORMAT(
            text,
            "%s %d",
            open_cfw_health_tr("ID_DASHBOARD_HEALTH_AVG"),
            average
        );
    }
    (void)open_cfw_health_make_label(
        OPEN_CFW_HEALTH_PAGE_ROOTS[1], text, 0xab, 0x13u, 40, 112);
    (void)OPEN_CFW_HEALTH_FORMAT(
        text,
        percent >= 100u ? "100%%" : "%d%%",
        percent
    );
    (void)open_cfw_health_make_metric(
        OPEN_CFW_HEALTH_PAGE_ROOTS[1], OPEN_CFW_HEALTH_ASSET_PERCENT, text, 178, 5u);

    /* Preserve the stock proportional progress semantics for both goals. */
    OPEN_CFW_HEALTH_WIDGET_HANDLES[12] =
        (uintptr_t)open_cfw_health_progress((float)steps, steps_goal, 0x218u);
    OPEN_CFW_HEALTH_WIDGET_HANDLES[13] =
        (uintptr_t)open_cfw_health_progress((float)calories, calories_goal, 0x218u);

    indicator_bar = OPEN_CFW_HEALTH_OBJECT_CREATE(parent);
    if (indicator_bar != 0u) {
        OPEN_CFW_HEALTH_SET_WIDTH(indicator_bar, OPEN_CFW_HEALTH_LV_SIZE_CONTENT);
        OPEN_CFW_HEALTH_SET_HEIGHT(indicator_bar, OPEN_CFW_HEALTH_LV_SIZE_CONTENT);
        OPEN_CFW_HEALTH_ALIGN(indicator_bar, 8u, -8, 0);
        OPEN_CFW_HEALTH_SET_BG_OPACITY(indicator_bar, 0u, 0u);
        for (index = 0u; index < OPEN_CFW_HEALTH_PAGE_COUNT; ++index) {
            uintptr_t dot = OPEN_CFW_HEALTH_OBJECT_CREATE(indicator_bar);
            OPEN_CFW_HEALTH_INDICATORS[index] = dot;
            OPEN_CFW_HEALTH_SET_SIZE(dot, 4, 4);
            OPEN_CFW_HEALTH_ALIGN(dot, 1u, 0, (int32_t)(index * 8u));
            OPEN_CFW_HEALTH_SET_BG_OPACITY(dot, 0xffu, 0u);
        }
    }
    open_cfw_health_page_update_indicator(OPEN_CFW_HEALTH_SELECTED_PAGE);
    OPEN_CFW_HEALTH_SET_X(scroll, (int32_t)(OPEN_CFW_HEALTH_SELECTED_PAGE << 8));
}
#endif

#if defined(OPEN_CFW_HEALTH_PAGE_BUILD_ALL) || \
    defined(OPEN_CFW_HEALTH_PAGE_INIT_ONLY)
__attribute__((used, noinline))
int32_t open_cfw_health_page_init(uintptr_t parent)
{
    if (OPEN_CFW_HEALTH_FIFO != NULL) {
        OPEN_CFW_HEALTH_FIFO_DELETE(OPEN_CFW_HEALTH_FIFO);
        OPEN_CFW_HEALTH_FIFO = NULL;
    }
    OPEN_CFW_HEALTH_FIFO = OPEN_CFW_HEALTH_FIFO_CREATE();
    if (OPEN_CFW_HEALTH_FIFO == NULL) {
        return -1;
    }
    OPEN_CFW_HEALTH_ANIMATING = 0u;
    OPEN_CFW_HEALTH_SELECTED_PAGE = 0u;
    open_cfw_health_page_build_detail(parent);
    OPEN_CFW_HEALTH_EXT_INITIALIZED = 1u;
    (void)OPEN_CFW_HEALTH_NOTIFY_PAGE(1u);
    return 0;
}
#endif

#if defined(OPEN_CFW_HEALTH_PAGE_BUILD_ALL) || \
    defined(OPEN_CFW_HEALTH_PAGE_DEINIT_ONLY)
__attribute__((used, noinline))
uint32_t open_cfw_health_page_deinit(void)
{
    if (OPEN_CFW_HEALTH_FIFO != NULL) {
        OPEN_CFW_HEALTH_FIFO_DELETE(OPEN_CFW_HEALTH_FIFO);
        OPEN_CFW_HEALTH_FIFO = NULL;
    }
    OPEN_CFW_HEALTH_EXT_INITIALIZED = 0u;
    OPEN_CFW_HEALTH_ANIMATING = 0u;
    OPEN_CFW_HEALTH_SELECTED_PAGE = 0u;
    OPEN_CFW_HEALTH_CURRENT_PAGE = 0u;
    OPEN_CFW_HEALTH_WIDGET_INITIALIZED = 0u;
    OPEN_CFW_HEALTH_SCROLL_CONTAINER = 0u;
    return 0u;
}
#endif
