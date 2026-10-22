/* SPDX-License-Identifier: MIT
 * Freestanding <assert.h> for pinned upstream units in the G2 Apollo main
 * image (littlefs, TLSF, FlashDB, nanopb, cJSON, LZ4, TinyFrame,
 * Ring-Buffer). Stock IAR DLIB assert calls __aeabi_assert 0x4D09B4 with
 * (expression text, source path, line); see the call at 0x4CFE38. The
 * stock path literal is the IAR build path, so a profile may set
 * G2_ASSERT_FILE to it (Ring-Buffer: ROM 0x6FC92C) instead of __FILE__.
 */
#ifndef G2_UPSTREAM_LIBC_ASSERT_H
#define G2_UPSTREAM_LIBC_ASSERT_H
void __aeabi_assert(const char *expression, const char *file, int line);
#ifdef NDEBUG
#define assert(x) ((void)0)
#else
#ifndef G2_ASSERT_FILE
#define G2_ASSERT_FILE __FILE__
#endif
#define assert(x) ((x) ? (void)0 : __aeabi_assert(#x, G2_ASSERT_FILE, __LINE__))
#endif
#endif
