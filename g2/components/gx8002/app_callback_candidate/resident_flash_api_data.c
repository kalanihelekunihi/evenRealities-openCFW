/* SPDX-License-Identifier: MIT
 * Stock 0x100264e4..0x1002657c: eight runtime flash-state words followed
 * by 30 callback slots. Native dispatch reads slots +4, +0x34, +0x58;
 * all nonzero targets are selected C providers. No opaque bytes retained.
 * Final SRAM alias, section adjacency, and startup copy need linker proof.
 */
#include "resident_flash_api_data.h"

extern uint32_t gx8002_resident_flash_interface_initialize_2443c(void);
extern uint32_t gx8002_resident_flash_read_2381c(uint32_t, void *, uint32_t);
extern void gx8002_resident_flash_chip_erase_23e00(void);
extern int32_t gx8002_resident_flash_erase_23d58(uint32_t, uint32_t);
extern int32_t gx8002_resident_flash_page_program_23c34(
    uint32_t, const uint8_t *, uint32_t);
extern void gx8002_resident_flash_sync_23ab8(void);
extern void gx8002_resident_flash_block_range_23a90(
    uint32_t, uint32_t, uint32_t *, uint32_t *);
extern uint32_t gx8002_resident_flash_gettype_24244(void);
extern uint32_t gx8002_resident_flash_getinfo_23858(uint32_t);
extern uint32_t gx8002_resident_flash_write_protect_mode_23980(void);
extern int32_t gx8002_resident_flash_write_protect_status_238ec(uint32_t *);
extern void gx8002_resident_flash_write_protect_lock_23a70(uint32_t);
extern void gx8002_resident_flash_write_protect_unlock_23a80(void);
extern int32_t gx8002_resident_flash_otp_lock_24250(void);
extern int32_t gx8002_resident_flash_otp_status_23ae0(uint8_t *);
extern uint32_t gx8002_resident_flash_otp_erase_23bd8(void);
extern uint32_t gx8002_resident_flash_otp_write_23eb8(
    uint32_t, const uint8_t *, uint32_t);
extern int32_t gx8002_resident_flash_otp_read_23fa4(
    uint32_t, uint8_t *, uint32_t);
extern uint32_t gx8002_resident_flash_otp_get_region_23b24(uint32_t *);
extern int32_t gx8002_resident_flash_otp_set_region_23b38(uint32_t);
extern uint32_t gx8002_resident_flash_otp_get_current_region_23b60(uint32_t *);
extern uint32_t gx8002_resident_flash_otp_get_region_size_23b78(uint32_t *);
extern int32_t gx8002_resident_flash_uid_read_24104(
    uint8_t *, int32_t, int32_t *);

uint32_t gx8002_flash_state_264e4[8]
    __attribute__((section(".gx8002.flash_state.264e4"), used,
                   aligned(4))) = {UINT32_MAX};

uintptr_t gx8002_flash_api_26504[30]
    __attribute__((section(".gx8002.flash_api.26504"), used,
                   aligned(4))) = {
    [0] = (uintptr_t)&gx8002_resident_flash_interface_initialize_2443c,
    [1] = (uintptr_t)&gx8002_resident_flash_read_2381c,
    [2] = (uintptr_t)&gx8002_resident_flash_chip_erase_23e00,
    [3] = (uintptr_t)&gx8002_resident_flash_erase_23d58,
    [4] = (uintptr_t)&gx8002_resident_flash_page_program_23c34,
    [5] = (uintptr_t)&gx8002_resident_flash_sync_23ab8,
    [7] = (uintptr_t)&gx8002_resident_flash_block_range_23a90,
    [12] = (uintptr_t)&gx8002_resident_flash_gettype_24244,
    [13] = (uintptr_t)&gx8002_resident_flash_getinfo_23858,
    [14] = (uintptr_t)&gx8002_resident_flash_write_protect_mode_23980,
    [15] = (uintptr_t)&gx8002_resident_flash_write_protect_status_238ec,
    [16] = (uintptr_t)&gx8002_resident_flash_write_protect_lock_23a70,
    [17] = (uintptr_t)&gx8002_resident_flash_write_protect_unlock_23a80,
    [18] = (uintptr_t)&gx8002_resident_flash_otp_lock_24250,
    [19] = (uintptr_t)&gx8002_resident_flash_otp_status_23ae0,
    [20] = (uintptr_t)&gx8002_resident_flash_otp_erase_23bd8,
    [21] = (uintptr_t)&gx8002_resident_flash_otp_write_23eb8,
    [22] = (uintptr_t)&gx8002_resident_flash_otp_read_23fa4,
    [23] = (uintptr_t)&gx8002_resident_flash_otp_get_region_23b24,
    [24] = (uintptr_t)&gx8002_resident_flash_otp_set_region_23b38,
    [25] = (uintptr_t)&gx8002_resident_flash_otp_get_current_region_23b60,
    [26] = (uintptr_t)&gx8002_resident_flash_otp_get_region_size_23b78,
    [29] = (uintptr_t)&gx8002_resident_flash_uid_read_24104,
};
