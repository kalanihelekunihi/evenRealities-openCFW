/*
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * Bounded EFS non-reflected CRC-32C updater matched to stock entry
 * 0x0047CBC4.
 */

#define OPEN_CFW_EFS_CRC32C_MSB_POLYNOMIAL 0x1EDC6F41U

__attribute__((used, noinline))
void open_cfw_efs_crc32c_msb_update(
    const unsigned char *data,
    unsigned int size,
    unsigned int *state
)
{
    unsigned int crc = *state;
    unsigned int index;

#pragma clang loop unroll(disable)
    for (index = 0U; index < size; ++index) {
        unsigned int bit;

        crc ^= (unsigned int)data[index] << 24U;
#pragma clang loop unroll(disable)
        for (bit = 0U; bit < 8U; ++bit) {
            unsigned int high = crc >> 31U;

            crc <<= 1U;
            if (high != 0U) {
                crc ^= OPEN_CFW_EFS_CRC32C_MSB_POLYNOMIAL;
            }
        }
    }
    *state = crc;
}

#undef OPEN_CFW_EFS_CRC32C_MSB_POLYNOMIAL
