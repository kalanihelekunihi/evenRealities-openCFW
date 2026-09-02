/*
 * SPDX-License-Identifier: MIT
 *
 * Reviewable clean-room no-op callbacks authenticated at three G2
 * bootloader entry addresses. Each preserves all state and returns.
 */

#define OPEN_CFW_DEFINE_NOOP(name) \
    __attribute__((used, noinline, naked, visibility("default"))) \
    void name(void) \
    { \
        __asm volatile("bx lr\n"); \
    }

#if defined(__arm__) || defined(__thumb__)

OPEN_CFW_DEFINE_NOOP(open_cfw_bootloader_noop_callback_42dd98)
OPEN_CFW_DEFINE_NOOP(open_cfw_bootloader_noop_callback_42e276)
OPEN_CFW_DEFINE_NOOP(open_cfw_bootloader_noop_callback_42e39a)

#else

__attribute__((used, noinline, visibility("default")))
void open_cfw_bootloader_noop_callback_42dd98(void) {}

__attribute__((used, noinline, visibility("default")))
void open_cfw_bootloader_noop_callback_42e276(void) {}

__attribute__((used, noinline, visibility("default")))
void open_cfw_bootloader_noop_callback_42e39a(void) {}

#endif
