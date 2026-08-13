#ifndef OPEN_CFW_CHG_BQ25180_HOST_H
#define OPEN_CFW_CHG_BQ25180_HOST_H

#include <stdint.h>

typedef struct {
    uint8_t reserved[0x14];
    uint8_t event;
    uint8_t alignment;
    uint16_t state;
} open_cfw_test_bq25180_runtime_type;

extern open_cfw_test_bq25180_runtime_type open_cfw_test_bq25180_runtime;
extern open_cfw_test_bq25180_runtime_type *open_cfw_test_bq25180_runtime_ptr;
extern uint32_t open_cfw_test_bq25180_charge_state;

void open_cfw_test_bq25180_read(uint8_t, uint8_t, uint8_t, uint8_t *);
void open_cfw_test_bq25180_write(uint8_t, uint8_t, uint8_t, uint8_t);
void open_cfw_test_bq25180_assert(const char *);
void open_cfw_test_bq25180_diagnostic(uint32_t);

#define OPEN_CFW_BQ25180_RUNTIME_POINTER_ADDRESS \
    ((uintptr_t)&open_cfw_test_bq25180_runtime_ptr)
#define OPEN_CFW_BQ25180_CHARGE_STATE_ADDRESS \
    ((uintptr_t)&open_cfw_test_bq25180_charge_state)
#define OPEN_CFW_BQ25180_BUS_READ(bus, address, reg, value) \
    open_cfw_test_bq25180_read((bus), (address), (reg), (value))
#define OPEN_CFW_BQ25180_BUS_WRITE(bus, address, reg, value) \
    open_cfw_test_bq25180_write((bus), (address), (reg), (value))
#define OPEN_CFW_BQ25180_ASSERT(condition, expression) \
    do { \
        if (!(condition)) { \
            open_cfw_test_bq25180_assert(expression); \
            __builtin_trap(); \
        } \
    } while (0)
#define OPEN_CFW_BQ25180_DIAGNOSTIC(code) \
    open_cfw_test_bq25180_diagnostic(code)

extern uint8_t open_cfw_test_bq25180_registers[13];
extern uint32_t open_cfw_test_bq25180_read_count;
extern uint32_t open_cfw_test_bq25180_write_count;
extern uint32_t open_cfw_test_bq25180_assert_count;
extern uint32_t open_cfw_test_bq25180_diagnostic_count;
extern uint32_t open_cfw_test_bq25180_last_diagnostic;
extern uint8_t open_cfw_test_bq25180_last_bus;
extern uint8_t open_cfw_test_bq25180_last_address;
extern char open_cfw_test_bq25180_assert_expression[112];

void open_cfw_test_bq25180_reset(void);

#endif
