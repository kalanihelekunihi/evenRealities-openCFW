/* SPDX-License-Identifier: MIT */
#ifndef OPEN_CFW_PT_PROTOCOL_HANDLERS_SERVICES_H
#define OPEN_CFW_PT_PROTOCOL_HANDLERS_SERVICES_H

#include <stddef.h>
#include <stdint.h>
#include "pt_protocol_procsr.h"

typedef int (*open_cfw_pt_service_mode_fn)(uint8_t *mode, void *context);
typedef int (*open_cfw_pt_service_box_set_fn)(
    uint8_t level, uint8_t charging, int has_lid, uint8_t lid, void *context);
typedef int (*open_cfw_pt_service_read_fn)(uint8_t *data,size_t length,void *context);
typedef int (*open_cfw_pt_service_write_fn)(const uint8_t *data,size_t length,void *context);
typedef int (*open_cfw_pt_service_sync_fn)(uint8_t *result,void *context);
typedef int (*open_cfw_pt_service_measure_fn)(
    uint8_t selector,uint32_t *measurement,uint8_t *status,void *context);

struct open_cfw_pt_service_providers {
    open_cfw_pt_service_mode_fn get_product_mode;
    open_cfw_pt_service_box_set_fn set_box_state;
    open_cfw_pt_service_read_fn read_box_summary_7;
    open_cfw_pt_service_read_fn read_box_detail_6;
    open_cfw_pt_service_write_fn write_and_verify_time_21;
    open_cfw_pt_service_sync_fn uart_sync_test;
    open_cfw_pt_service_measure_fn calibrate_ambient;
    open_cfw_pt_service_sync_fn lens_sync_test;
    void *context;
};
int open_cfw_pt_bind_service_handlers(
    struct open_cfw_pt_protocol *protocol,
    const struct open_cfw_pt_service_providers *providers);
#endif
