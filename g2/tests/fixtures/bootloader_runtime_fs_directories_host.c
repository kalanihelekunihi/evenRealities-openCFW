#include <stdint.h>
#include <stddef.h>
#include <string.h>

#define OPEN_CFW_FS_DIRECTORIES_HOST 1
#include "../../components/bootloader/core_overlay/runtime_fs_directories_4210c8.c"

static const char *const fixture_paths[4] = {
    "/firmware", "/ota", "/user", "/log"
};
static int32_t open_results[4];
static int32_t mkdir_results[4];
static int32_t close_results[4];
static uint32_t events[64];
static uint32_t event_count;

static uint32_t fixture_index(const char *path)
{
    uint32_t index;
    for (index = 0U; index < 4U; ++index) {
        if (strcmp(path, fixture_paths[index]) == 0) return index;
    }
    return 0xFFU;
}

static void fixture_event(uint32_t kind, uint32_t index, int32_t status)
{
    if (event_count + 3U <= 64U) {
        events[event_count++] = kind;
        events[event_count++] = index;
        events[event_count++] = (uint32_t)status;
    }
}

void open_cfw_fs_directories_fixture_reset(void)
{
    uint32_t index;
    for (index = 0U; index < 4U; ++index) {
        open_results[index] = 0;
        mkdir_results[index] = 0;
        close_results[index] = 0;
    }
    for (index = 0U; index < 64U; ++index) events[index] = 0U;
    event_count = 0U;
}

void open_cfw_fs_directories_fixture_config(
    uint32_t operation, uint32_t index, int32_t result)
{
    if (index >= 4U) return;
    if (operation == 1U) open_results[index] = result;
    if (operation == 2U) mkdir_results[index] = result;
    if (operation == 3U) close_results[index] = result;
}

uint32_t open_cfw_fs_directories_fixture_value(uint32_t index)
{
    if (index == 64U) return event_count;
    return index < 64U ? events[index] : 0U;
}

const char *open_cfw_fs_directories_host_path(uint32_t index)
{
    return index < 4U ? fixture_paths[index] : (const char *)0;
}

int32_t open_cfw_fs_directories_host_open(
    open_cfw_fs_directories_dir *directory, const char *path)
{
    uint32_t index = fixture_index(path);
    directory->words[0] = index;
    fixture_event(1U, index, open_results[index]);
    return open_results[index];
}

int32_t open_cfw_fs_directories_host_mkdir(const char *path)
{
    uint32_t index = fixture_index(path);
    fixture_event(2U, index, mkdir_results[index]);
    return mkdir_results[index];
}

int32_t open_cfw_fs_directories_host_close(
    open_cfw_fs_directories_dir *directory)
{
    uint32_t index = directory->words[0];
    fixture_event(3U, index, close_results[index]);
    return close_results[index];
}

void open_cfw_fs_directories_host_log(
    uint32_t kind, const char *path, int32_t status)
{
    fixture_event(10U + kind, fixture_index(path), status);
}
