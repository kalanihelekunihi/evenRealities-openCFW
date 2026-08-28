/* SPDX-License-Identifier: MIT */
#ifndef OPEN_CFW_PT_PROTOCOL_PROCSR_H
#define OPEN_CFW_PT_PROTOCOL_PROCSR_H

#include <stddef.h>
#include <stdint.h>

#define OPEN_CFW_PT_COMMAND_COUNT 66U
#define OPEN_CFW_PT_MAX_FRAME_SIZE 256U
#define OPEN_CFW_PT_HEADER_SIZE 4U
#define OPEN_CFW_PT_CHECKSUM_SIZE 1U

enum open_cfw_pt_result {
    OPEN_CFW_PT_OK = 0,
    OPEN_CFW_PT_INVALID_ARGUMENT = -1,
    OPEN_CFW_PT_HEADER_FAILED = -2,
    OPEN_CFW_PT_FRAME_TOO_LARGE = -3,
    OPEN_CFW_PT_CHECKSUM_FAILED = -4,
    OPEN_CFW_PT_HANDLER_FAILED = -5,
    OPEN_CFW_PT_COMMAND_NOT_FOUND = -6
};

struct open_cfw_pt_time {
    uint32_t hour;
    uint32_t minute;
    uint32_t second;
};

typedef int (*open_cfw_pt_file_tell_fn)(void *file, void *context);
typedef int (*open_cfw_pt_file_seek_fn)(
    void *file,
    int offset,
    unsigned int origin,
    void *context
);

struct open_cfw_pt_file_ops {
    open_cfw_pt_file_tell_fn tell;
    open_cfw_pt_file_seek_fn seek;
    void *context;
};

typedef int (*open_cfw_pt_handler_fn)(
    const uint8_t *request,
    uint8_t request_length,
    uint8_t *payload,
    uint8_t *payload_length,
    void *context
);

struct open_cfw_pt_handler_slot {
    open_cfw_pt_handler_fn function;
    void *context;
};

struct open_cfw_pt_protocol {
    struct open_cfw_pt_handler_slot handlers[OPEN_CFW_PT_COMMAND_COUNT];
};

uint32_t open_cfw_pt_elapsed_seconds(
    const struct open_cfw_pt_time *current,
    const struct open_cfw_pt_time *previous,
    uint32_t wrap_seconds
);

int open_cfw_pt_file_size(void *file, const struct open_cfw_pt_file_ops *ops);

int open_cfw_pt_response_prefix(
    uint8_t *response,
    uint8_t payload_length,
    uint8_t *response_length
);

int open_cfw_pt_response_checksum(uint8_t *response, uint8_t *response_length);

int open_cfw_pt_make_status_payload(
    uint8_t command,
    uint8_t value,
    uint8_t status,
    uint8_t *payload,
    uint8_t *payload_length
);

void open_cfw_pt_protocol_initialize(struct open_cfw_pt_protocol *protocol);

size_t open_cfw_pt_command_count(void);
int open_cfw_pt_command_at(size_t index, uint8_t *command);

int open_cfw_pt_protocol_bind(
    struct open_cfw_pt_protocol *protocol,
    uint8_t command,
    open_cfw_pt_handler_fn function,
    void *context
);

int open_cfw_pt_protocol_dispatch(
    const struct open_cfw_pt_protocol *protocol,
    const uint8_t *request,
    uint8_t request_length,
    uint8_t *response,
    size_t response_capacity,
    uint8_t *response_length
);

#endif
