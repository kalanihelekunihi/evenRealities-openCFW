/*
 * SPDX-License-Identifier: FTL
 *
 * Host-only lifecycle and allocation fixture for the G2 FreeType base admission.
 * See third_party/freetype/LICENSE.
 */

#include "runtime_freetype_base.h"
#include "runtime_freetype_base_face.h"
#include "runtime_freetype_system_candidate.h"

#include <stdint.h>
#include <stdlib.h>
#include <string.h>

static struct open_cfw_freetype_base_state test_state;
static size_t test_allocation_calls;
static size_t test_release_calls;
static size_t test_live_blocks;
static size_t test_fail_at;
static const unsigned char *test_path_data;
static size_t test_path_size;
static size_t test_path_release_calls;

static void *test_system_allocate(size_t size, void *context)
{
    (void)context;
    return malloc(size);
}

static void *test_system_reallocate(
    void *block,
    size_t current_size,
    size_t new_size,
    void *context
)
{
    (void)current_size;
    (void)context;
    return realloc(block, new_size);
}

static void test_system_release(void *block, void *context)
{
    (void)context;
    free(block);
}

static void *test_allocate(size_t size, void *context)
{
    void *block;
    (void)context;
    test_allocation_calls++;
    if (test_fail_at != 0U && test_allocation_calls == test_fail_at) {
        return NULL;
    }
    block = malloc(size);
    if (block != NULL) {
        test_live_blocks++;
    }
    return block;
}

static void *test_reallocate(
    void *block,
    size_t current_size,
    size_t new_size,
    void *context
)
{
    void *replacement;
    (void)current_size;
    (void)context;
    test_allocation_calls++;
    if (test_fail_at != 0U && test_allocation_calls == test_fail_at) {
        return NULL;
    }
    replacement = realloc(block, new_size);
    if (replacement != NULL && block == NULL) {
        test_live_blocks++;
    }
    return replacement;
}

static void test_release(void *block, void *context)
{
    (void)context;
    if (block != NULL) {
        free(block);
        test_release_calls++;
        test_live_blocks--;
    }
}

static int test_resolve_view(
    const char *pathname,
    const unsigned char **data,
    size_t *size,
    void **token,
    void *context
)
{
    (void)context;
    if (pathname == NULL || strcmp(pathname, "open-cfw-font") != 0 ||
        test_path_data == NULL || test_path_size == 0U)
        return -1;
    *data = test_path_data;
    *size = test_path_size;
    *token = (void *)test_path_data;
    return 0;
}

static void test_release_view(
    void *token,
    const unsigned char *data,
    size_t size,
    void *context
)
{
    (void)token;
    (void)data;
    (void)size;
    (void)context;
    test_path_release_calls++;
}

int open_cfw_test_freetype_system_configure(void)
{
    const struct open_cfw_freetype_system_ports ports = {
        test_system_allocate,
        test_system_reallocate,
        test_system_release,
        test_resolve_view,
        test_release_view,
        NULL
    };
    return open_cfw_freetype_system_configure(&ports);
}

void open_cfw_test_freetype_set_path_data(
    const unsigned char *data,
    size_t size
)
{
    test_path_data = data;
    test_path_size = size;
    test_path_release_calls = 0U;
}

size_t open_cfw_test_freetype_path_release_calls(void)
{
    return test_path_release_calls;
}

void open_cfw_test_freetype_reset(size_t fail_at)
{
    test_state = (struct open_cfw_freetype_base_state){0};
    test_allocation_calls = 0U;
    test_release_calls = 0U;
    test_live_blocks = 0U;
    test_fail_at = fail_at;
}

int open_cfw_test_freetype_init(void)
{
    const struct open_cfw_freetype_ports ports = {
        test_allocate,
        test_reallocate,
        test_release,
        NULL
    };
    return open_cfw_freetype_base_init(&test_state, &ports);
}

int open_cfw_test_freetype_done(void)
{
    return open_cfw_freetype_base_done(&test_state);
}

FT_Library open_cfw_test_freetype_library(void)
{
    return open_cfw_freetype_base_library(&test_state);
}

FT_Error open_cfw_test_freetype_open_memory_policy(
    const unsigned char *data,
    size_t size,
    long face_index,
    int policy,
    FT_Face *face
)
{
    return open_cfw_freetype_base_open_memory(
        &test_state,
        data,
        size,
        face_index,
        (enum open_cfw_freetype_face_policy)policy,
        face
    );
}

size_t open_cfw_test_freetype_allocation_calls(void)
{
    return test_allocation_calls;
}

size_t open_cfw_test_freetype_release_calls(void)
{
    return test_release_calls;
}

size_t open_cfw_test_freetype_live_blocks(void)
{
    return test_live_blocks;
}

size_t open_cfw_test_freetype_memory_size(void)
{
    return sizeof(struct FT_MemoryRec_);
}
