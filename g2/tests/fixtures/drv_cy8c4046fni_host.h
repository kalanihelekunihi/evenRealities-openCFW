#ifndef OPEN_CFW_DRV_CY8C4046FNI_HOST_H
#define OPEN_CFW_DRV_CY8C4046FNI_HOST_H

#include <stdint.h>

extern uint8_t open_cfw_test_cy8c_ops_storage[4u * sizeof(void *)];
extern uint8_t open_cfw_test_cy8c_baseline_scratch[4];
extern uint32_t open_cfw_test_cy8c_stock_ops_words[4];

int32_t open_cfw_test_cy8c_hal_register_write(
    uint32_t bus, uint32_t address, const void *command,
    uint32_t command_size, const void *data, uint16_t data_size
);
int32_t open_cfw_test_cy8c_hal_register_read(
    uint32_t bus, uint32_t address, const void *command,
    uint32_t command_size, void *data, uint16_t data_size
);
int32_t open_cfw_test_cy8c_hal_raw_write(
    uint32_t bus, uint32_t address, const void *data, uint16_t size
);
int32_t open_cfw_test_cy8c_hal_raw_read(
    uint32_t bus, uint32_t address, void *data, uint16_t size
);
void open_cfw_test_cy8c_board_control(uint32_t selector, uint32_t enabled);
void open_cfw_test_cy8c_delay(uint32_t milliseconds);
void open_cfw_test_cy8c_install_default_ops(void *ops);

#define OPEN_CFW_CY8C_OPS \
    ((open_cfw_cy8c_ops *)(void *)open_cfw_test_cy8c_ops_storage)
#define OPEN_CFW_CY8C_BASELINE_SCRATCH open_cfw_test_cy8c_baseline_scratch
#define OPEN_CFW_CY8C_STOCK_OPS_TABLE open_cfw_test_cy8c_stock_ops_words
#define OPEN_CFW_CY8C_HAL_REGISTER_WRITE(...) \
    open_cfw_test_cy8c_hal_register_write(__VA_ARGS__)
#define OPEN_CFW_CY8C_HAL_REGISTER_READ(...) \
    open_cfw_test_cy8c_hal_register_read(__VA_ARGS__)
#define OPEN_CFW_CY8C_HAL_RAW_WRITE(...) \
    open_cfw_test_cy8c_hal_raw_write(__VA_ARGS__)
#define OPEN_CFW_CY8C_HAL_RAW_READ(...) \
    open_cfw_test_cy8c_hal_raw_read(__VA_ARGS__)
#define OPEN_CFW_CY8C_BOARD_CONTROL(selector, enabled) \
    open_cfw_test_cy8c_board_control((selector), (enabled))
#define OPEN_CFW_CY8C_DELAY(milliseconds) \
    open_cfw_test_cy8c_delay(milliseconds)
#define OPEN_CFW_CY8C_HOST_INSTALL_DEFAULT_OPS(ops) \
    open_cfw_test_cy8c_install_default_ops((void *)(ops))

#endif
