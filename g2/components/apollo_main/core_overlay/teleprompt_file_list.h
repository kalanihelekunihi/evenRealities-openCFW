/* SPDX-License-Identifier: MIT */
#ifndef OPEN_CFW_TELEPROMPT_FILE_LIST_H
#define OPEN_CFW_TELEPROMPT_FILE_LIST_H

#include <stdint.h>

#define OPEN_CFW_TELEPROMPT_FILE_LIST_BYTES 0x0F52U
#define OPEN_CFW_TELEPROMPT_FILE_PAYLOAD_BYTES 0x0F50U

typedef struct {
    uint16_t file_count;
    uint8_t payload[OPEN_CFW_TELEPROMPT_FILE_PAYLOAD_BYTES];
} open_cfw_teleprompt_file_list;

void open_cfw_teleprompt_file_list_update(
    const open_cfw_teleprompt_file_list *file_list
);
open_cfw_teleprompt_file_list *open_cfw_teleprompt_file_list_get(void);
void open_cfw_teleprompt_file_list_reset(void);

#endif
