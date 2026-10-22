/* SPDX-License-Identifier: MIT
 * Freestanding <inttypes.h> for pinned upstream units in the G2 Apollo main
 * image. IAR ARM uses int for int32_t, so the PRI*32 strings carry no 'l':
 * stock literals "%s:%d:error: No more free space 0x%x%s\n" (ROM 0x74A5DC,
 * littlefs PRIx32) and "Error: Read the KV (%.*s@0x%08X) CRC32 check
 * failed!\n" (ROM 0x71F3A0, FlashDB PRIX32).
 */
#ifndef G2_UPSTREAM_LIBC_INTTYPES_H
#define G2_UPSTREAM_LIBC_INTTYPES_H
#include <stdint.h>
#define PRId8 "d"
#define PRIi8 "i"
#define PRIu8 "u"
#define PRIx8 "x"
#define PRIX8 "X"
#define PRId16 "d"
#define PRIi16 "i"
#define PRIu16 "u"
#define PRIx16 "x"
#define PRIX16 "X"
#define PRId32 "d"
#define PRIi32 "i"
#define PRIu32 "u"
#define PRIx32 "x"
#define PRIX32 "X"
#define PRId64 "lld"
#define PRIi64 "lli"
#define PRIu64 "llu"
#define PRIx64 "llx"
#define PRIX64 "llX"
#define PRIdLEAST16 "d"
#define PRIuLEAST16 "u"
#define PRIdLEAST32 "d"
#define PRIuLEAST32 "u"
#define PRIdMAX "lld"
#define PRIuMAX "llu"
#define PRIdPTR "d"
#define PRIuPTR "u"
#define PRIxPTR "x"
#endif
