/* SPDX-License-Identifier: MIT
 * Explicit reconstructed string resources, not executable retained blobs.
 * Addresses are stock pointers passed by the update core's provider ABI. */
__attribute__((section(".boot_modes"),used))
const char opencfw_boot_modes[6][4]={"w+","a+","r+","a","w","r"};
__attribute__((section(".boot_path"),used))
const char opencfw_boot_update_path[]="ota/s200_firmware_ota.bin";
