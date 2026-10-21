/* SPDX-License-Identifier: MIT */
#ifndef OPENCFW_ASSERT_H
#define OPENCFW_ASSERT_H
#ifdef OPENCFW_NATIVE_LFS_ASSERT
/* The retained LittleFS source has the same assertion line numbers as stock.
 * Stock passes condition, original source path, and line to SYS_WRITE0. */
void opencfw_boot_assert_report(const char *condition, const char *file,
                                unsigned line);
#define assert(x) ((x) ? (void)0 : opencfw_boot_assert_report(#x, \
    "D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\littlefs\\lfs.c", __LINE__))
#elif defined(NDEBUG)
#define assert(x) ((void)0)
#else
void opencfw_boot_assert_failure(void);
#define assert(x) ((x)?(void)0:opencfw_boot_assert_failure())
#endif
#endif
