/* SPDX-License-Identifier: MIT */
#include <assert.h>
#include <stdint.h>
#include <string.h>

#include "../../components/apollo_main/core_overlay/production_test_screen.h"

typedef struct {
    void *parent;
    int32_t width;
    int32_t height;
    int32_t x;
    int32_t y;
    uint32_t bg_color;
    uint32_t bg_opacity;
    uint32_t border_color;
    int32_t border_width;
    uint32_t cleared_flags;
} host_production_test_object;

static host_production_test_object g_objects[10];
static uint32_t g_object_count;
static uint32_t g_clear_count;
static void *g_root;
static void *g_registry_root;

void *open_cfw_retained_production_test_object_create(void *parent)
{
    host_production_test_object *object;
    assert(g_object_count < 10U);
    object = &g_objects[g_object_count++];
    object->parent = parent;
    return object;
}

void open_cfw_retained_production_test_clear_flags(
    void *object, uint32_t flags
)
{
    ((host_production_test_object *)object)->cleared_flags |= flags;
    ++g_clear_count;
}

void open_cfw_retained_production_test_set_width(void *object, int32_t width)
{
    ((host_production_test_object *)object)->width = width;
}

void open_cfw_retained_production_test_set_height(void *object, int32_t height)
{
    ((host_production_test_object *)object)->height = height;
}

void open_cfw_retained_production_test_set_size(
    void *object, int32_t width, int32_t height
)
{
    open_cfw_retained_production_test_set_width(object, width);
    open_cfw_retained_production_test_set_height(object, height);
}

void open_cfw_retained_production_test_set_pos(
    void *object, int32_t x, int32_t y
)
{
    host_production_test_object *record = object;
    record->x = x;
    record->y = y;
}

uint32_t open_cfw_retained_production_test_color_hex(uint32_t rgb)
{
    return rgb;
}

uint32_t open_cfw_retained_production_test_color_make(
    uint32_t red, uint32_t green, uint32_t blue
)
{
    return (red << 16) | (green << 8) | blue;
}

void open_cfw_retained_production_test_set_bg_color(
    void *object, uint32_t color, uint32_t selector
)
{
    assert(selector == 0U);
    ((host_production_test_object *)object)->bg_color = color;
}

void open_cfw_retained_production_test_set_bg_opacity(
    void *object, uint32_t opacity, uint32_t selector
)
{
    assert(selector == 0U);
    ((host_production_test_object *)object)->bg_opacity = opacity;
}

void open_cfw_retained_production_test_set_border_color(
    void *object, uint32_t color, uint32_t selector
)
{
    assert(selector == 0U);
    ((host_production_test_object *)object)->border_color = color;
}

void open_cfw_retained_production_test_set_border_width(
    void *object, int32_t width, uint32_t selector
)
{
    assert(selector == 0U);
    ((host_production_test_object *)object)->border_width = width;
}

#define OPEN_CFW_PRODUCTION_TEST_ROOT g_root
#define OPEN_CFW_PRODUCTION_TEST_REGISTRY_ROOT g_registry_root
#include "../../components/apollo_main/core_overlay/production_test_screen.c"

static void reset_fixture(void)
{
    memset(g_objects, 0, sizeof(g_objects));
    g_object_count = 0U;
    g_clear_count = 0U;
    g_root = 0;
    g_registry_root = 0;
}

int main(void)
{
    uint32_t index;
    host_production_test_object parent;

    memset(&parent, 0, sizeof(parent));
    reset_fixture();
    assert(open_cfw_production_test_common_data_handler(0, 0, 7U) == 0);
    assert(open_cfw_production_test_predicate() == 1);
    assert(open_cfw_production_test_screen_event(
        OPEN_CFW_PRODUCTION_TEST_EXIT_EVENT, 0, 0, &parent
    ) == 0);
    assert(g_object_count == 0U);

    assert(open_cfw_production_test_screen_event(
        OPEN_CFW_PRODUCTION_TEST_CONSTRUCT_EVENT, 0, 0, &parent
    ) == 0);
    assert(g_object_count == 10U);
    assert(g_root == &g_objects[0]);
    assert(g_registry_root == g_root);
    assert(g_objects[0].parent == &parent);
    assert(g_objects[0].width == 640);
    assert(g_objects[0].height == 480);
    assert(g_objects[0].bg_color == 0U);
    assert(g_objects[0].bg_opacity == 255U);
    assert(g_objects[0].border_color == 0U);
    assert(g_objects[0].cleared_flags == 0x10U);
    assert(g_clear_count == 2U);

    for (index = 0U; index < 9U; ++index) {
        host_production_test_object *dot = &g_objects[index + 1U];
        assert(dot->parent == g_root);
        assert(dot->width == 10);
        assert(dot->height == 10);
        assert(dot->bg_color == 0x00FFFFFFU);
        assert(dot->border_width == 0);
        assert(dot->x == 66 + 200 * (int32_t)(index % 3U));
        assert(dot->y == 21 + 100 * (int32_t)(index / 3U));
    }
    return 0;
}
