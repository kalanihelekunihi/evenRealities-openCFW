/* SPDX-License-Identifier: MIT */
#include <stdint.h>
/* Shared by the flash identification routine preceding the platform setter.
 * Bindings retain the original ABI addresses; provider code is qualified
 * separately. These are semantic pointers and text, never encoded opcodes. */
extern const unsigned char open_cfw_gx8002_backup_flash_probe_slot;
extern const unsigned char open_cfw_gx8002_backup_platform_dispatch;
__attribute__((section(".otp_error"),used))
const char open_cfw_gx8002_backup_otp_error[]="read flash otp error\n";
__attribute__((section(".otp_model"),used))
const char open_cfw_gx8002_backup_otp_model[]="8003A";
__attribute__((section(".shared_literals"),used))
const void * const open_cfw_gx8002_backup_platform_literals[]={
    &open_cfw_gx8002_backup_flash_probe_slot,
    open_cfw_gx8002_backup_otp_model,
    open_cfw_gx8002_backup_otp_error,
    &open_cfw_gx8002_backup_platform_dispatch
};
