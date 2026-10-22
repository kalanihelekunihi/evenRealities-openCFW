/* SPDX-License-Identifier: MIT
 * Freestanding <ctype.h> for pinned upstream units in the G2 Apollo main
 * image (cJSON case_insensitive_strcmp).
 */
#ifndef G2_UPSTREAM_LIBC_CTYPE_H
#define G2_UPSTREAM_LIBC_CTYPE_H
int tolower(int c);
int toupper(int c);
int isdigit(int c);
int isspace(int c);
#endif
