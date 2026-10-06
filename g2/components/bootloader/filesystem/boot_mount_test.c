/* SPDX-License-Identifier: MIT */
#include "boot_mount.h"
#include "filesystem.h"
#include <assert.h>
#include <stdarg.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define NOR_BASE 0x01400000u
#define NOR_SIZE (3008u * 4096u)
static uint8_t *nor;
static lfs_t test_fs;
lfs_t *opencfw_boot_test_fs = &test_fs;
lfs_file_t opencfw_boot_test_boot_count_file;
volatile uint32_t opencfw_boot_test_ready;
uintptr_t opencfw_boot_test_mutex = 0x51;
static unsigned logs, programs, erases;

uint32_t opencfw_boot_nor_read(uint32_t address, void *out, uint32_t size) {
    assert(address >= NOR_BASE && address + size <= NOR_BASE + NOR_SIZE);
    memcpy(out, nor + address - NOR_BASE, size);
    return 0;
}
uint32_t opencfw_boot_nor_prog(uint32_t address, const void *in, uint32_t size) {
    assert(address >= NOR_BASE && address + size <= NOR_BASE + NOR_SIZE);
    uint8_t *dst = nor + address - NOR_BASE;
    const uint8_t *src = in;
    for (uint32_t i = 0; i < size; ++i) {
        assert((dst[i] & src[i]) == src[i]);
        dst[i] &= src[i];
    }
    ++programs;
    return 0;
}
uint32_t opencfw_boot_nor_erase(uint32_t address) {
    assert(address >= NOR_BASE && address + 4096 <= NOR_BASE + NOR_SIZE);
    assert((address & 4095u) == 0);
    memset(nor + address - NOR_BASE, 0xff, 4096);
    ++erases;
    return 0;
}
void opencfw_boot_fs_error(uintptr_t format, ...) { (void)format; ++logs; }
uint32_t opencfw_boot_fs_mutex_acquire(uintptr_t mutex, uint32_t timeout) { (void)mutex; (void)timeout; assert(0); return 0; }
void opencfw_boot_fs_mutex_release(uintptr_t mutex) { (void)mutex; assert(0); }
void *opencfw_boot_fs_alloc(uint32_t size) { return malloc(size); }
void opencfw_boot_fs_free(void *p) { free(p); }

static uint32_t read_count(void) {
    lfs_file_t f = {0};
    uint32_t count = 0;
    assert(lfs_file_open(&test_fs, &f, "boot_count", LFS_O_RDONLY) == 0);
    assert(lfs_file_read(&test_fs, &f, &count, sizeof(count)) == sizeof(count));
    assert(lfs_file_close(&test_fs, &f) == 0);
    return count;
}

int main(void) {
    nor = malloc(NOR_SIZE);
    assert(nor);
    memset(nor, 0xff, NOR_SIZE);
    assert(opencfw_provider_421210() == 0); /* blank NOR -> format/mount */
    assert(opencfw_boot_test_ready == 1);
    assert(read_count() == 1);
    for (const char *p[] = {"/firmware", "/ota", "/user", "/log"}, **it = p;
         it != p + 4; ++it) {
        struct lfs_info info;
        assert(lfs_stat(&test_fs, *it, &info) == 0);
        assert(info.type == LFS_TYPE_DIR);
    }
    assert(opencfw_provider_421210() == 0); /* existing dirs/count */
    assert(read_count() == 2);
    assert(programs && erases && logs == 10);
    printf("PASS boot mount: blank-media format, mount, four dirs, boot_count 1->2; 10 init log events, no mutex calls, programs=%u, erases=%u\n",
           programs, erases);
    assert(lfs_unmount(&test_fs) == 0);
    free(nor);
    return 0;
}
