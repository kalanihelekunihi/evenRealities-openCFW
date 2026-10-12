/* SPDX-License-Identifier: MIT
 * Selected ABI-preserving adapter for platform bringup's seven direct calls
 * to stock formatter 0x415fae. The two binary64 formats were compared with
 * source output in six bounded cases. Stock vcvt.f32.f64 is modeled for
 * finite round-to-nearest inputs because Unicorn lacks that instruction;
 * full FPSCR, exceptional values and hardware behavior remain open.
 */
#include <stdint.h>

__attribute__((naked)) uint32_t opencfw_bl_generic_log(const char *format, ...)
{
    __asm__ volatile("b.w opencfw_provider_415fae");
}
