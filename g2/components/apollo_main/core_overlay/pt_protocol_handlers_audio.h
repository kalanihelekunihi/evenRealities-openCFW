/* SPDX-License-Identifier: MIT */
#ifndef OPEN_CFW_PT_PROTOCOL_HANDLERS_AUDIO_H
#define OPEN_CFW_PT_PROTOCOL_HANDLERS_AUDIO_H
#include <stddef.h>
#include <stdint.h>
#include "pt_protocol_procsr.h"

typedef int (*open_cfw_pt_audio_mode_fn)(uint8_t *mode,void *context);
typedef int (*open_cfw_pt_audio_control_fn)(uint8_t channel,uint8_t action,uint8_t argument,void *context);
typedef int (*open_cfw_pt_audio_chunk_fn)(uint8_t selector,int restart,uint8_t data[210],uint16_t *bytes,int *done,void *context);
typedef int (*open_cfw_pt_audio_read_fn)(uint8_t *data,size_t length,void *context);
struct open_cfw_pt_audio_providers {
 open_cfw_pt_audio_mode_fn get_product_mode;
 open_cfw_pt_audio_control_fn control_channel;
 open_cfw_pt_audio_chunk_fn read_test_file_chunk;
 open_cfw_pt_audio_read_fn read_metrics_32;
 open_cfw_pt_audio_read_fn read_version_status_5;
 void *context;
};
int open_cfw_pt_bind_audio_handlers(struct open_cfw_pt_protocol *protocol,const struct open_cfw_pt_audio_providers *providers);
#endif
