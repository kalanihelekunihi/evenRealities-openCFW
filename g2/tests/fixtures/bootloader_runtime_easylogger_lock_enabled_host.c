#include <stdint.h>
#include <string.h>

#define OPEN_CFW_EASYLOGGER_HELPERS_PROFILE \
    OPEN_CFW_EASYLOGGER_HELPERS_PROFILE_BOOTLOADER
#define OPEN_CFW_BOOTLOADER_EASYLOGGER_LOCK_ENABLED_HOST 1
#include "../../components/bootloader/core_overlay/runtime_easylogger_lock_enabled_417b7c.c"

static struct open_cfw_easylogger_helpers_logger logger_state;
static uint32_t lock_calls;
static uint32_t unlock_calls;

struct open_cfw_easylogger_helpers_logger *
open_cfw_bootloader_easylogger_lock_enabled_host_get_logger(void)
{
    return &logger_state;
}

void open_cfw_bootloader_easylogger_lock_enabled_host_port_lock(void)
{
    ++lock_calls;
}

void open_cfw_bootloader_easylogger_lock_enabled_host_port_unlock(void)
{
    ++unlock_calls;
}

static void reset_state(uint8_t before_enable, uint8_t before_disable)
{
    memset(&logger_state, 0, sizeof(logger_state));
    logger_state.output_is_locked_before_enable = before_enable;
    logger_state.output_is_locked_before_disable = before_disable;
    lock_calls = 0U;
    unlock_calls = 0U;
}

uint32_t open_cfw_test_easylogger_lock_enabled_disabled_is_side_effect_free(void)
{
    reset_state(1U, 0U);
    open_cfw_bootloader_easylogger_output_lock_enabled_417b7c(0U);
    return logger_state.output_lock_enabled == 0U &&
        lock_calls == 0U && unlock_calls == 0U;
}

uint32_t open_cfw_test_easylogger_lock_enabled_relocks(void)
{
    reset_state(1U, 0U);
    open_cfw_bootloader_easylogger_output_lock_enabled_417b7c(1U);
    return logger_state.output_lock_enabled == 1U &&
        lock_calls == 1U && unlock_calls == 0U;
}

uint32_t open_cfw_test_easylogger_lock_enabled_reunlocks(void)
{
    reset_state(0U, 1U);
    open_cfw_bootloader_easylogger_output_lock_enabled_417b7c(1U);
    return logger_state.output_lock_enabled == 1U &&
        lock_calls == 0U && unlock_calls == 1U;
}

uint32_t open_cfw_test_easylogger_lock_enabled_matching_state_is_noop(void)
{
    reset_state(0U, 0U);
    open_cfw_bootloader_easylogger_output_lock_enabled_417b7c(1U);
    if (lock_calls != 0U || unlock_calls != 0U) {
        return 0U;
    }
    reset_state(1U, 1U);
    open_cfw_bootloader_easylogger_output_lock_enabled_417b7c(1U);
    return lock_calls == 0U && unlock_calls == 0U;
}
