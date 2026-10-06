/* SPDX-License-Identifier: MIT
 * Real pinned littlefs and reconstructed glue over synthetic NOR, host only. */
#include "file_services.h"
#include <assert.h>
#include <stdarg.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#define START 0x01400000u
#define SIZE (3008u*4096u)
static uint8_t *flash;
static unsigned reads,programs,erases,fs_errors,allocs,frees,locks,unlocks;
static uint32_t fail_nor,fail_lock;static int fail_alloc;
lfs_t *opencfw_boot_test_fs;uintptr_t opencfw_boot_test_mutex=0x51;
uint32_t opencfw_boot_nor_read(uint32_t at,void *out,uint32_t n) {
 ++reads;if(fail_nor)return fail_nor;assert(at>=START && (uint64_t)at+n<=START+SIZE);memcpy(out,flash+at-START,n);return 0;
}
uint32_t opencfw_boot_nor_prog(uint32_t at,const void *data,uint32_t n) {
 ++programs;if(fail_nor)return fail_nor;assert(at>=START && (uint64_t)at+n<=START+SIZE);
 const uint8_t *p=data;for(uint32_t i=0;i<n;i++){assert((flash[at-START+i]&p[i])==p[i]);flash[at-START+i]&=p[i];}return 0;
}
uint32_t opencfw_boot_nor_erase(uint32_t at) {++erases;if(fail_nor)return fail_nor;assert(at>=START && at+4096<=START+SIZE);memset(flash+at-START,255,4096);return 0;}
void opencfw_boot_fs_error(uintptr_t format,...) {(void)format;++fs_errors;}
void *opencfw_boot_fs_alloc(uint32_t n) {++allocs;if(fail_alloc)return NULL;return calloc(1,n+64);/* Host64 struct larger; extra capacity is fixture only. */}
void opencfw_boot_fs_free(void *p) {++frees;free(p);}
uint32_t opencfw_boot_fs_mutex_acquire(uintptr_t m,uint32_t timeout) {assert(m==0x51 && timeout==1000);++locks;return fail_lock;}
void opencfw_boot_fs_mutex_release(uintptr_t m) {assert(m==0x51);++unlocks;}
int main(void) {
 flash=malloc(SIZE);assert(flash);memset(flash,255,SIZE);lfs_t fs={0};opencfw_boot_test_fs=&fs;
 assert(opencfw_boot_lfs_config.block_count==3008 && opencfw_boot_lfs_config.block_size==4096);
 assert(lfs_format(&fs,&opencfw_boot_lfs_config)==0);assert(lfs_mount(&fs,&opencfw_boot_lfs_config)==0);assert(lfs_mkdir(&fs,"ota")==0);
 uint8_t data[9001],out[9001];for(unsigned i=0;i<sizeof(data);i++)data[i]=(uint8_t)(i*37u);
 uintptr_t handle=opencfw_boot_file_open((uintptr_t)"ota/s200_firmware_ota.bin",(uintptr_t)"w+");assert(handle);
 /* Host struct offset differs from ARM; writing uses a separate upstream file
  * to avoid using the recovered opaque handle layout from another ABI. */
 assert(opencfw_boot_file_close(handle)==0);
 lfs_file_t file;assert(lfs_file_open(&fs,&file,"ota/s200_firmware_ota.bin",LFS_O_WRONLY)==0);assert(lfs_file_write(&fs,&file,data,sizeof(data))==sizeof(data));assert(lfs_file_close(&fs,&file)==0);
 handle=opencfw_boot_file_open((uintptr_t)"ota/s200_firmware_ota.bin",(uintptr_t)"r+");assert(handle);
 assert(opencfw_boot_file_read(out,1,sizeof(out),handle)==sizeof(out));assert(memcmp(out,data,sizeof(data))==0);
 assert(opencfw_boot_file_prepare(handle,8,0)==0);assert(opencfw_boot_file_read(out,4,100,handle)==100);assert(memcmp(out,data+8,400)==0);
 assert(opencfw_boot_file_prepare(handle,32,0)==0);assert(opencfw_boot_file_read(out,1,64,handle)==64);assert(memcmp(out,data+32,64)==0);
 assert(opencfw_boot_file_prepare(handle,0,3)==UINT32_MAX);
 fail_lock=1;assert(opencfw_boot_file_read(out,1,10,handle)==0);assert(opencfw_boot_file_prepare(handle,0,0)==UINT32_MAX);assert(opencfw_boot_file_close(handle)==UINT32_MAX);fail_lock=0;assert(opencfw_boot_file_close(handle)==0);
 fail_alloc=1;assert(!opencfw_boot_file_open((uintptr_t)"ota/s200_firmware_ota.bin",(uintptr_t)"r"));fail_alloc=0;
 fail_lock=1;assert(!opencfw_boot_file_open((uintptr_t)"ota/s200_firmware_ota.bin",(uintptr_t)"r"));fail_lock=0;
 assert(!opencfw_boot_file_open((uintptr_t)"missing",(uintptr_t)"r"));
 fail_nor=6;assert(opencfw_boot_lfs_read(&opencfw_boot_lfs_config,0,0,out,16)==-5);assert(opencfw_boot_lfs_prog(&opencfw_boot_lfs_config,0,0,out,256)==-5);assert(opencfw_boot_lfs_erase(&opencfw_boot_lfs_config,0)==-5);fail_nor=0;assert(fs_errors==3);
 assert(opencfw_boot_lfs_sync(&opencfw_boot_lfs_config)==0);assert(lfs_unmount(&fs)==0);
 memset(&fs,0,sizeof(fs));assert(lfs_mount(&fs,&opencfw_boot_lfs_config)==0);handle=opencfw_boot_file_open((uintptr_t)"ota/s200_firmware_ota.bin",(uintptr_t)"r");assert(handle);assert(opencfw_boot_file_read(out,1,sizeof(out),handle)==sizeof(out));assert(memcmp(data,out,sizeof(out))==0);assert(opencfw_boot_file_close(handle)==0);assert(lfs_unmount(&fs)==0);
 printf("PASS actual littlefs format/mount/write/read/seek/remount + reconstructed glue failures; reads=%u programs=%u erases=%u locks=%u unlocks=%u allocations=%u frees=%u\n",reads,programs,erases,locks,unlocks,allocs,frees);assert(allocs==frees+1);free(flash);return 0;
}
