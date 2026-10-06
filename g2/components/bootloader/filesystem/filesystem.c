/* SPDX-License-Identifier: MIT
 * Bootloader littlefs config at431070 and callbacks4212d8/421310/421348/4213d4.
 * No range guard is added to the stock callback arithmetic. */
#include "filesystem.h"
#include <stddef.h>
#ifndef OPENCFW_BOOT_FS_TEST
_Static_assert(sizeof(void *)==4,"stock littlefs ABI is ARM32");
_Static_assert(sizeof(struct lfs_config)==84,"stock config is 84 bytes");
_Static_assert(offsetof(struct lfs_config,read_size)==20,"no LFS_THREADSAFE fields");
_Static_assert(offsetof(struct lfs_config,compact_thresh)==48,"v2.10 config");
_Static_assert(sizeof(lfs_file_t)<=92,"candidate file must fit stock 96-byte allocation with leading pointer");
#endif
int opencfw_boot_lfs_read(const struct lfs_config *cfg,lfs_block_t block,lfs_off_t off,void *out,lfs_size_t size) {
    (void)cfg;uint32_t address=0x01400000u+block*0x1000u+off;
    uint32_t status=opencfw_boot_nor_read(address,out,size);
    if(status) {opencfw_boot_fs_error(0x4317ccu,block,off,size,address,status);return LFS_ERR_IO;}
    return 0;
}
int opencfw_boot_lfs_prog(const struct lfs_config *cfg,lfs_block_t block,lfs_off_t off,const void *data,lfs_size_t size) {
    (void)cfg;uint32_t address=0x01400000u+block*0x1000u+off;
    uint32_t status=opencfw_boot_nor_prog(address,data,size);
    if(status) {opencfw_boot_fs_error(0x43180cu,block,off,size,address,status);return LFS_ERR_IO;}
    return 0;
}
int opencfw_boot_lfs_erase(const struct lfs_config *cfg,lfs_block_t block) {
    (void)cfg;uint32_t address=0x01400000u+block*0x1000u;
    uint32_t status=opencfw_boot_nor_erase(address);
    if(status) {opencfw_boot_fs_error(0x432568u,block,address,status);return LFS_ERR_IO;}
    return 0;
}
int opencfw_boot_lfs_sync(const struct lfs_config *cfg) {(void)cfg;return 0;}
const struct lfs_config opencfw_boot_lfs_config={
    .context=0,.read=opencfw_boot_lfs_read,.prog=opencfw_boot_lfs_prog,
    .erase=opencfw_boot_lfs_erase,.sync=opencfw_boot_lfs_sync,
    .read_size=16,.prog_size=256,.block_size=4096,.block_count=3008,
    .block_cycles=500,.cache_size=4096,.lookahead_size=256,
    .compact_thresh=0,.read_buffer=0,.prog_buffer=0,.lookahead_buffer=0,
    .name_max=0,.file_max=0,.attr_max=0,.metadata_max=0,.inline_max=0
};
