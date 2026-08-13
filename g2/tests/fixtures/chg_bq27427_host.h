#ifndef OPEN_CFW_TEST_CHG_BQ27427_HOST_H
#define OPEN_CFW_TEST_CHG_BQ27427_HOST_H

#include <stddef.h>
#include <stdint.h>

typedef struct {
    uint32_t reserved;
    int32_t state_of_charge;
    int32_t voltage_mv;
    int32_t average_current_ma;
    int32_t temperature_centi_c;
} open_cfw_test_bq27427_runtime_type;

extern open_cfw_test_bq27427_runtime_type open_cfw_test_bq27427_runtime;

int open_cfw_test_bq27427_read(
    uint8_t bus, uint8_t address, const uint8_t *command,
    size_t command_length, uint8_t *data, size_t data_length
);
int open_cfw_test_bq27427_write(
    uint8_t bus, uint8_t address, const uint8_t *command,
    size_t command_length, const uint8_t *data, size_t data_length
);
void open_cfw_test_bq27427_delay(uint32_t delay_ms);
void open_cfw_test_bq27427_reset(void);

#define OPEN_CFW_BQ27427_TRANSFER_READ open_cfw_test_bq27427_read
#define OPEN_CFW_BQ27427_TRANSFER_WRITE open_cfw_test_bq27427_write
#define OPEN_CFW_BQ27427_DELAY_MS open_cfw_test_bq27427_delay
#define OPEN_CFW_BQ27427_RUNTIME open_cfw_test_bq27427_runtime

#endif
