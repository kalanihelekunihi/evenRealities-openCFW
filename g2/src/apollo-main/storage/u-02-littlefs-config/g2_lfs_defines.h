/* Recovered littlefs v2.10.1 (0494ce71) build configuration for the G2
 * Apollo main image 2.2.6.10. Stock source: D:\01_workspace\s200_ap510b_iar_git\
 * third_party\littlefs\lfs.c, code 0x4CA6F8..0x4CFD02.
 *
 * Use with the pinned third-party/upstream/littlefs/lfs.c and lfs_util.c:
 *   -DLFS_DEFINES=g2_lfs_defines.h -DLFS_NO_INTRINSICS
 *   -I<this dir> -I<this dir>/include -I third-party/upstream/littlefs
 *   -I g2/src/apollo-bootloader/filesystem/freestanding_include
 *
 * Evidence (stock addresses):
 *  - lfs_malloc 0x4CA80A tail-calls file_heap_allocate 0x474CD2 and lfs_free
 *    0x4CA812 tail-calls file_heap_free 0x474D16 (mutex-guarded TLSF pool).
 *  - LFS_ERROR at 0x4CB222 (lfs_alloc, line 706) passes the stock literal
 *    "%s:%d:error: No more free space 0x%x%s\n" (ROM 0x74A5DC), the source
 *    path (ROM 0x70C264), 706, the block and "" to the printf body 0x4733EE.
 *  - LFS_ASSERT at 0x4CFAAC (lfs_file_open, line 6119) calls 0x4D09B4 with
 *    (expression text ROM 0x71F8A8, source path, line): IAR __aeabi_assert.
 *  - lfs_npw2/lfs_ctz/lfs_popc 0x4CA720..0x4CA7B2 are the portable bodies,
 *    i.e. LFS_NO_INTRINSICS (IAR is not __GNUC__).
 *  - Trace, LFS_THREADSAFE, LFS_MULTIVERSION, LFS_MIGRATE and LFS_READONLY
 *    are off; asserts and debug/warn/error output are on.
 *
 * The messages use the stock D:\ path rather than __FILE__ so that the
 * literal pool matches; line numbers come from the pinned lfs.c.
 */
#ifndef G2_LFS_DEFINES_H
#define G2_LFS_DEFINES_H

#include <stddef.h>

#define G2_LFS_SOURCE_PATH \
    "D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\littlefs\\lfs.c"

extern void *file_heap_allocate(size_t size); /* 0x474CD2 */
extern void file_heap_free(void *buffer);     /* 0x474D16 */
extern int printf(const char *format, ...);   /* 0x4733EE */
extern void __aeabi_assert(const char *expression, const char *file,
                           int line);         /* 0x4D09B4 */

#define LFS_MALLOC(size) file_heap_allocate(size)
#define LFS_FREE(pointer) file_heap_free(pointer)

#define LFS_DEBUG_(fmt, ...) \
    printf("%s:%d:debug: " fmt "%s\n", G2_LFS_SOURCE_PATH, __LINE__, __VA_ARGS__)
#define LFS_DEBUG(...) LFS_DEBUG_(__VA_ARGS__, "")
#define LFS_WARN_(fmt, ...) \
    printf("%s:%d:warn: " fmt "%s\n", G2_LFS_SOURCE_PATH, __LINE__, __VA_ARGS__)
#define LFS_WARN(...) LFS_WARN_(__VA_ARGS__, "")
#define LFS_ERROR_(fmt, ...) \
    printf("%s:%d:error: " fmt "%s\n", G2_LFS_SOURCE_PATH, __LINE__, __VA_ARGS__)
#define LFS_ERROR(...) LFS_ERROR_(__VA_ARGS__, "")

#define LFS_ASSERT(test) \
    ((test) ? (void)0 : __aeabi_assert(#test, G2_LFS_SOURCE_PATH, __LINE__))

#endif /* G2_LFS_DEFINES_H */
