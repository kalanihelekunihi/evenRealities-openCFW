/* SPDX-License-Identifier: MIT */

#ifndef OPEN_CFW_AT_FS_REMOVE_ADDRESS
#define OPEN_CFW_AT_FS_REMOVE_ADDRESS 0x007F0F74u
#endif
#ifndef OPEN_CFW_AT_FS_LIST_ADDRESS
#define OPEN_CFW_AT_FS_LIST_ADDRESS 0x007F10CCu
#endif
#ifndef OPEN_CFW_AT_FS_MKDIR_ADDRESS
#define OPEN_CFW_AT_FS_MKDIR_ADDRESS 0x007F10F8u
#endif

#define OPEN_CFW_THUMB_ENTRY(address) ((address) | 1u)

__attribute__((section(".rodata.open_cfw_at_fs_command_records"), used))
const unsigned int open_cfw_at_fs_command_records[12] = {
    3u, 0x0078CBFCu, OPEN_CFW_THUMB_ENTRY(OPEN_CFW_AT_FS_REMOVE_ADDRESS), 0u,
    3u, 0x0078CC04u, OPEN_CFW_THUMB_ENTRY(OPEN_CFW_AT_FS_LIST_ADDRESS), 0u,
    3u, 0x0078A394u, OPEN_CFW_THUMB_ENTRY(OPEN_CFW_AT_FS_MKDIR_ADDRESS), 0u,
};

_Static_assert(sizeof(open_cfw_at_fs_command_records) == 48u,
               "eAT filesystem command-record ABI drift");
