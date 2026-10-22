/* SPDX-License-Identifier: MIT
 * Freestanding <time.h> for pinned upstream units in the G2 Apollo main
 * image. FlashDB's flashdb.h only needs time_t for fdb_time_t (TSDB is not
 * built); IAR DLIB's default time_t is 32-bit.
 */
#ifndef G2_UPSTREAM_LIBC_TIME_H
#define G2_UPSTREAM_LIBC_TIME_H
#include <stdint.h>
typedef int32_t time_t;
#endif
