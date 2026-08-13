#include <stdint.h>

typedef struct open_cfw_test_pwrctrl_control_register {
    uint32_t address;
    uint32_t value;
} open_cfw_test_pwrctrl_control_register;

enum {
    OPEN_CFW_TEST_PWRCTRL_CONTROL_READ = 1,
    OPEN_CFW_TEST_PWRCTRL_CONTROL_WRITE = 2,
    OPEN_CFW_TEST_PWRCTRL_CONTROL_SPOT_BEFORE_OVERRIDE = 3,
    OPEN_CFW_TEST_PWRCTRL_CONTROL_OVERRIDE_INIT = 4,
    OPEN_CFW_TEST_PWRCTRL_CONTROL_SPOT_BEFORE_ENABLE = 5,
    OPEN_CFW_TEST_PWRCTRL_CONTROL_SPOT_AFTER_ENABLE = 6,
    OPEN_CFW_TEST_PWRCTRL_CONTROL_PERIPH_ENABLED = 7,
    OPEN_CFW_TEST_PWRCTRL_CONTROL_CRYPTO_QUIESCE = 8,
    OPEN_CFW_TEST_PWRCTRL_CONTROL_PERIPH_DISABLE = 9,
    OPEN_CFW_TEST_PWRCTRL_CONTROL_STATUS_CHECK = 10,
    OPEN_CFW_TEST_PWRCTRL_CONTROL_SPOT_UPDATE = 11
};

open_cfw_test_pwrctrl_control_register
    open_cfw_test_pwrctrl_control_registers[32];
uint32_t open_cfw_test_pwrctrl_control_register_count;
uint32_t open_cfw_test_pwrctrl_control_operations[64];
uint32_t open_cfw_test_pwrctrl_control_arg0[64];
uint32_t open_cfw_test_pwrctrl_control_arg1[64];
uint32_t open_cfw_test_pwrctrl_control_arg2[64];
uint32_t open_cfw_test_pwrctrl_control_arg3[64];
uint32_t open_cfw_test_pwrctrl_control_arg4[64];
uint32_t open_cfw_test_pwrctrl_control_operation_count;
uint32_t open_cfw_test_pwrctrl_control_enabled;
uint32_t open_cfw_test_pwrctrl_control_enabled_status;
uint32_t open_cfw_test_pwrctrl_control_quiesce_status;
uint32_t open_cfw_test_pwrctrl_control_disable_status;
uint32_t open_cfw_test_pwrctrl_control_status_check_results[2];
uint32_t open_cfw_test_pwrctrl_control_status_check_count;
uint32_t open_cfw_test_pwrctrl_control_spot_results[2];
uint32_t open_cfw_test_pwrctrl_control_spot_outputs[2];
uint32_t open_cfw_test_pwrctrl_control_spot_count;

static void
open_cfw_test_pwrctrl_control_record(
    uint32_t operation,
    uint32_t arg0,
    uint32_t arg1,
    uint32_t arg2,
    uint32_t arg3,
    uint32_t arg4
)
{
    uint32_t index = open_cfw_test_pwrctrl_control_operation_count++;

    if (index < 64U) {
        open_cfw_test_pwrctrl_control_operations[index] = operation;
        open_cfw_test_pwrctrl_control_arg0[index] = arg0;
        open_cfw_test_pwrctrl_control_arg1[index] = arg1;
        open_cfw_test_pwrctrl_control_arg2[index] = arg2;
        open_cfw_test_pwrctrl_control_arg3[index] = arg3;
        open_cfw_test_pwrctrl_control_arg4[index] = arg4;
    }
}

uint32_t
open_cfw_test_pwrctrl_control_get(uint32_t address)
{
    uint32_t index;

    for (
        index = 0U;
        index < open_cfw_test_pwrctrl_control_register_count;
        ++index
    ) {
        if (
            open_cfw_test_pwrctrl_control_registers[index].address
            == address
        ) {
            return open_cfw_test_pwrctrl_control_registers[index].value;
        }
    }
    return 0U;
}

void
open_cfw_test_pwrctrl_control_set(uint32_t address, uint32_t value)
{
    uint32_t index;

    for (
        index = 0U;
        index < open_cfw_test_pwrctrl_control_register_count;
        ++index
    ) {
        if (
            open_cfw_test_pwrctrl_control_registers[index].address
            == address
        ) {
            open_cfw_test_pwrctrl_control_registers[index].value = value;
            return;
        }
    }

    index = open_cfw_test_pwrctrl_control_register_count++;
    open_cfw_test_pwrctrl_control_registers[index].address = address;
    open_cfw_test_pwrctrl_control_registers[index].value = value;
}

static uint32_t
open_cfw_test_pwrctrl_control_read32(uint32_t address)
{
    uint32_t value = open_cfw_test_pwrctrl_control_get(address);

    open_cfw_test_pwrctrl_control_record(
        OPEN_CFW_TEST_PWRCTRL_CONTROL_READ,
        address,
        value,
        0U,
        0U,
        0U
    );
    return value;
}

static void
open_cfw_test_pwrctrl_control_write32(uint32_t address, uint32_t value)
{
    open_cfw_test_pwrctrl_control_record(
        OPEN_CFW_TEST_PWRCTRL_CONTROL_WRITE,
        address,
        value,
        0U,
        0U,
        0U
    );
    open_cfw_test_pwrctrl_control_set(address, value);
}

static void open_cfw_test_pwrctrl_control_spot_before_override(void)
{
    open_cfw_test_pwrctrl_control_record(
        OPEN_CFW_TEST_PWRCTRL_CONTROL_SPOT_BEFORE_OVERRIDE,
        0U,
        0U,
        0U,
        0U,
        0U
    );
}

static void open_cfw_test_pwrctrl_control_override_init(void)
{
    open_cfw_test_pwrctrl_control_record(
        OPEN_CFW_TEST_PWRCTRL_CONTROL_OVERRIDE_INIT,
        0U,
        0U,
        0U,
        0U,
        0U
    );
}

static void open_cfw_test_pwrctrl_control_spot_before_enable(void)
{
    open_cfw_test_pwrctrl_control_record(
        OPEN_CFW_TEST_PWRCTRL_CONTROL_SPOT_BEFORE_ENABLE,
        0U,
        0U,
        0U,
        0U,
        0U
    );
}

static void open_cfw_test_pwrctrl_control_spot_after_enable(void)
{
    open_cfw_test_pwrctrl_control_record(
        OPEN_CFW_TEST_PWRCTRL_CONTROL_SPOT_AFTER_ENABLE,
        0U,
        0U,
        0U,
        0U,
        0U
    );
}

static uint32_t
open_cfw_test_pwrctrl_control_periph_enabled(
    uint32_t peripheral,
    unsigned char *enabled
)
{
    open_cfw_test_pwrctrl_control_record(
        OPEN_CFW_TEST_PWRCTRL_CONTROL_PERIPH_ENABLED,
        peripheral,
        0U,
        0U,
        0U,
        0U
    );
    *enabled = (unsigned char)open_cfw_test_pwrctrl_control_enabled;
    return open_cfw_test_pwrctrl_control_enabled_status;
}

static uint32_t open_cfw_test_pwrctrl_control_crypto_quiesce(void)
{
    open_cfw_test_pwrctrl_control_record(
        OPEN_CFW_TEST_PWRCTRL_CONTROL_CRYPTO_QUIESCE,
        0U,
        0U,
        0U,
        0U,
        0U
    );
    return open_cfw_test_pwrctrl_control_quiesce_status;
}

static uint32_t
open_cfw_test_pwrctrl_control_periph_disable(uint32_t peripheral)
{
    open_cfw_test_pwrctrl_control_record(
        OPEN_CFW_TEST_PWRCTRL_CONTROL_PERIPH_DISABLE,
        peripheral,
        0U,
        0U,
        0U,
        0U
    );
    return open_cfw_test_pwrctrl_control_disable_status;
}

static uint32_t
open_cfw_test_pwrctrl_control_status_check(
    uint32_t maximum_wait,
    uint32_t address,
    uint32_t mask,
    uint32_t expected,
    uint32_t wait
)
{
    uint32_t call = open_cfw_test_pwrctrl_control_status_check_count++;

    open_cfw_test_pwrctrl_control_record(
        OPEN_CFW_TEST_PWRCTRL_CONTROL_STATUS_CHECK,
        maximum_wait,
        address,
        mask,
        expected,
        wait
    );
    return open_cfw_test_pwrctrl_control_status_check_results[call];
}

static uint32_t
open_cfw_test_pwrctrl_control_spot_update(
    uint32_t stimulus,
    uint32_t enabled,
    uint32_t *status
)
{
    uint32_t call = open_cfw_test_pwrctrl_control_spot_count++;

    open_cfw_test_pwrctrl_control_record(
        OPEN_CFW_TEST_PWRCTRL_CONTROL_SPOT_UPDATE,
        stimulus,
        enabled,
        *status,
        0U,
        0U
    );
    *status = open_cfw_test_pwrctrl_control_spot_outputs[call];
    return open_cfw_test_pwrctrl_control_spot_results[call];
}

#define OPEN_CFW_PWRCTRL_CONTROL_READ32(address) \
    open_cfw_test_pwrctrl_control_read32(address)
#define OPEN_CFW_PWRCTRL_CONTROL_WRITE32(address, value) \
    open_cfw_test_pwrctrl_control_write32((address), (value))
#define OPEN_CFW_PWRCTRL_CONTROL_SPOT_BEFORE_OVERRIDE() \
    open_cfw_test_pwrctrl_control_spot_before_override()
#define OPEN_CFW_PWRCTRL_CONTROL_BUCK_LDO_OVERRIDE_INIT() \
    open_cfw_test_pwrctrl_control_override_init()
#define OPEN_CFW_PWRCTRL_CONTROL_SPOT_BEFORE_ENABLE() \
    open_cfw_test_pwrctrl_control_spot_before_enable()
#define OPEN_CFW_PWRCTRL_CONTROL_SPOT_AFTER_ENABLE() \
    open_cfw_test_pwrctrl_control_spot_after_enable()
#define OPEN_CFW_PWRCTRL_CONTROL_PERIPH_ENABLED(peripheral, enabled) \
    open_cfw_test_pwrctrl_control_periph_enabled((peripheral), (enabled))
#define OPEN_CFW_PWRCTRL_CONTROL_CRYPTO_QUIESCE() \
    open_cfw_test_pwrctrl_control_crypto_quiesce()
#define OPEN_CFW_PWRCTRL_CONTROL_PERIPH_DISABLE(peripheral) \
    open_cfw_test_pwrctrl_control_periph_disable(peripheral)
#define OPEN_CFW_PWRCTRL_CONTROL_STATUS_CHECK( \
    maximum_wait, address, mask, expected, wait \
) \
    open_cfw_test_pwrctrl_control_status_check( \
        (maximum_wait), (address), (mask), (expected), (wait) \
    )
#define OPEN_CFW_PWRCTRL_CONTROL_SPOT_UPDATE(stimulus, enabled, status) \
    open_cfw_test_pwrctrl_control_spot_update( \
        (stimulus), (enabled), (status) \
    )

#include "../../components/apollo_main/core_overlay/pwrctrl_control.c"

void open_cfw_test_pwrctrl_control_reset(void)
{
    uint32_t index;

    open_cfw_test_pwrctrl_control_register_count = 0U;
    open_cfw_test_pwrctrl_control_operation_count = 0U;
    open_cfw_test_pwrctrl_control_enabled = 0U;
    open_cfw_test_pwrctrl_control_enabled_status = 0U;
    open_cfw_test_pwrctrl_control_quiesce_status = 0U;
    open_cfw_test_pwrctrl_control_disable_status = 0U;
    open_cfw_test_pwrctrl_control_status_check_count = 0U;
    open_cfw_test_pwrctrl_control_spot_count = 0U;

    for (index = 0U; index < 32U; ++index) {
        open_cfw_test_pwrctrl_control_registers[index].address = 0U;
        open_cfw_test_pwrctrl_control_registers[index].value = 0U;
    }
    for (index = 0U; index < 64U; ++index) {
        open_cfw_test_pwrctrl_control_operations[index] = 0U;
        open_cfw_test_pwrctrl_control_arg0[index] = 0U;
        open_cfw_test_pwrctrl_control_arg1[index] = 0U;
        open_cfw_test_pwrctrl_control_arg2[index] = 0U;
        open_cfw_test_pwrctrl_control_arg3[index] = 0U;
        open_cfw_test_pwrctrl_control_arg4[index] = 0U;
    }
    for (index = 0U; index < 2U; ++index) {
        open_cfw_test_pwrctrl_control_status_check_results[index] = 0U;
        open_cfw_test_pwrctrl_control_spot_results[index] = 0U;
        open_cfw_test_pwrctrl_control_spot_outputs[index] = 0U;
    }
}
