/* SPDX-License-Identifier: MIT
 * Boot mount/directory/boot counter source provider for stock 0x00421210.
 * Geometry and littlefs callbacks are supplied by filesystem.c. */
#include "boot_mount.h"
#include "file_services.h"
#include <stdint.h>

#ifdef OPENCFW_BOOT_FS_TEST
extern lfs_t *opencfw_boot_test_fs;
extern lfs_file_t opencfw_boot_test_boot_count_file;
extern volatile uint32_t opencfw_boot_test_ready;
#define BOOT_FS (opencfw_boot_test_fs)
#define BOOT_COUNT_FILE (&opencfw_boot_test_boot_count_file)
#define BOOT_READY (&opencfw_boot_test_ready)
#else
#define BOOT_FS ((lfs_t *)(uintptr_t)0x20026878u)
#define BOOT_COUNT_FILE ((lfs_file_t *)(uintptr_t)0x20026c0cu)
#define BOOT_READY ((volatile uint32_t *)(uintptr_t)0x2002711cu)
#endif

static const char *const boot_directories[4] = {
    "/firmware", "/ota", "/user", "/log"
};
static const char boot_count_path[] = "boot_count";

static int ensure_directories(lfs_t *fs) {
    for (unsigned i = 0; i != 4; ++i) {
        lfs_dir_t directory;
        int status = lfs_dir_open(fs, &directory, boot_directories[i]);
        if (status == 0) {
            (void)lfs_dir_close(fs, &directory);
            opencfw_boot_fs_error(0x0043394cu, boot_directories[i]);
            continue;
        }
        if (status != LFS_ERR_NOENT) {
            opencfw_boot_fs_error(0x00433340u, boot_directories[i], status);
            return -1;
        }
        status = lfs_mkdir(fs, boot_directories[i]);
        if (status == 0) {
            opencfw_boot_fs_error(0x00433934u, boot_directories[i]);
        } else if (status == LFS_ERR_EXIST) {
            opencfw_boot_fs_error(0x00433320u, boot_directories[i]);
        } else {
            opencfw_boot_fs_error(0x00432fdcu, boot_directories[i], status);
        }
    }
    return 0;
}

static int format_recover(lfs_t *fs) {
    (void)lfs_unmount(fs);
    (void)lfs_format(fs, &opencfw_boot_lfs_config);
    int status = lfs_mount(fs, &opencfw_boot_lfs_config);
    if (status != 0) {
        opencfw_boot_fs_error(0x0043397cu, status);
        return 9;
    }
    if (ensure_directories(fs) != 0) {
        opencfw_boot_fs_error(0x0043178cu);
        return 9;
    }
    return 0;
}

static void update_boot_count(lfs_t *fs) {
    /* The stock object is a static 92-byte lfs_file_t at 0x20026c0c. */
    lfs_file_t *file = BOOT_COUNT_FILE;
    uint32_t count = 0;
    (void)lfs_file_open(fs, file, boot_count_path, 0x103);
    (void)lfs_file_read(fs, file, &count, sizeof(count));
    ++count;
    (void)lfs_file_seek(fs, file, 0, LFS_SEEK_SET);
    (void)lfs_file_write(fs, file, &count, sizeof(count));
    (void)lfs_file_close(fs, file);
    opencfw_boot_fs_error(0x00433e48u, count);
}

uint32_t opencfw_provider_421210(void) {
    lfs_t *fs = BOOT_FS;
    int status = lfs_mount(fs, &opencfw_boot_lfs_config);
    if (status != 0) {
        (void)lfs_format(fs, &opencfw_boot_lfs_config);
        status = lfs_mount(fs, &opencfw_boot_lfs_config);
        if (status != 0) {
            opencfw_boot_fs_error(0x0043397cu, status);
            return 9;
        }
    }
    if (ensure_directories(fs) != 0) {
        opencfw_boot_fs_error(0x0043178cu);
        (void)format_recover(fs);
    }
    *BOOT_READY = 1;
    update_boot_count(fs);
    return 0;
}
