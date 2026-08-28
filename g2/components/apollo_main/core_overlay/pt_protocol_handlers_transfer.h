/* SPDX-License-Identifier: MIT */
#ifndef OPEN_CFW_PT_PROTOCOL_HANDLERS_TRANSFER_H
#define OPEN_CFW_PT_PROTOCOL_HANDLERS_TRANSFER_H
#include <stddef.h>
#include <stdint.h>
#include "pt_protocol_procsr.h"

typedef int (*open_cfw_pt_transfer_action_fn)(void *context);
typedef int (*open_cfw_pt_transfer_dispatch_fn)(uint8_t type,const uint8_t *data,size_t length,void *context);
typedef int (*open_cfw_pt_transfer_status_fn)(uint8_t *status,void *context);
typedef int (*open_cfw_pt_transfer_read_fn)(uint8_t *data,size_t length,void *context);
typedef int (*open_cfw_pt_transfer_open_fn)(void *context);
typedef int (*open_cfw_pt_transfer_read_at_fn)(uint32_t offset,uint8_t *data,size_t requested,size_t *received,void *context);
typedef int (*open_cfw_pt_transfer_self_test_fn)(uint8_t *status,void *context);
struct open_cfw_pt_transfer_providers {
 open_cfw_pt_transfer_action_fn ota_initialize;
 open_cfw_pt_transfer_dispatch_fn ota_dispatch;
 open_cfw_pt_transfer_status_fn ota_status;
 open_cfw_pt_transfer_self_test_fn storage_self_test;
 open_cfw_pt_transfer_read_fn read_metadata_32;
 open_cfw_pt_transfer_status_fn storage_ready;
 open_cfw_pt_transfer_open_fn open_payload;
 open_cfw_pt_transfer_read_at_fn read_payload_at;
 open_cfw_pt_transfer_action_fn close_payload;
 void *context;
};
struct open_cfw_pt_transfer_service {
 const struct open_cfw_pt_transfer_providers *providers;
 uint8_t expected_sequence;
 uint8_t *staging;
 size_t staging_capacity;
 size_t staging_length;
 int payload_open;
};
void open_cfw_pt_transfer_initialize(
 struct open_cfw_pt_transfer_service *service,
 const struct open_cfw_pt_transfer_providers *providers,
 uint8_t *staging, size_t staging_capacity);
int open_cfw_pt_bind_transfer_handlers(struct open_cfw_pt_protocol *protocol,struct open_cfw_pt_transfer_service *service);
#endif
