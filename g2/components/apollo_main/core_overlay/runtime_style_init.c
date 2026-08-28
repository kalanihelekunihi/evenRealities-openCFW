/*
 * SPDX-License-Identifier: MIT
 *
 * Bounded source replacement for the G2 2.2.6.10 style initializer at
 * 0x0048278C...0x00482795. The stock routine initializes the complete
 * 12-byte style/map descriptor to zero.
 *
 * All three direct callers discard the stock epilogue's incidental saved-r7
 * value, and complete branch/pointer scans find no alternate entry, so this
 * initializer exposes its semantic void ABI.
 */

#ifndef OPEN_CFW_RUNTIME_STYLE_INIT_MEMORY_ZERO
void *open_cfw_runtime_memory_zero(void *destination, unsigned int size);
#define OPEN_CFW_RUNTIME_STYLE_INIT_MEMORY_ZERO(destination, size) \
    open_cfw_runtime_memory_zero((destination), (size))
#endif

__attribute__((used, noinline))
void open_cfw_runtime_style_init(void *style)
{
    OPEN_CFW_RUNTIME_STYLE_INIT_MEMORY_ZERO(style, 12U);
}

#undef OPEN_CFW_RUNTIME_STYLE_INIT_MEMORY_ZERO
