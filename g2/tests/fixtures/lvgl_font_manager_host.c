/* Host oracle for the clean-room G2 LVGL font manager. */
#include <stdint.h>
#include <stdlib.h>
#include <string.h>

#define OPEN_CFW_FONT_MANAGER_TEST_HOST 1
#define OPEN_CFW_FONT_MANAGER_BUILD_ALL 1
#include "../../components/apollo_main/core_overlay/lvgl_font_manager.c"

open_cfw_font_config open_cfw_test_font_background_configs[4];
open_cfw_font_config open_cfw_test_font_foreground_configs[4];
open_cfw_font_manager *open_cfw_test_font_background_manager;
open_cfw_font_manager *open_cfw_test_font_foreground_manager;
void *open_cfw_test_font_background_font;
void *open_cfw_test_font_foreground_font;
uint8_t open_cfw_test_font_xip_scratch[0x5000];
open_cfw_xip_font_header open_cfw_test_font_background_header;
open_cfw_xip_font_header open_cfw_test_font_foreground_header;
open_cfw_xip_font_registration open_cfw_test_font_background_xip;
open_cfw_xip_font_registration open_cfw_test_font_foreground_xip;
char open_cfw_test_font_xip_name[16];
uint8_t open_cfw_test_font_xip_native;

static uint8_t open_cfw_test_font_native[8][64];
static uint8_t open_cfw_test_font_freetype[8][64];
static uint32_t open_cfw_test_font_alloc_calls;
static uint32_t open_cfw_test_font_free_calls;
static uint32_t open_cfw_test_font_fail_alloc_call;
static uint32_t open_cfw_test_font_freetype_create_calls;
static uint32_t open_cfw_test_font_freetype_delete_calls;
static uint32_t open_cfw_test_font_lock_calls;
static uint32_t open_cfw_test_font_unlock_calls;

void *open_cfw_retained_font_manager_alloc(size_t size)
{
    ++open_cfw_test_font_alloc_calls;
    if (open_cfw_test_font_fail_alloc_call != 0U &&
        open_cfw_test_font_alloc_calls == open_cfw_test_font_fail_alloc_call) {
        return NULL;
    }
    return calloc(1U, size);
}

void open_cfw_retained_font_manager_free(void *pointer)
{
    if (pointer != NULL) {
        ++open_cfw_test_font_free_calls;
        free(pointer);
    }
}

void *open_cfw_retained_font_manager_freetype_create(
    const char *name,
    uint32_t render_mode,
    uint16_t size,
    uint8_t style
)
{
    uint32_t slot = open_cfw_test_font_freetype_create_calls++;
    (void)render_mode;
    (void)size;
    (void)style;
    if (name == NULL || strcmp(name, "fail") == 0 || slot >= 8U) {
        return NULL;
    }
    return open_cfw_test_font_freetype[slot];
}

void open_cfw_retained_font_manager_freetype_delete(void *font)
{
    if (font != NULL) {
        ++open_cfw_test_font_freetype_delete_calls;
    }
}

void open_cfw_retained_font_manager_mspi_lock(void)
{
    ++open_cfw_test_font_lock_calls;
}

void open_cfw_retained_font_manager_mspi_unlock(void)
{
    ++open_cfw_test_font_unlock_calls;
}

void *open_cfw_retained_font_manager_memset(void *p, int value, size_t size)
{
    return memset(p, value, size);
}

void *open_cfw_retained_font_manager_memcpy(
    void *destination,
    const void *source,
    size_t size
)
{
    return memcpy(destination, source, size);
}

int open_cfw_test_font_is_native(const void *font_data)
{
    return (uintptr_t)font_data == 0x00100000U;
}

static void open_cfw_test_font_reset(void)
{
    memset(open_cfw_test_font_background_configs, 0,
           sizeof(open_cfw_test_font_background_configs));
    memset(open_cfw_test_font_foreground_configs, 0,
           sizeof(open_cfw_test_font_foreground_configs));
    memset(open_cfw_test_font_native, 0, sizeof(open_cfw_test_font_native));
    memset(open_cfw_test_font_freetype, 0, sizeof(open_cfw_test_font_freetype));
    memset(open_cfw_test_font_xip_scratch, 0xA5,
           sizeof(open_cfw_test_font_xip_scratch));
    memset(&open_cfw_test_font_background_header, 0,
           sizeof(open_cfw_test_font_background_header));
    memset(&open_cfw_test_font_foreground_header, 0,
           sizeof(open_cfw_test_font_foreground_header));
    memset(&open_cfw_test_font_background_xip, 0,
           sizeof(open_cfw_test_font_background_xip));
    memset(&open_cfw_test_font_foreground_xip, 0,
           sizeof(open_cfw_test_font_foreground_xip));
    memset(open_cfw_test_font_xip_name, 0, sizeof(open_cfw_test_font_xip_name));
    open_cfw_test_font_background_manager = NULL;
    open_cfw_test_font_foreground_manager = NULL;
    open_cfw_test_font_background_font = NULL;
    open_cfw_test_font_foreground_font = NULL;
    open_cfw_test_font_xip_native = 0U;
    open_cfw_test_font_alloc_calls = 0U;
    open_cfw_test_font_free_calls = 0U;
    open_cfw_test_font_fail_alloc_call = 0U;
    open_cfw_test_font_freetype_create_calls = 0U;
    open_cfw_test_font_freetype_delete_calls = 0U;
    open_cfw_test_font_lock_calls = 0U;
    open_cfw_test_font_unlock_calls = 0U;
}

uint32_t open_cfw_test_font_chain_scenario(uint32_t fail_alloc_call)
{
    open_cfw_font_config configs[4];
    open_cfw_font_manager *manager;
    void *first;
    void *second;
    void *third;
    uint32_t result = 0U;

    open_cfw_test_font_reset();
    memset(configs, 0, sizeof(configs));
    configs[0].type = OPEN_CFW_FONT_TYPE_NATIVE;
    configs[0].source = open_cfw_test_font_native[0];
    configs[1].type = OPEN_CFW_FONT_TYPE_FREETYPE;
    configs[1].source = "font-one";
    configs[1].size = 24U;
    configs[1].style = 3U;
    configs[2].type = OPEN_CFW_FONT_TYPE_FREETYPE;
    configs[2].source = "fail";
    configs[3].type = OPEN_CFW_FONT_TYPE_NATIVE;
    configs[3].source = open_cfw_test_font_native[3];
    open_cfw_test_font_fail_alloc_call = fail_alloc_call;
    manager = open_cfw_font_manager_create_chain(configs, 4U);
    if (manager == NULL) {
        return 0U;
    }
    first = (void *)configs[0].source;
    second = open_cfw_test_font_freetype[0];
    third = (void *)configs[3].source;
    result |= manager->head == first ? 1U : 0U;
    result |= manager->count == 3U ? 2U : 0U;
    result |= *(void **)((uint8_t *)first + 0x1CU) == second ? 4U : 0U;
    result |= *(void **)((uint8_t *)second + 0x1CU) == third ? 8U : 0U;
    result |= *(void **)((uint8_t *)third + 0x1CU) == NULL ? 16U : 0U;
    result |= open_cfw_test_font_freetype_create_calls == 2U ? 32U : 0U;
    return result;
}

uint32_t open_cfw_test_font_invalid_scenario(void)
{
    open_cfw_font_config config;
    open_cfw_test_font_reset();
    memset(&config, 0, sizeof(config));
    return
        (open_cfw_font_manager_create_chain(NULL, 1U) == NULL ? 1U : 0U) |
        (open_cfw_font_manager_create_chain(&config, 0U) == NULL ? 2U : 0U) |
        (open_cfw_font_manager_create_chain(&config, 9U) == NULL ? 4U : 0U) |
        (open_cfw_font_manager_get_font(NULL) == NULL ? 8U : 0U);
}

uint32_t open_cfw_test_font_cleanup_scenario(void)
{
    open_cfw_test_font_reset();
    open_cfw_font_manager_cleanup_single(open_cfw_test_font_native[0], 0U);
    open_cfw_font_manager_cleanup_single(open_cfw_test_font_freetype[0], 1U);
    open_cfw_font_manager_cleanup_single(open_cfw_test_font_freetype[1], 2U);
    open_cfw_font_manager_cleanup_single(NULL, 1U);
    return open_cfw_test_font_freetype_delete_calls;
}

uint32_t open_cfw_test_font_xip_scenario(uint32_t foreground_valid)
{
    open_cfw_test_font_reset();
    open_cfw_test_font_background_header.magic = OPEN_CFW_FONT_XIP_MAGIC;
    memcpy(open_cfw_test_font_background_header.name, "background-font", 16U);
    open_cfw_test_font_background_header.font_data = 0x00100000U;
    open_cfw_test_font_background_header.size = 28U;
    open_cfw_test_font_background_header.style = 5U;
    open_cfw_test_font_foreground_header.magic = foreground_valid != 0U
        ? OPEN_CFW_FONT_XIP_MAGIC : 0U;
    open_cfw_test_font_foreground_header.font_data = 0x00700000U;
    open_cfw_test_font_foreground_header.size = UINT16_MAX;
    open_cfw_test_font_foreground_header.style = UINT16_MAX;
    open_cfw_test_font_background_xip.size = 1U;
    open_cfw_test_font_background_xip.style = 2U;
    open_cfw_test_font_foreground_xip.size = 33U;
    open_cfw_test_font_foreground_xip.style = 6U;
    open_cfw_font_manager_configure_xip();
    return
        (open_cfw_test_font_lock_calls == 1U ? 1U : 0U) |
        (open_cfw_test_font_unlock_calls == 1U ? 2U : 0U) |
        (open_cfw_test_font_xip_scratch[0] == 0U &&
         open_cfw_test_font_xip_scratch[0x4FFF] == 0U ? 4U : 0U) |
        (open_cfw_test_font_background_xip.font_data ==
             (void *)(uintptr_t)0x00100000U ? 8U : 0U) |
        (open_cfw_test_font_background_xip.size == 28U ? 16U : 0U) |
        (open_cfw_test_font_background_xip.style == 5U ? 32U : 0U) |
        (open_cfw_test_font_background_xip.loader ==
             (void *)(uintptr_t)0x0046D239U ? 64U : 0U) |
        (open_cfw_test_font_xip_native == 1U ? 128U : 0U) |
        (memcmp(open_cfw_test_font_xip_name, "background-font", 15U) == 0
             ? 256U : 0U) |
        ((foreground_valid != 0U
              ? open_cfw_test_font_foreground_xip.font_data ==
                    (void *)(uintptr_t)0x00700000U
              : open_cfw_test_font_foreground_xip.font_data == NULL)
             ? 512U : 0U) |
        (open_cfw_test_font_foreground_xip.size == 33U &&
         open_cfw_test_font_foreground_xip.style == 6U ? 1024U : 0U);
}

uint32_t open_cfw_test_font_init_scenario(void)
{
    uint32_t index;
    open_cfw_test_font_reset();
    for (index = 0U; index < 4U; ++index) {
        open_cfw_test_font_background_configs[index].type = 0U;
        open_cfw_test_font_background_configs[index].source =
            open_cfw_test_font_native[index];
        open_cfw_test_font_foreground_configs[index].type = 0U;
        open_cfw_test_font_foreground_configs[index].source =
            open_cfw_test_font_native[index + 4U];
    }
    open_cfw_font_manager_init();
    return
        (open_cfw_test_font_background_manager != NULL ? 1U : 0U) |
        (open_cfw_test_font_foreground_manager != NULL ? 2U : 0U) |
        (open_cfw_test_font_background_font == open_cfw_test_font_native[0]
             ? 4U : 0U) |
        (open_cfw_test_font_foreground_font == open_cfw_test_font_native[4]
             ? 8U : 0U) |
        (open_cfw_test_font_background_manager != NULL &&
         open_cfw_test_font_background_manager->count == 4U ? 16U : 0U) |
        (open_cfw_test_font_foreground_manager != NULL &&
         open_cfw_test_font_foreground_manager->count == 4U ? 32U : 0U) |
        (open_cfw_font_manager_xip_name() == open_cfw_test_font_xip_name
             ? 64U : 0U);
}
