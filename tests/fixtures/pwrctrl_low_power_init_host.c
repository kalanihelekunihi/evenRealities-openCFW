#include <stdint.h>

typedef struct open_cfw_test_low_power_register {
    unsigned int address;
    unsigned int value;
} open_cfw_test_low_power_register;

open_cfw_test_low_power_register open_cfw_test_low_power_registers[64];
unsigned int open_cfw_test_low_power_register_count;
unsigned int open_cfw_test_low_power_operations[64];
unsigned int open_cfw_test_low_power_operation_arg0[64];
unsigned int open_cfw_test_low_power_operation_arg1[64];
unsigned int open_cfw_test_low_power_operation_count;
unsigned int open_cfw_test_low_power_enabled_value;
unsigned int open_cfw_test_low_power_trim_value;
unsigned int open_cfw_test_low_power_info1_fail_call;
unsigned int open_cfw_test_low_power_info1_fail_status;
unsigned int open_cfw_test_low_power_info1_call_count;
unsigned int open_cfw_test_low_power_info1_space[2];
unsigned int open_cfw_test_low_power_info1_offset[2];
unsigned int open_cfw_test_low_power_info1_count[2];
unsigned int open_cfw_test_low_power_info1_destination[2];
unsigned int open_cfw_test_low_power_irq_value;
unsigned int open_cfw_test_low_power_subordinate_status;

static void
open_cfw_test_low_power_record(
    unsigned int operation,
    unsigned int arg0,
    unsigned int arg1
)
{
    unsigned int index = open_cfw_test_low_power_operation_count++;
    open_cfw_test_low_power_operations[index] = operation;
    open_cfw_test_low_power_operation_arg0[index] = arg0;
    open_cfw_test_low_power_operation_arg1[index] = arg1;
}

unsigned int
open_cfw_test_low_power_get(unsigned int address)
{
    unsigned int index;

    for (index = 0U; index < open_cfw_test_low_power_register_count; ++index) {
        if (open_cfw_test_low_power_registers[index].address == address) {
            return open_cfw_test_low_power_registers[index].value;
        }
    }
    return 0U;
}

void
open_cfw_test_low_power_set(unsigned int address, unsigned int value)
{
    unsigned int index;

    for (index = 0U; index < open_cfw_test_low_power_register_count; ++index) {
        if (open_cfw_test_low_power_registers[index].address == address) {
            open_cfw_test_low_power_registers[index].value = value;
            return;
        }
    }
    index = open_cfw_test_low_power_register_count++;
    open_cfw_test_low_power_registers[index].address = address;
    open_cfw_test_low_power_registers[index].value = value;
}

static unsigned int
open_cfw_test_low_power_read32(unsigned int address)
{
    return open_cfw_test_low_power_get(address);
}

static void
open_cfw_test_low_power_write32(
    unsigned int address,
    unsigned int value
)
{
    open_cfw_test_low_power_set(address, value);
}

static unsigned int
open_cfw_test_low_power_read8(unsigned int address)
{
    return open_cfw_test_low_power_get(address) & 0xFFU;
}

static void
open_cfw_test_low_power_write8(
    unsigned int address,
    unsigned int value
)
{
    unsigned int prior = open_cfw_test_low_power_get(address);
    open_cfw_test_low_power_set(
        address,
        (prior & 0xFFFFFF00U) | (value & 0xFFU)
    );
}

static unsigned int open_cfw_test_low_power_debug_disable(void)
{
    open_cfw_test_low_power_record(1U, 0U, 0U);
    return open_cfw_test_low_power_subordinate_status;
}

static unsigned int
open_cfw_test_low_power_periph_disable(unsigned int peripheral)
{
    open_cfw_test_low_power_record(2U, peripheral, 0U);
    return open_cfw_test_low_power_subordinate_status;
}

static unsigned int
open_cfw_test_low_power_cpdlp_config(unsigned int configuration)
{
    open_cfw_test_low_power_record(3U, configuration, 0U);
    return open_cfw_test_low_power_subordinate_status;
}

static unsigned int open_cfw_test_low_power_periph_enabled(
    unsigned int peripheral,
    unsigned char *enabled
)
{
    open_cfw_test_low_power_record(4U, peripheral, 0U);
    *enabled = (unsigned char)open_cfw_test_low_power_enabled_value;
    return open_cfw_test_low_power_subordinate_status;
}

static unsigned int
open_cfw_test_low_power_periph_enable(unsigned int peripheral)
{
    open_cfw_test_low_power_record(5U, peripheral, 0U);
    return open_cfw_test_low_power_subordinate_status;
}

static unsigned int
open_cfw_test_low_power_trim_get(unsigned int *output)
{
    open_cfw_test_low_power_record(6U, 0U, 0U);
    *output = open_cfw_test_low_power_trim_value;
    return open_cfw_test_low_power_subordinate_status;
}

static unsigned int open_cfw_test_low_power_info1_populate(void)
{
    open_cfw_test_low_power_record(7U, 0U, 0U);
    return open_cfw_test_low_power_subordinate_status;
}

static unsigned int open_cfw_test_low_power_info1_read(
    unsigned int info_space,
    unsigned int word_offset,
    unsigned int word_count,
    unsigned int destination
)
{
    unsigned int call = open_cfw_test_low_power_info1_call_count++;

    open_cfw_test_low_power_record(8U, word_offset, destination);
    open_cfw_test_low_power_info1_space[call] = info_space;
    open_cfw_test_low_power_info1_offset[call] = word_offset;
    open_cfw_test_low_power_info1_count[call] = word_count;
    open_cfw_test_low_power_info1_destination[call] = destination;
    if (call == open_cfw_test_low_power_info1_fail_call) {
        return open_cfw_test_low_power_info1_fail_status;
    }
    open_cfw_test_low_power_set(
        destination,
        0xA5000000U | word_offset
    );
    return 0U;
}

static unsigned int open_cfw_test_low_power_spot_init(void)
{
    open_cfw_test_low_power_record(9U, 0U, 0U);
    return open_cfw_test_low_power_subordinate_status;
}

static unsigned int
open_cfw_test_low_power_mcu_memory_config(unsigned int address)
{
    open_cfw_test_low_power_record(10U, address, 0U);
    return open_cfw_test_low_power_subordinate_status;
}

static unsigned int
open_cfw_test_low_power_sram_config(unsigned int address)
{
    open_cfw_test_low_power_record(11U, address, 0U);
    return open_cfw_test_low_power_subordinate_status;
}

static unsigned int open_cfw_test_low_power_irq_disable(void)
{
    open_cfw_test_low_power_record(12U, 0U, 0U);
    return open_cfw_test_low_power_irq_value;
}

static unsigned int open_cfw_test_low_power_spot_ton_init(void)
{
    open_cfw_test_low_power_record(13U, 0U, 0U);
    return open_cfw_test_low_power_subordinate_status;
}

static unsigned int open_cfw_test_low_power_spot_ton_update(
    unsigned int enabled,
    unsigned int gpu_mode
)
{
    open_cfw_test_low_power_record(14U, enabled, gpu_mode);
    return open_cfw_test_low_power_subordinate_status;
}

static void
open_cfw_test_low_power_irq_restore(unsigned int primask)
{
    open_cfw_test_low_power_record(15U, primask, 0U);
}

static unsigned int open_cfw_test_low_power_simobuck_autosw_init(void)
{
    open_cfw_test_low_power_record(16U, 0U, 0U);
    return open_cfw_test_low_power_subordinate_status;
}

static unsigned int open_cfw_test_low_power_clkmux_init(void)
{
    open_cfw_test_low_power_record(17U, 0U, 0U);
    return open_cfw_test_low_power_subordinate_status;
}

#define OPEN_CFW_PWRCTRL_LOW_POWER_READ32(address) \
    open_cfw_test_low_power_read32(address)
#define OPEN_CFW_PWRCTRL_LOW_POWER_WRITE32(address, value) \
    open_cfw_test_low_power_write32((address), (value))
#define OPEN_CFW_PWRCTRL_LOW_POWER_READ8(address) \
    open_cfw_test_low_power_read8(address)
#define OPEN_CFW_PWRCTRL_LOW_POWER_WRITE8(address, value) \
    open_cfw_test_low_power_write8((address), (value))
#define OPEN_CFW_PWRCTRL_LOW_POWER_DEBUG_DISABLE() \
    open_cfw_test_low_power_debug_disable()
#define OPEN_CFW_PWRCTRL_LOW_POWER_PERIPH_DISABLE(peripheral) \
    open_cfw_test_low_power_periph_disable(peripheral)
#define OPEN_CFW_PWRCTRL_LOW_POWER_CPDLP_CONFIG(configuration) \
    open_cfw_test_low_power_cpdlp_config(configuration)
#define OPEN_CFW_PWRCTRL_LOW_POWER_PERIPH_ENABLED(peripheral, enabled) \
    open_cfw_test_low_power_periph_enabled((peripheral), (enabled))
#define OPEN_CFW_PWRCTRL_LOW_POWER_PERIPH_ENABLE(peripheral) \
    open_cfw_test_low_power_periph_enable(peripheral)
#define OPEN_CFW_PWRCTRL_LOW_POWER_TRIM_GET(output) \
    open_cfw_test_low_power_trim_get(output)
#define OPEN_CFW_PWRCTRL_LOW_POWER_INFO1_POPULATE() \
    open_cfw_test_low_power_info1_populate()
#define OPEN_CFW_PWRCTRL_LOW_POWER_INFO1_READ( \
    info_space, word_offset, word_count, destination \
) \
    open_cfw_test_low_power_info1_read( \
        (info_space), (word_offset), (word_count), (destination) \
    )
#define OPEN_CFW_PWRCTRL_LOW_POWER_SPOT_INIT() \
    open_cfw_test_low_power_spot_init()
#define OPEN_CFW_PWRCTRL_LOW_POWER_MCU_MEMORY_CONFIG(configuration) \
    open_cfw_test_low_power_mcu_memory_config(configuration)
#define OPEN_CFW_PWRCTRL_LOW_POWER_SRAM_CONFIG(configuration) \
    open_cfw_test_low_power_sram_config(configuration)
#define OPEN_CFW_PWRCTRL_LOW_POWER_IRQ_DISABLE() \
    open_cfw_test_low_power_irq_disable()
#define OPEN_CFW_PWRCTRL_LOW_POWER_SPOT_TON_INIT() \
    open_cfw_test_low_power_spot_ton_init()
#define OPEN_CFW_PWRCTRL_LOW_POWER_SPOT_TON_UPDATE(enabled, gpu_mode) \
    open_cfw_test_low_power_spot_ton_update((enabled), (gpu_mode))
#define OPEN_CFW_PWRCTRL_LOW_POWER_IRQ_RESTORE(primask) \
    open_cfw_test_low_power_irq_restore(primask)
#define OPEN_CFW_PWRCTRL_LOW_POWER_SIMOBUCK_AUTOSW_INIT() \
    open_cfw_test_low_power_simobuck_autosw_init()
#define OPEN_CFW_PWRCTRL_LOW_POWER_CLKMUX_INIT() \
    open_cfw_test_low_power_clkmux_init()

#include "../../components/apollo_main/core_overlay/pwrctrl_low_power_init.c"

void open_cfw_test_low_power_reset(void)
{
    unsigned int index;

    open_cfw_test_low_power_register_count = 0U;
    open_cfw_test_low_power_operation_count = 0U;
    open_cfw_test_low_power_info1_call_count = 0U;
    for (index = 0U; index < 64U; ++index) {
        open_cfw_test_low_power_operations[index] = 0U;
        open_cfw_test_low_power_operation_arg0[index] = 0U;
        open_cfw_test_low_power_operation_arg1[index] = 0U;
    }
    for (index = 0U; index < 2U; ++index) {
        open_cfw_test_low_power_info1_space[index] = 0U;
        open_cfw_test_low_power_info1_offset[index] = 0U;
        open_cfw_test_low_power_info1_count[index] = 0U;
        open_cfw_test_low_power_info1_destination[index] = 0U;
    }

    open_cfw_test_low_power_enabled_value = 0U;
    open_cfw_test_low_power_trim_value = 0U;
    open_cfw_test_low_power_info1_fail_call = 0xFFFFFFFFU;
    open_cfw_test_low_power_info1_fail_status = 0x55U;
    open_cfw_test_low_power_irq_value = 1U;
    open_cfw_test_low_power_subordinate_status = 0U;

    open_cfw_test_low_power_set(0x4002000CU, 0x21U);
    open_cfw_test_low_power_set(0x20074F5EU, 1U);
    open_cfw_test_low_power_set(0x0078EE50U, 0x030303U);
    open_cfw_test_low_power_set(0x4002021CU, 0x10U);
    open_cfw_test_low_power_set(0x20071948U, 0x1F01600DU);
    open_cfw_test_low_power_set(0x20074F63U, 1U);
    open_cfw_test_low_power_set(0x40004044U, 0x80004000U);
    open_cfw_test_low_power_set(0x40004120U, 0xFFFFFFFFU);
    open_cfw_test_low_power_set(0x40020448U, 0xA5A5A5A5U);
    open_cfw_test_low_power_set(0x4002037CU, 0x100U);
    open_cfw_test_low_power_set(0x40020380U, 0x200U);
    open_cfw_test_low_power_set(0x20074F60U, 2U);
    open_cfw_test_low_power_set(0x400211C8U, 0x100U);
}
