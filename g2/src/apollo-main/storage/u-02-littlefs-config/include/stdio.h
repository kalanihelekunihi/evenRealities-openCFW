/* Freestanding stand-in for <stdio.h> as used by littlefs logging: only
 * printf, whose stock body is 0x4733EE. */
#ifndef G2_LFS_STDIO_H
#define G2_LFS_STDIO_H

extern int printf(const char *format, ...); /* 0x4733EE */

#endif /* G2_LFS_STDIO_H */
