/* SPDX-License-Identifier: BSD-3-Clause */
#ifndef OPEN_CFW_BOOTLOADER_RUNTIME_MSPI_DEVICE_CONFIGURE_PUBLIC_424BE4_H
#define OPEN_CFW_BOOTLOADER_RUNTIME_MSPI_DEVICE_CONFIGURE_PUBLIC_424BE4_H

typedef __UINT8_TYPE__ open_cfw_mspi_public_u8;
typedef __UINT16_TYPE__ open_cfw_mspi_public_u16;
typedef __UINT32_TYPE__ open_cfw_mspi_public_u32;

typedef struct open_cfw_mspi_public_config {
    open_cfw_mspi_public_u8 turnaround;
    open_cfw_mspi_public_u8 address_size;
    open_cfw_mspi_public_u8 instruction_size;
    open_cfw_mspi_public_u8 reserved3;
    open_cfw_mspi_public_u16 read_instruction;
    open_cfw_mspi_public_u16 write_instruction;
    open_cfw_mspi_public_u8 device;
    open_cfw_mspi_public_u8 write_latency;
    open_cfw_mspi_public_u8 spi_mode;
    open_cfw_mspi_public_u8 frequency;
    open_cfw_mspi_public_u8 enable_write_latency;
    open_cfw_mspi_public_u8 send_address;
    open_cfw_mspi_public_u8 send_instruction;
    open_cfw_mspi_public_u8 enable_turnaround;
    open_cfw_mspi_public_u8 emulate_ddr;
    open_cfw_mspi_public_u8 ce_latency;
    open_cfw_mspi_public_u8 reserved18;
    open_cfw_mspi_public_u8 reserved19;
    open_cfw_mspi_public_u16 dma_time_limit;
    open_cfw_mspi_public_u8 dma_boundary;
} open_cfw_mspi_public_config;

#if defined(__arm__) || defined(__thumb__)
open_cfw_mspi_public_u32
open_cfw_bootloader_mspi_device_configure_public_424be4(
    void *handle, const open_cfw_mspi_public_config *configuration);
#else
typedef struct open_cfw_mspi_public_trace {
    open_cfw_mspi_public_u32 clock_calls, clock_disable_module;
    open_cfw_mspi_public_u32 clock_enable_module, clock_select;
    open_cfw_mspi_public_u32 release_calls, request_calls;
    open_cfw_mspi_public_u32 released_source, requested_source;
    open_cfw_mspi_public_u32 device_config_calls, divisor;
    open_cfw_mspi_public_u32 sdr250, high_speed_thresholds;
    open_cfw_mspi_public_u32 release_status, request_status;
} open_cfw_mspi_public_trace;

open_cfw_mspi_public_u32
open_cfw_bootloader_mspi_device_configure_public_424be4(
    open_cfw_mspi_public_u8 *state,
    const open_cfw_mspi_public_config *configuration,
    open_cfw_mspi_public_trace *trace);
#endif

#endif
