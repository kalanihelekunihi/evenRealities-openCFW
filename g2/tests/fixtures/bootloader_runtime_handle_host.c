/* SPDX-License-Identifier: GPL-3.0-or-later */

#include <stdint.h>

static uintptr_t critical_value;
static uintptr_t tagged_result;
static uintptr_t plain_result;
static uintptr_t tagged_calls;
static uintptr_t plain_calls;
static uintptr_t observed_object;
static uintptr_t observed_timeout;
static uintptr_t observed_zero_arguments;

static uintptr_t test_critical(void) { return critical_value; }
static uintptr_t test_acquire_tagged(uintptr_t object, uintptr_t timeout) {
    tagged_calls++; observed_object = object; observed_timeout = timeout; return tagged_result;
}
static uintptr_t test_acquire_plain(uintptr_t object, uintptr_t timeout) {
    plain_calls++; observed_object = object; observed_timeout = timeout; return plain_result;
}
static uintptr_t test_release_tagged(uintptr_t object) {
    tagged_calls++; observed_object = object; return tagged_result;
}
static uintptr_t test_release_plain(uintptr_t object, uintptr_t a, uintptr_t b, uintptr_t c) {
    plain_calls++; observed_object = object; observed_zero_arguments = a | b | c; return plain_result;
}

#define OPEN_CFW_BOOTLOADER_CRITICAL_CONTEXT() test_critical()
#define OPEN_CFW_BOOTLOADER_RUNTIME_HANDLE_ACQUIRE_TAGGED_419E22(object, timeout) test_acquire_tagged((object), (timeout))
#define OPEN_CFW_BOOTLOADER_RUNTIME_HANDLE_ACQUIRE_PLAIN_41A24E(object, timeout) test_acquire_plain((object), (timeout))
#define OPEN_CFW_BOOTLOADER_RUNTIME_HANDLE_RELEASE_TAGGED_419DE2(object) test_release_tagged((object))
#define OPEN_CFW_BOOTLOADER_RUNTIME_HANDLE_RELEASE_PLAIN_419EC0(object, a, b, c) test_release_plain((object), (a), (b), (c))
#include "../../components/bootloader/core_overlay/runtime_handle_acquire_4166aa.c"
#include "../../components/bootloader/core_overlay/runtime_handle_release_416710.c"

void open_cfw_test_handle_reset(uintptr_t critical, uintptr_t tagged, uintptr_t plain) {
    critical_value = critical; tagged_result = tagged; plain_result = plain;
    tagged_calls = 0; plain_calls = 0; observed_object = 0; observed_timeout = 0;
    observed_zero_arguments = 0;
}
uintptr_t open_cfw_test_handle_tagged_calls(void) { return tagged_calls; }
uintptr_t open_cfw_test_handle_plain_calls(void) { return plain_calls; }
uintptr_t open_cfw_test_handle_object(void) { return observed_object; }
uintptr_t open_cfw_test_handle_timeout(void) { return observed_timeout; }
uintptr_t open_cfw_test_handle_zero_arguments(void) { return observed_zero_arguments; }
