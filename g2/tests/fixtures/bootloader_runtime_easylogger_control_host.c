#include <stdint.h>

#define OPEN_CFW_EASYLOGGER_HELPERS_PROFILE \
    OPEN_CFW_EASYLOGGER_HELPERS_PROFILE_BOOTLOADER
#define OPEN_CFW_BOOTLOADER_EASYLOGGER_CONTROL_HOST 1
#include "../../components/bootloader/core_overlay/runtime_easylogger_control_41733c.c"

static struct open_cfw_easylogger_helpers_logger logger_state;
static open_cfw_bootloader_elog_u8 port_result;
static unsigned port_init_calls;
static unsigned lock_enable_calls;
static unsigned port_lock_calls;
static unsigned port_unlock_calls;
static unsigned output_calls;
static unsigned assert_calls;
static open_cfw_bootloader_elog_u32 last_assert_line;

static void reset_state(void)
{
    unsigned char *bytes = (unsigned char *)&logger_state;
    open_cfw_bootloader_elog_u32 index;
    for (index = 0U; index < sizeof(logger_state); ++index) {
        bytes[index] = 0U;
    }
    port_result = 0U;
    port_init_calls = 0U;
    lock_enable_calls = 0U;
    port_lock_calls = 0U;
    port_unlock_calls = 0U;
    output_calls = 0U;
    assert_calls = 0U;
    last_assert_line = 0U;
}

struct open_cfw_easylogger_helpers_logger *
open_cfw_bootloader_easylogger_host_get_logger(void)
{
    return &logger_state;
}

open_cfw_bootloader_elog_u8
open_cfw_bootloader_easylogger_host_port_init(void)
{
    ++port_init_calls;
    return port_result;
}

void open_cfw_bootloader_easylogger_host_output_lock_enabled(
    open_cfw_bootloader_elog_u8 enabled)
{
    ++lock_enable_calls;
    logger_state.output_lock_enabled = enabled;
}

void open_cfw_bootloader_easylogger_host_port_lock(void)
{
    ++port_lock_calls;
}

void open_cfw_bootloader_easylogger_host_port_unlock(void)
{
    ++port_unlock_calls;
}

void open_cfw_bootloader_easylogger_host_assert(
    open_cfw_bootloader_elog_u32 line)
{
    ++assert_calls;
    last_assert_line = line;
}

void open_cfw_bootloader_easylogger_host_start_output(void)
{
    ++output_calls;
}

int open_cfw_bootloader_easylogger_host_strncmp(
    const char *left,
    const char *right,
    open_cfw_bootloader_elog_u32 count)
{
    open_cfw_bootloader_elog_u32 index;
    for (index = 0U; index < count; ++index) {
        const unsigned char a = (unsigned char)left[index];
        const unsigned char b = (unsigned char)right[index];
        if (a != b) {
            return (int)a - (int)b;
        }
        if (a == 0U) {
            return 0;
        }
    }
    return 0;
}

static void set_slot(
    open_cfw_bootloader_elog_u32 slot,
    const char *tag,
    open_cfw_bootloader_elog_u8 level)
{
    open_cfw_bootloader_elog_u32 index = 0U;
    while (index < OPEN_CFW_BOOTLOADER_ELOG_TAG_MAX && tag[index] != '\0') {
        logger_state.filter.tag_level[slot].tag[index] = tag[index];
        ++index;
    }
    logger_state.filter.tag_level[slot].tag[index] = '\0';
    logger_state.filter.tag_level[slot].level = level;
    logger_state.filter.tag_level[slot].tag_use_flag = 1U;
}

unsigned open_cfw_test_easylogger_control_init(void)
{
    open_cfw_bootloader_elog_u32 slot;
    reset_state();
    port_result = 7U;
    if (open_cfw_bootloader_easylogger_init_41733c() != 7U ||
            logger_state.init_ok != 0U || port_init_calls != 1U) {
        return 0U;
    }
    reset_state();
    for (slot = 0U; slot < OPEN_CFW_BOOTLOADER_ELOG_TAG_LEVEL_COUNT; ++slot) {
        set_slot(slot, "stale", 4U);
    }
    if (open_cfw_bootloader_easylogger_init_41733c() != 0U ||
            logger_state.init_ok != 1U ||
            logger_state.filter.level != 5U ||
            logger_state.text_color_enabled != 1U ||
            logger_state.output_lock_enabled != 1U ||
            lock_enable_calls != 1U || port_init_calls != 1U) {
        return 0U;
    }
    for (slot = 0U; slot < OPEN_CFW_BOOTLOADER_ELOG_TAG_LEVEL_COUNT; ++slot) {
        if (logger_state.filter.tag_level[slot].level != 0U ||
                logger_state.filter.tag_level[slot].tag_use_flag != 0U ||
                logger_state.filter.tag_level[slot].tag[0] != '\0') {
            return 0U;
        }
    }
    (void)open_cfw_bootloader_easylogger_init_41733c();
    return port_init_calls == 1U;
}

unsigned open_cfw_test_easylogger_control_start_and_setters(void)
{
    reset_state();
    open_cfw_bootloader_easylogger_start_417392();
    if (output_calls != 0U || logger_state.output_enabled != 0U) {
        return 0U;
    }
    logger_state.init_ok = 1U;
    open_cfw_bootloader_easylogger_start_417392();
    open_cfw_bootloader_easylogger_set_text_color_enabled_417438(0U);
    open_cfw_bootloader_easylogger_set_fmt_4174a6(3U, 0xD7U);
    open_cfw_bootloader_easylogger_set_filter_lvl_417510(4U);
    if (output_calls != 1U || logger_state.output_enabled != 1U ||
            logger_state.text_color_enabled != 0U ||
            logger_state.enabled_format_set[3] != 0xD7U ||
            logger_state.filter.level != 4U) {
        return 0U;
    }
    open_cfw_bootloader_easylogger_set_output_enabled_4173ca(2U);
    if (assert_calls != 1U || last_assert_line != 278U ||
            logger_state.output_enabled != 2U) {
        return 0U;
    }
    open_cfw_bootloader_easylogger_set_text_color_enabled_417438(2U);
    return assert_calls == 2U && last_assert_line == 290U;
}

unsigned open_cfw_test_easylogger_control_locking(void)
{
    reset_state();
    open_cfw_bootloader_easylogger_output_lock_417570();
    if (logger_state.output_is_locked_before_enable != 1U ||
            port_lock_calls != 0U) {
        return 0U;
    }
    open_cfw_bootloader_easylogger_output_unlock_417592();
    if (logger_state.output_is_locked_before_enable != 0U) {
        return 0U;
    }
    logger_state.output_lock_enabled = 1U;
    open_cfw_bootloader_easylogger_output_lock_417570();
    open_cfw_bootloader_easylogger_output_unlock_417592();
    return port_lock_calls == 1U && port_unlock_calls == 1U &&
        logger_state.output_is_locked_before_disable == 0U;
}

unsigned open_cfw_test_easylogger_control_tag_levels(void)
{
    reset_state();
    if (open_cfw_bootloader_easylogger_get_filter_tag_lvl_41760a("abc") !=
            5U) {
        return 0U;
    }
    logger_state.init_ok = 1U;
    logger_state.output_lock_enabled = 1U;
    set_slot(1U, "abc", 2U);
    set_slot(3U, "other", 4U);
    if (open_cfw_bootloader_easylogger_get_filter_tag_lvl_41760a("abc") !=
            2U || port_lock_calls != 1U || port_unlock_calls != 1U) {
        return 0U;
    }
    if (open_cfw_bootloader_easylogger_get_filter_tag_lvl_41760a("missing") !=
            5U || port_lock_calls != 2U || port_unlock_calls != 2U) {
        return 0U;
    }
    open_cfw_bootloader_easylogger_filter_tag_lvl_default_4175b4();
    return logger_state.filter.tag_level[1].tag_use_flag == 0U &&
        logger_state.filter.tag_level[1].tag[0] == '\0';
}
