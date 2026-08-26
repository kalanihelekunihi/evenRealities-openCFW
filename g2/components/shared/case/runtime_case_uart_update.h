#ifndef OPEN_CFW_RUNTIME_CASE_UART_UPDATE_H
#define OPEN_CFW_RUNTIME_CASE_UART_UPDATE_H

#include <stddef.h>
#include <stdint.h>

#define OPEN_CFW_CASE_FRAME_CHANNEL 0x5AU
#define OPEN_CFW_CASE_FRAME_SYNC_1  0xA5U
#define OPEN_CFW_CASE_FRAME_SYNC_2  0xFFU
#define OPEN_CFW_CASE_CURRENT_MAJOR 2U
#define OPEN_CFW_CASE_CURRENT_MINOR 57U

typedef enum open_cfw_case_frame_result {
    OPEN_CFW_CASE_FRAME_OK = 0,
    OPEN_CFW_CASE_FRAME_NO_HEADER = -1,
    OPEN_CFW_CASE_FRAME_TRUNCATED = -2,
    OPEN_CFW_CASE_FRAME_BAD_CHECKSUM = -3,
    OPEN_CFW_CASE_FRAME_BAD_ARGUMENT = -4
} open_cfw_case_frame_result;

typedef struct open_cfw_case_frame {
    uint8_t command;
    uint8_t length;
    const uint8_t *payload;
    uint8_t checksum;
    uint8_t header_offset;
} open_cfw_case_frame;

typedef struct open_cfw_case_ota_offer {
    uint8_t format_major;
    uint8_t version_major;
    uint8_t version_minor;
    uint32_t image_length;
    uint32_t image_checksum;
} open_cfw_case_ota_offer;

typedef enum open_cfw_case_ota_state {
    OPEN_CFW_CASE_OTA_IDLE = 0,
    OPEN_CFW_CASE_OTA_CHECK_READY,
    OPEN_CFW_CASE_OTA_GET_RUNNING_BANK,
    OPEN_CFW_CASE_OTA_ERASE_TARGET,
    OPEN_CFW_CASE_OTA_COPY_SERIAL,
    OPEN_CFW_CASE_OTA_RECEIVE_IMAGE,
    OPEN_CFW_CASE_OTA_VERIFY_IMAGE,
    OPEN_CFW_CASE_OTA_INFORM_RESULT,
    OPEN_CFW_CASE_OTA_SWAP_AND_RESET,
    OPEN_CFW_CASE_OTA_DONE,
    OPEN_CFW_CASE_OTA_FAILED
} open_cfw_case_ota_state;

typedef struct open_cfw_case_ota_context {
    open_cfw_case_ota_state state;
    open_cfw_case_ota_offer offer;
    uint8_t running_bank;
    uint8_t target_bank;
    uint8_t retry_count;
    uint8_t result;
} open_cfw_case_ota_context;

typedef struct open_cfw_case_ota_port {
    int (*glasses_ready)(void *context);
    int (*get_running_bank)(void *context, uint8_t *bank);
    int (*erase_bank)(void *context, uint8_t bank);
    int (*copy_serial_windows)(void *context, uint8_t from_bank, uint8_t to_bank);
    int (*receive_image)(void *context, uint8_t bank, uint32_t length);
    int (*verify_image)(void *context, uint8_t bank, uint32_t length, uint32_t checksum);
    int (*inform_glasses)(void *context, uint8_t result);
    int (*swap_and_reset)(void *context, uint8_t target_bank);
    void *context;
} open_cfw_case_ota_port;

typedef int (*open_cfw_case_channel_write)(uint8_t channel, uint8_t command,
                                           uint8_t length, uint8_t *payload,
                                           void *context);

int open_cfw_case_frame_find_validate(const uint8_t *bytes, size_t size,
                                      open_cfw_case_frame *frame);
uint8_t open_cfw_case_frame_checksum(uint8_t length, const uint8_t *payload);
uint32_t open_cfw_case_image_be32_sum(const uint8_t *bytes, size_t size);
int open_cfw_case_parse_ota_offer(const open_cfw_case_frame *frame,
                                  open_cfw_case_ota_offer *offer);
int open_cfw_case_validate_chunk(const open_cfw_case_frame *frame);
int open_cfw_case_channel_send_retry(uint8_t command, uint8_t length,
                                     uint8_t *payload, int fill_on_failure,
                                     open_cfw_case_channel_write writer,
                                     void *context);
void open_cfw_case_ota_begin(open_cfw_case_ota_context *ota,
                             const open_cfw_case_ota_offer *offer);
open_cfw_case_ota_state open_cfw_case_ota_advance(
    open_cfw_case_ota_context *ota, const open_cfw_case_ota_port *port);

#endif
