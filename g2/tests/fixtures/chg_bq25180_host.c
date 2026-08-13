#include <string.h>

#include "chg_bq25180_host.h"

open_cfw_test_bq25180_runtime_type open_cfw_test_bq25180_runtime;
open_cfw_test_bq25180_runtime_type *open_cfw_test_bq25180_runtime_ptr;
uint32_t open_cfw_test_bq25180_charge_state;
uint8_t open_cfw_test_bq25180_registers[13];
uint32_t open_cfw_test_bq25180_read_count;
uint32_t open_cfw_test_bq25180_write_count;
uint32_t open_cfw_test_bq25180_assert_count;
uint32_t open_cfw_test_bq25180_diagnostic_count;
uint32_t open_cfw_test_bq25180_last_diagnostic;
uint8_t open_cfw_test_bq25180_last_bus;
uint8_t open_cfw_test_bq25180_last_address;
char open_cfw_test_bq25180_assert_expression[112];

void open_cfw_test_bq25180_read(
    uint8_t bus, uint8_t address, uint8_t reg, uint8_t *value
)
{
    open_cfw_test_bq25180_last_bus = bus;
    open_cfw_test_bq25180_last_address = address;
    ++open_cfw_test_bq25180_read_count;
    *value = open_cfw_test_bq25180_registers[reg];
}

void open_cfw_test_bq25180_write(
    uint8_t bus, uint8_t address, uint8_t reg, uint8_t value
)
{
    open_cfw_test_bq25180_last_bus = bus;
    open_cfw_test_bq25180_last_address = address;
    ++open_cfw_test_bq25180_write_count;
    open_cfw_test_bq25180_registers[reg] = value;
}

void open_cfw_test_bq25180_assert(const char *expression)
{
    ++open_cfw_test_bq25180_assert_count;
    strcpy(open_cfw_test_bq25180_assert_expression, expression);
}

void open_cfw_test_bq25180_diagnostic(uint32_t code)
{
    ++open_cfw_test_bq25180_diagnostic_count;
    open_cfw_test_bq25180_last_diagnostic = code;
}

void open_cfw_test_bq25180_reset(void)
{
    memset(&open_cfw_test_bq25180_runtime, 0, sizeof(open_cfw_test_bq25180_runtime));
    open_cfw_test_bq25180_runtime_ptr = &open_cfw_test_bq25180_runtime;
    open_cfw_test_bq25180_charge_state = 0;
    memset(open_cfw_test_bq25180_registers, 0, sizeof(open_cfw_test_bq25180_registers));
    open_cfw_test_bq25180_registers[0x0c] = 0xc0u;
    open_cfw_test_bq25180_read_count = 0;
    open_cfw_test_bq25180_write_count = 0;
    open_cfw_test_bq25180_assert_count = 0;
    open_cfw_test_bq25180_diagnostic_count = 0;
    open_cfw_test_bq25180_last_diagnostic = 0;
    open_cfw_test_bq25180_last_bus = 0;
    open_cfw_test_bq25180_last_address = 0;
    memset(open_cfw_test_bq25180_assert_expression, 0,
        sizeof(open_cfw_test_bq25180_assert_expression));
}
