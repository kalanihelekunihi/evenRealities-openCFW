/* SPDX-License-Identifier: MIT */
/* Typed fail-closed boundary for the authenticated G2 MSPI FIFO-read leaf. */

#ifndef OPEN_CFW_BOOTLOADER_MSPI_FIFO_READ_BOUNDARY_H
#define OPEN_CFW_BOOTLOADER_MSPI_FIFO_READ_BOUNDARY_H

typedef __UINT8_TYPE__ open_cfw_mspi_read_u8;
typedef __UINT32_TYPE__ open_cfw_mspi_read_u32;

enum open_cfw_mspi_read_admission_status {
    OPEN_CFW_BOOT_MSPI_FIFO_READ_EXACT_TOOLCHAIN_UNRESOLVED = 1
};

typedef struct open_cfw_mspi_read_boundary {
    open_cfw_mspi_read_u32 stock_start;
    open_cfw_mspi_read_u32 stock_end;
    open_cfw_mspi_read_u32 status_check_start;
    open_cfw_mspi_read_u32 delay_start;
    open_cfw_mspi_read_u32 bootrom_delay_start;
    open_cfw_mspi_read_u32 mspi_base;
    open_cfw_mspi_read_u32 mspi_stride;
    open_cfw_mspi_read_u32 rxfifo_offset;
    open_cfw_mspi_read_u32 rxentries_offset;
    open_cfw_mspi_read_u32 rxentries_mask;
    open_cfw_mspi_read_u32 module_count;
    const char *upstream_function;
    const char *upstream_provider;
    const char *upstream_commit;
    const char *source_license;
    const char *blocker;
    enum open_cfw_mspi_read_admission_status status;
} open_cfw_mspi_read_boundary;

const open_cfw_mspi_read_boundary *
open_cfw_bootloader_mspi_fifo_read_boundary(void);
enum open_cfw_mspi_read_admission_status
open_cfw_bootloader_mspi_fifo_read_admission_status(void);

typedef struct open_cfw_mspi_read_model_ports {
    void *context;
    open_cfw_mspi_read_u32 (*read_word)(
        void *context, open_cfw_mspi_read_u32 address);
    open_cfw_mspi_read_u32 (*status_check)(
        void *context, open_cfw_mspi_read_u32 timeout,
        open_cfw_mspi_read_u32 address, open_cfw_mspi_read_u32 mask,
        open_cfw_mspi_read_u32 value, open_cfw_mspi_read_u8 is_equal);
} open_cfw_mspi_read_model_ports;

open_cfw_mspi_read_u32 open_cfw_bootloader_mspi_fifo_read_model(
    open_cfw_mspi_read_u32 module,
    open_cfw_mspi_read_u8 *data,
    open_cfw_mspi_read_u32 byte_count,
    open_cfw_mspi_read_u32 timeout,
    const open_cfw_mspi_read_model_ports *ports);

#endif
