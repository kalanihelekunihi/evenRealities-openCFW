/* SPDX-License-Identifier: MIT
 * Stock NOR-write error at 0x420742 calls printf at 0x415fae. Source callers
 * pass the relocated format symbol; preserve all variadic words by tail branch.
 */
#include <stdint.h>

__attribute__((naked)) uint32_t opencfw_bl_transfer_error(
    const char *format, ...)
{
    __asm__ volatile(
        "b.w opencfw_provider_415fae\n"
    );
}
