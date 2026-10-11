/* Minimal numerical port for pinned NationalChip base/src/crc32.c.
 * ARC/board/autoconf product configuration is neither required nor supplied.
 * This target is independently qualified C-SKY ELF32 little endian; upstream
 * common.h defines both 32-bit conversions as identity for this configuration.
 */
#ifndef OPENCFW_CODEC_CRC_COMMON_H
#define OPENCFW_CODEC_CRC_COMMON_H
#include <stddef.h>
#include <stdint.h>
#define cpu_to_le32(value) (value)
#define le32_to_cpu(value) (value)
#endif
