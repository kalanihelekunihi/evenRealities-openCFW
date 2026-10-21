/* SPDX-License-Identifier: MIT
 * Recovered file wrappers4153a4/415484/4154d2/415446 and substring415ffa.
 * Open-source littlefs replaces explicit LFS provider bodies only. Raw lock,
 * allocation and error behavior retained; no inferred bootloader RTOS revision.
 */
#include "file_services.h"
#ifdef OPENCFW_BOOT_FS_TEST
#define INSTANCE opencfw_boot_test_fs
#define MUTEX opencfw_boot_test_mutex
#else
#define INSTANCE ((lfs_t *)(uintptr_t)0x20026878u)
#define MUTEX (*(volatile uintptr_t *)(uintptr_t)0x2002712cu)
#endif
struct boot_file { lfs_t *fs; lfs_file_t file; };
#ifndef OPENCFW_BOOT_FS_TEST
_Static_assert(sizeof(struct boot_file)<=0x60,"candidate fits stock allocation");
#endif
static int contains(const char *s,char c) {while(*s) {if(*s++==c)return 1;}return 0;}
uintptr_t opencfw_boot_file_open(uintptr_t path,uintptr_t mode) {
    struct boot_file *file=opencfw_boot_fs_alloc(0x60);
    if(!file)return 0;
    file->fs=INSTANCE;
    const char *s=(const char *)mode;
    uint32_t flags=contains(s,'r')?1u:0u;
    if(contains(s,'w'))flags|=0x502u;
    if(contains(s,'a'))flags|=0x902u;
    if(contains(s,'+'))flags|=3u;
    uintptr_t mutex=MUTEX;
    if(opencfw_boot_fs_mutex_acquire(mutex,1000)!=0) {opencfw_boot_fs_free(file);return 0;}
    int status=lfs_file_open(file->fs,&file->file,(const char *)path,(int)flags);
    opencfw_boot_fs_mutex_release(mutex);
    if(status<0) {opencfw_boot_fs_free(file);return 0;}
    return (uintptr_t)file;
}
uint32_t opencfw_boot_file_read(void *out,uint32_t element_size,uint32_t count,uintptr_t handle) {
    struct boot_file *file=(struct boot_file *)handle;
    uintptr_t mutex=MUTEX;
    if(opencfw_boot_fs_mutex_acquire(mutex,1000)!=0)return 0;
    lfs_ssize_t read=lfs_file_read(file->fs,&file->file,out,element_size*count);
    opencfw_boot_fs_mutex_release(mutex);
    if(read<0)return 0;
    /* Raw stock division: element_size==0 is not a safe caller contract. */
    return (uint32_t)read/element_size;
}
uint32_t opencfw_boot_file_prepare(uintptr_t handle,uint32_t offset,uint32_t whence) {
    if(whence>2)return UINT32_MAX;
    struct boot_file *file=(struct boot_file *)handle;
    uintptr_t mutex=MUTEX;
    if(opencfw_boot_fs_mutex_acquire(mutex,1000)!=0)return UINT32_MAX;
    lfs_soff_t result=lfs_file_seek(file->fs,&file->file,(lfs_soff_t)offset,(int)whence);
    opencfw_boot_fs_mutex_release(mutex);
    return result<0?UINT32_MAX:0;
}
uint32_t opencfw_boot_file_close(uintptr_t handle) {
    struct boot_file *file=(struct boot_file *)handle;
    uintptr_t mutex=MUTEX;
    if(opencfw_boot_fs_mutex_acquire(mutex,1000)!=0)return UINT32_MAX;
    int result=lfs_file_close(file->fs,&file->file);
    opencfw_boot_fs_mutex_release(mutex);
    opencfw_boot_fs_free(file);
    return result<0?UINT32_MAX:0;
}
