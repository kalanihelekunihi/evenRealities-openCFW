/* SPDX-License-Identifier: MIT */
#include <assert.h>
#include <stdint.h>
#include <string.h>

#include "../../components/apollo_main/core_overlay/pdt_distortion_test.h"

typedef enum {
    HOST_OBJECT,
    HOST_IMAGE,
    HOST_LABEL
} host_kind;

typedef struct {
    host_kind kind;
    void *parent;
    int32_t width;
    int32_t height;
    int32_t x;
    int32_t y;
    uint32_t bg_color;
    uint32_t bg_opacity;
    uint32_t border_color;
    uint32_t border_opacity;
    int32_t border_width;
    uint32_t cleared_flags;
    uint32_t added_flags;
    uint32_t flex_flow;
    uint32_t flex_align[3];
    uint32_t alignment;
    const void *image_source;
    const char *text;
    const void *font;
    uint32_t text_color;
    uint32_t text_align;
    uint32_t style[4];
    uint32_t style_calls[4];
    uint32_t frame_style[6];
    uint32_t frame_style_calls[6];
    uint32_t layout_gap[2];
    uint32_t layout_gap_calls[2];
} host_pdt_distortion_object;

static host_pdt_distortion_object g_objects[7];
static uint32_t g_object_count;
static void *g_root;
static void *g_registry_root;
static const uint32_t g_font_marker = 0xFACEU;
static const uint32_t g_image_marker = 0x1A6EU;
static const char g_key_1[] = "ID_DASHBOARD_CALENDAR_BLUETOOTH_DISCONNECTED_1";
static const char g_key_2[] = "ID_DASHBOARD_CALENDAR_BLUETOOTH_DISCONNECTED_2";
static char g_text_1[] = "translated-1";
static char g_text_2[] = "translated-2";
static uint32_t g_translation_calls;

static void *host_create(void *parent, host_kind kind)
{
    host_pdt_distortion_object *object;
    assert(g_object_count < 7U);
    object = &g_objects[g_object_count++];
    object->kind = kind;
    object->parent = parent;
    return object;
}

void *open_cfw_retained_pdt_distortion_object_create(void *parent)
{
    return host_create(parent, HOST_OBJECT);
}

void open_cfw_retained_pdt_distortion_clear_flags(void *object, uint32_t flags)
{
    ((host_pdt_distortion_object *)object)->cleared_flags |= flags;
}

void open_cfw_retained_pdt_distortion_add_flags(void *object, uint32_t flags)
{
    ((host_pdt_distortion_object *)object)->added_flags |= flags;
}

void open_cfw_retained_pdt_distortion_set_width(void *object, int32_t width)
{
    ((host_pdt_distortion_object *)object)->width = width;
}

void open_cfw_retained_pdt_distortion_set_height(void *object, int32_t height)
{
    ((host_pdt_distortion_object *)object)->height = height;
}

void open_cfw_retained_pdt_distortion_set_size(
    void *object, int32_t width, int32_t height
)
{
    open_cfw_retained_pdt_distortion_set_width(object, width);
    open_cfw_retained_pdt_distortion_set_height(object, height);
}

void open_cfw_retained_pdt_distortion_set_pos(
    void *object, int32_t x, int32_t y
)
{
    host_pdt_distortion_object *record = object;
    record->x = x;
    record->y = y;
}

void open_cfw_retained_pdt_distortion_align(
    void *object, uint32_t alignment, int32_t x, int32_t y
)
{
    host_pdt_distortion_object *record = object;
    record->alignment = alignment;
    record->x = x;
    record->y = y;
}

uint32_t open_cfw_retained_pdt_distortion_color_hex(uint32_t rgb)
{
    return rgb;
}

#define HOST_COLOR_SETTER(name, field) \
    void name(void *object, uint32_t value, uint32_t selector) \
    { \
        assert(selector == 0U); \
        ((host_pdt_distortion_object *)object)->field = value; \
    }

HOST_COLOR_SETTER(open_cfw_retained_pdt_distortion_set_bg_color, bg_color)
HOST_COLOR_SETTER(open_cfw_retained_pdt_distortion_set_bg_opacity, bg_opacity)
HOST_COLOR_SETTER(open_cfw_retained_pdt_distortion_set_border_color, border_color)
HOST_COLOR_SETTER(open_cfw_retained_pdt_distortion_set_border_opacity, border_opacity)
HOST_COLOR_SETTER(open_cfw_retained_pdt_distortion_set_text_color, text_color)

void open_cfw_retained_pdt_distortion_set_border_width(
    void *object, int32_t width, uint32_t selector
)
{
    assert(selector == 0U);
    ((host_pdt_distortion_object *)object)->border_width = width;
}

void open_cfw_retained_pdt_distortion_set_shadow_color(
    void *object, uint32_t color, uint32_t selector
)
{
    (void)object;
    assert(color == 0xFFFFFFU);
    assert(selector == 0U);
}

void open_cfw_retained_pdt_distortion_set_shadow_opacity(
    void *object, uint32_t opacity, uint32_t selector
)
{
    (void)object;
    assert(opacity == 255U);
    assert(selector == 0U);
}

#define HOST_STYLE_SETTER(number) \
    void open_cfw_retained_pdt_distortion_set_style_##number( \
        void *object, uint32_t value, uint32_t selector \
    ) \
    { \
        assert(selector == 0U); \
        ((host_pdt_distortion_object *)object)->style[number] = value; \
        ++((host_pdt_distortion_object *)object)->style_calls[number]; \
    }

HOST_STYLE_SETTER(0)
HOST_STYLE_SETTER(1)
HOST_STYLE_SETTER(2)
HOST_STYLE_SETTER(3)
void open_cfw_retained_pdt_distortion_set_layout_gap_0(
    void *object, uint32_t value, uint32_t selector
)
{
    assert(selector == 0U);
    ((host_pdt_distortion_object *)object)->layout_gap[0] = value;
    ++((host_pdt_distortion_object *)object)->layout_gap_calls[0];
}

void open_cfw_retained_pdt_distortion_set_layout_gap_1(
    void *object, uint32_t value, uint32_t selector
)
{
    assert(selector == 0U);
    ((host_pdt_distortion_object *)object)->layout_gap[1] = value;
    ++((host_pdt_distortion_object *)object)->layout_gap_calls[1];
}

#define HOST_FRAME_STYLE_SETTER(number) \
    void open_cfw_retained_pdt_distortion_set_frame_style_##number( \
        void *object, uint32_t value, uint32_t selector \
    ) \
    { \
        assert(selector == 0U); \
        ((host_pdt_distortion_object *)object)->frame_style[number] = value; \
        ++((host_pdt_distortion_object *)object)->frame_style_calls[number]; \
    }

HOST_FRAME_STYLE_SETTER(0)
HOST_FRAME_STYLE_SETTER(1)
HOST_FRAME_STYLE_SETTER(2)
HOST_FRAME_STYLE_SETTER(3)
HOST_FRAME_STYLE_SETTER(4)
HOST_FRAME_STYLE_SETTER(5)

void open_cfw_retained_pdt_distortion_set_scrollbar_mode(
    void *object, uint32_t mode
)
{
    (void)object;
    assert(mode == 0U);
}

void open_cfw_retained_pdt_distortion_set_flex_flow(
    void *object, uint32_t flow
)
{
    ((host_pdt_distortion_object *)object)->flex_flow = flow;
}

void open_cfw_retained_pdt_distortion_set_flex_align(
    void *object, uint32_t main_place, uint32_t cross_place,
    uint32_t track_place
)
{
    host_pdt_distortion_object *record = object;
    record->flex_align[0] = main_place;
    record->flex_align[1] = cross_place;
    record->flex_align[2] = track_place;
}

void *open_cfw_retained_pdt_distortion_image_create(void *parent)
{
    return host_create(parent, HOST_IMAGE);
}

void open_cfw_retained_pdt_distortion_image_set_source(
    void *object, const void *source
)
{
    ((host_pdt_distortion_object *)object)->image_source = source;
}

void *open_cfw_retained_pdt_distortion_label_create(void *parent)
{
    return host_create(parent, HOST_LABEL);
}

void open_cfw_retained_pdt_distortion_label_set_text(
    void *object, const char *text
)
{
    ((host_pdt_distortion_object *)object)->text = text;
}

uint32_t open_cfw_retained_pdt_distortion_translation_id(const char *key)
{
    ++g_translation_calls;
    if (key == g_key_1) {
        return 1U;
    }
    assert(key == g_key_2);
    return 2U;
}

const char *open_cfw_retained_pdt_distortion_translation(
    const char *key, uint32_t id
)
{
    if (key == g_key_1) {
        assert(id == 1U);
        return g_text_1;
    }
    assert(key == g_key_2);
    assert(id == 2U);
    return g_text_2;
}

void open_cfw_retained_pdt_distortion_set_font(
    void *object, const void *font, uint32_t selector
)
{
    assert(selector == 0U);
    ((host_pdt_distortion_object *)object)->font = font;
}

void open_cfw_retained_pdt_distortion_set_text_align(
    void *object, uint32_t alignment, uint32_t selector
)
{
    assert(selector == 0U);
    ((host_pdt_distortion_object *)object)->text_align = alignment;
}

#define OPEN_CFW_PDT_DISTORTION_ROOT g_root
#define OPEN_CFW_PDT_DISTORTION_REGISTRY_ROOT g_registry_root
#define OPEN_CFW_PDT_DISTORTION_FONT (&g_font_marker)
#define OPEN_CFW_PDT_DISTORTION_IMAGE (&g_image_marker)
#define OPEN_CFW_PDT_DISTORTION_TEXT_KEY_1 g_key_1
#define OPEN_CFW_PDT_DISTORTION_TEXT_KEY_2 g_key_2
#include "../../components/apollo_main/core_overlay/pdt_distortion_test.c"

static void reset_fixture(void)
{
    memset(g_objects, 0, sizeof(g_objects));
    g_object_count = 0U;
    g_root = 0;
    g_registry_root = 0;
    g_translation_calls = 0U;
}

int main(void)
{
    host_pdt_distortion_object parent;
    host_pdt_distortion_object scratch;
    uint32_t index;

    memset(&parent, 0, sizeof(parent));
    memset(&scratch, 0, sizeof(scratch));
    open_cfw_pdt_distortion_zero_styles(&scratch, 7U, 0U);
    for (index = 0U; index < 4U; ++index) {
        assert(scratch.style[index] == 7U);
    }
    assert(open_cfw_pdt_distortion_common_data_handler(0, 0, 9U) == 0);
    assert(open_cfw_pdt_distortion_predicate() == 1);

    reset_fixture();
    assert(open_cfw_pdt_distortion_screen_event(
        OPEN_CFW_PDT_DISTORTION_EXIT_EVENT, 0, 0, &parent
    ) == 0);
    assert(g_object_count == 0U);
    assert(open_cfw_pdt_distortion_screen_event(99U, 0, 0, &parent) == 0);
    assert(g_object_count == 0U);

    assert(open_cfw_pdt_distortion_screen_event(
        OPEN_CFW_PDT_DISTORTION_CONSTRUCT_EVENT, 0, 0, &parent
    ) == 0);
    assert(g_object_count == 7U);
    assert(g_root == &g_objects[0]);
    assert(g_registry_root == g_root);
    assert(g_objects[0].kind == HOST_OBJECT);
    assert(g_objects[0].parent == &parent);
    assert(g_objects[0].width == 640);
    assert(g_objects[0].height == 480);
    assert(g_objects[0].bg_color == 0U);
    assert(g_objects[0].bg_opacity == 255U);
    assert(g_objects[0].border_width == 0);
    assert(g_objects[0].cleared_flags == 0x10U);
    for (index = 0U; index < 4U; ++index) {
        assert(g_objects[0].style_calls[index] == 1U);
    }

    assert(g_objects[1].parent == g_root);
    assert(g_objects[1].x == 0);
    assert(g_objects[1].y == 50);
    assert(g_objects[1].width == 574);
    assert(g_objects[1].height == 206);
    assert(g_objects[1].bg_opacity == 0U);
    assert(g_objects[1].border_width == 2);
    assert(g_objects[1].border_color == 0xFFFFFFU);
    assert(g_objects[1].border_opacity == 255U);
    for (index = 0U; index < 4U; ++index) {
        assert(g_objects[1].style_calls[index] == 2U);
    }
    for (index = 0U; index < 6U; ++index) {
        assert(g_objects[1].frame_style_calls[index] == 1U);
    }

    assert(g_objects[2].parent == &g_objects[1]);
    assert(g_objects[2].width == 0x3FFFFFFF);
    assert(g_objects[2].height == 0x3FFFFFFF);
    assert(g_objects[2].flex_flow == 1U);
    assert(g_objects[2].flex_align[0] == 2U);
    assert(g_objects[2].layout_gap[0] == 8U);
    assert(g_objects[2].layout_gap_calls[0] == 1U);
    assert(g_objects[2].alignment == 9U);

    assert(g_objects[3].parent == &g_objects[2]);
    assert(g_objects[3].flex_flow == 0U);
    assert(g_objects[3].flex_align[2] == 2U);
    assert(g_objects[3].layout_gap[1] == 8U);
    assert(g_objects[3].layout_gap_calls[1] == 1U);

    assert(g_objects[4].kind == HOST_IMAGE);
    assert(g_objects[4].parent == &g_objects[3]);
    assert(g_objects[4].image_source == &g_image_marker);
    assert(g_objects[4].width == 24);
    assert(g_objects[4].height == 24);
    assert(g_objects[4].added_flags == 0x10000U);
    assert(g_objects[4].cleared_flags == 0x10U);

    assert(g_objects[5].kind == HOST_LABEL);
    assert(g_objects[5].parent == &g_objects[3]);
    assert(g_objects[5].text == g_text_1);
    assert(g_objects[5].font == &g_font_marker);
    assert(g_objects[5].text_color == 0xFFFFFFU);
    assert(g_objects[6].kind == HOST_LABEL);
    assert(g_objects[6].parent == &g_objects[2]);
    assert(g_objects[6].text == g_text_2);
    assert(g_objects[6].font == &g_font_marker);
    assert(g_objects[6].text_align == 2U);
    assert(g_translation_calls == 2U);
    return 0;
}
