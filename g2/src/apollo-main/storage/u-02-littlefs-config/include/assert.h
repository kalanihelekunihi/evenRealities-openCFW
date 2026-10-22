/* Freestanding stand-in for the IAR DLIB <assert.h> seen by the stock
 * littlefs build: assert(e) reports through __aeabi_assert 0x4D09B4. */
#ifndef G2_LFS_ASSERT_H
#define G2_LFS_ASSERT_H

extern void __aeabi_assert(const char *expression, const char *file,
                           int line); /* 0x4D09B4 */

#define assert(e) ((e) ? (void)0 : __aeabi_assert(#e, __FILE__, __LINE__))

#endif /* G2_LFS_ASSERT_H */
