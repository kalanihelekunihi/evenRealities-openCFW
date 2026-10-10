/*
 * Production-excluded G2 configuration recovered from official firmware.
 * SPDX-License-Identifier: Apache-2.0
 */

#ifndef OPENCFW_G2_FDB_CFG_H
#define OPENCFW_G2_FDB_CFG_H

#define FDB_USING_KVDB
#define FDB_USING_FAL_MODE
#define FDB_WRITE_GRAN 1
#define FDB_KV_CACHE_TABLE_SIZE 64
#define FDB_SECTOR_CACHE_TABLE_SIZE 64

/*
 * Omitted from this minimal recovered build because no live/retained TSDB
 * subsystem is present. The original FDB_USING_TSDB macro state is not
 * statically proven: linker garbage collection could discard TSDB code.
 *
 * Statically recovered as absent from the retained behavior:
 *   FDB_USING_FILE_LIBC_MODE
 *   FDB_USING_FILE_POSIX_MODE
 *   FDB_KV_AUTO_UPDATE
 *   FDB_DEBUG_ENABLE
 *
 * The eventual target build must also use the 32-bit, short-enum ABI and
 * supply source-owned FDB_PRINT, FDB_ASSERT, FAL table, and norflash seams.
 */

#endif /* OPENCFW_G2_FDB_CFG_H */
