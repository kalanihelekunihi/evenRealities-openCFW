#ifndef OPEN_CFW_RUNTIME_TOUCH_I2C_PROTOCOL_H
#define OPEN_CFW_RUNTIME_TOUCH_I2C_PROTOCOL_H

#include <stddef.h>
#include <stdint.h>

#define OPEN_CFW_TOUCH_FRAME_SIZE 16U
#define OPEN_CFW_TOUCH_CONFIG_MAGIC 0x45564E55UL
#define OPEN_CFW_TOUCH_REPORT_TIMEOUT 0x280U

typedef struct open_cfw_touch_config {
    uint32_t magic;
    uint16_t proximity_baseline;
    uint16_t long_press_ms;
} open_cfw_touch_config;

typedef struct open_cfw_touch_fifo {
    uint8_t *buffer;
    uint16_t capacity;
    uint16_t position;
} open_cfw_touch_fifo;

typedef struct open_cfw_touch_protocol {
    open_cfw_touch_config config;
    uint8_t tx[OPEN_CFW_TOUCH_FRAME_SIZE];
    uint8_t report[OPEN_CFW_TOUCH_FRAME_SIZE];
    uint16_t current_baseline;
    uint16_t current_channel;
    uint16_t current_proximity;
    uint16_t current_gesture;
    uint16_t report_timeout;
    uint8_t save_baseline_pending;
    uint8_t gesture_dirty_primary;
    uint8_t gesture_dirty_secondary;
    uint8_t report_pending;
} open_cfw_touch_protocol;

typedef struct open_cfw_touch_port {
    uint16_t (*sensor_read)(void *context, uint8_t channel);
    int (*config_save)(void *context, const open_cfw_touch_config *config);
    void (*attention_set)(void *context, int asserted_low);
    void (*enter_dfu_and_reset)(void *context, uint8_t mode);
    int (*event_dispatch)(void *context, uint8_t event,
                          const uint8_t payload[3]);
    void *context;
} open_cfw_touch_port;

typedef enum open_cfw_touch_command_result {
    OPEN_CFW_TOUCH_COMMAND_OK = 0,
    OPEN_CFW_TOUCH_COMMAND_IGNORED = 1,
    OPEN_CFW_TOUCH_COMMAND_BAD_LENGTH = -1,
    OPEN_CFW_TOUCH_COMMAND_BAD_ARGUMENT = -2
} open_cfw_touch_command_result;

void open_cfw_touch_protocol_init(open_cfw_touch_protocol *state,
                                  const open_cfw_touch_config *stored);
int open_cfw_touch_handle_command(open_cfw_touch_protocol *state,
                                  const uint8_t *rx, size_t rx_length,
                                  const open_cfw_touch_port *port);
void open_cfw_touch_build_report(open_cfw_touch_protocol *state,
                                 uint8_t event, const uint8_t payload[3],
                                 const open_cfw_touch_port *port);
void open_cfw_touch_tx_complete(open_cfw_touch_protocol *state,
                                const open_cfw_touch_port *port);
int open_cfw_touch_dispatch_event(const open_cfw_touch_port *port,
                                  uint8_t event, const uint8_t payload[3]);
void open_cfw_touch_fifo_arm(open_cfw_touch_fifo *fifo, uint8_t *buffer,
                             uint16_t capacity);
uint16_t open_cfw_touch_fifo_position(const open_cfw_touch_fifo *fifo);
int open_cfw_touch_power_mode_valid(uint8_t mode);

#endif
