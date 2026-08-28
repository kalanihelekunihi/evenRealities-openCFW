/* SPDX-License-Identifier: MIT */

typedef __UINTPTR_TYPE__ open_cfw_bootloader_word;

#ifndef OPEN_CFW_BOOTLOADER_CRITICAL_CONTEXT
extern open_cfw_bootloader_word open_cfw_bootloader_critical_context(void);
#define OPEN_CFW_BOOTLOADER_CRITICAL_CONTEXT() \
    open_cfw_bootloader_critical_context()
#endif

#ifndef OPEN_CFW_BOOTLOADER_RUNTIME_HANDLE_RELEASE_TAGGED_419DE2
extern open_cfw_bootloader_word open_cfw_bootloader_runtime_handle_release_tagged_419de2(
    open_cfw_bootloader_word object
);
#define OPEN_CFW_BOOTLOADER_RUNTIME_HANDLE_RELEASE_TAGGED_419DE2(object) \
    open_cfw_bootloader_runtime_handle_release_tagged_419de2(object)
#endif

#ifndef OPEN_CFW_BOOTLOADER_RUNTIME_HANDLE_RELEASE_PLAIN_419EC0
extern open_cfw_bootloader_word open_cfw_bootloader_runtime_handle_release_plain_419ec0(
    open_cfw_bootloader_word object,
    open_cfw_bootloader_word first,
    open_cfw_bootloader_word second,
    open_cfw_bootloader_word third
);
#define OPEN_CFW_BOOTLOADER_RUNTIME_HANDLE_RELEASE_PLAIN_419EC0(object, first, second, third) \
    open_cfw_bootloader_runtime_handle_release_plain_419ec0(object, first, second, third)
#endif

__attribute__((used, noinline))
open_cfw_bootloader_word open_cfw_bootloader_runtime_handle_release_416710(
    open_cfw_bootloader_word tagged_object
)
{
    open_cfw_bootloader_word object = tagged_object & ~(open_cfw_bootloader_word)1U;
    open_cfw_bootloader_word tagged = tagged_object & 1U;
    open_cfw_bootloader_word result;

    if (OPEN_CFW_BOOTLOADER_CRITICAL_CONTEXT() != 0U) {
        return (open_cfw_bootloader_word)-6;
    }
    if (object == 0U) {
        return (open_cfw_bootloader_word)-4;
    }
    result = tagged != 0U
        ? OPEN_CFW_BOOTLOADER_RUNTIME_HANDLE_RELEASE_TAGGED_419DE2(object)
        : OPEN_CFW_BOOTLOADER_RUNTIME_HANDLE_RELEASE_PLAIN_419EC0(object, 0U, 0U, 0U);
    return result == 1U ? 0U : (open_cfw_bootloader_word)-3;
}
