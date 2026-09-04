/* SPDX-License-Identifier: MIT */
#ifndef OPEN_CFW_QUICKLIST_DATA_MANAGER_H
#define OPEN_CFW_QUICKLIST_DATA_MANAGER_H

#include <stdint.h>

enum open_cfw_quicklist_result {
    OPEN_CFW_QUICKLIST_OK = 0,
    OPEN_CFW_QUICKLIST_MORE = 1,
    OPEN_CFW_QUICKLIST_INVALID_ARGUMENT = 2,
    OPEN_CFW_QUICKLIST_CAPACITY_EXCEEDED = 4,
};

typedef struct {
    uint32_t id;
    uint32_t index;
    uint32_t flags;
    uint32_t reserved_0c;
    uint32_t icon;
    uint32_t action;
    uint16_t text_length;
    char text[203];
    uint8_t continuation;
    uint8_t reserved_tail[2];
} open_cfw_quicklist_input_record;

typedef struct {
    uint32_t id;
    uint32_t index;
    uint32_t flags;
    uint32_t reserved_0c;
    uint32_t icon;
    uint32_t action;
    uint8_t continuation;
    char text[201];
    uint16_t text_length;
    uint8_t valid;
    uint8_t reserved_tail[3];
} open_cfw_quicklist_record;

typedef struct {
    open_cfw_quicklist_record records[20];
    uint8_t expected_records;
    uint8_t received_records;
    uint8_t message_type;
    uint8_t reserved_1223[5];
    uint32_t updated_epoch;
    uint32_t reserved_122c;
    uint8_t reserved_tail[8];
} open_cfw_quicklist_state;

typedef struct {
    uint8_t message_type;
    uint8_t expected_records;
    uint16_t record_count;
    uint32_t reserved_04;
    open_cfw_quicklist_input_record records[];
} open_cfw_quicklist_packet;

int open_cfw_quicklist_record_copy(
    const open_cfw_quicklist_input_record *source,
    open_cfw_quicklist_record *destination
);
int open_cfw_quicklist_data_initialize(
    const open_cfw_quicklist_input_record *record
);
int open_cfw_quicklist_data_append(const open_cfw_quicklist_packet *packet);

#endif
