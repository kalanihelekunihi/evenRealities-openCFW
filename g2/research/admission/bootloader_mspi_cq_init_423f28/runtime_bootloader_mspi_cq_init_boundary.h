/* SPDX-License-Identifier: MIT */
#ifndef OPEN_CFW_BOOTLOADER_MSPI_CQ_INIT_423F28_BOUNDARY_H
#define OPEN_CFW_BOOTLOADER_MSPI_CQ_INIT_423F28_BOUNDARY_H

#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef enum
{
    OPEN_CFW_BOOT_MSPI_CQ_INIT_EXACT_TOOLCHAIN_UNRESOLVED = 1
} open_cfw_bootloader_mspi_cq_init_admission_status_t;

typedef struct
{
    uint32_t stock_start;
    uint32_t stock_end;
    uint32_t cmdq_init_start;
    uint32_t cmdq_init_end;
    uint32_t mspi_state_base;
    uint32_t mspi_state_stride;
    uint32_t cmdq_handle_offset;
    uint32_t cmdq_interface_base;
    uint32_t cmdq_interface_count;
    uint32_t cmdq_state_base;
    uint32_t cmdq_register_table;
    const char *upstream_function;
    const char *upstream_provider;
    const char *upstream_commit;
    const char *source_license;
    const char *blocker;
    open_cfw_bootloader_mspi_cq_init_admission_status_t status;
} open_cfw_bootloader_mspi_cq_init_boundary_t;

typedef struct
{
    uint32_t cmdq_size;
    const uint32_t *cmdq_buffer;
    uint8_t priority;
} open_cfw_bootloader_cmdq_config_model_t;

typedef uint32_t (*open_cfw_bootloader_cmdq_init_model_fn)(
    void *context,
    uint8_t hardware_interface,
    const open_cfw_bootloader_cmdq_config_model_t *config,
    uint32_t handle_slot_address);

typedef struct
{
    void *context;
    open_cfw_bootloader_cmdq_init_model_fn cmdq_init;
} open_cfw_bootloader_mspi_cq_init_model_ports_t;

const open_cfw_bootloader_mspi_cq_init_boundary_t *
open_cfw_bootloader_mspi_cq_init_boundary(void);

open_cfw_bootloader_mspi_cq_init_admission_status_t
open_cfw_bootloader_mspi_cq_init_admission_status(void);

uint32_t open_cfw_bootloader_mspi_cq_init_model(
    uint32_t module,
    uint32_t length,
    const uint32_t *transfer_control_buffer,
    const open_cfw_bootloader_mspi_cq_init_model_ports_t *ports);

#ifdef __cplusplus
}
#endif

#endif
