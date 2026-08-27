/* SPDX-License-Identifier: GPL-3.0-or-later */
#include <stdint.h>
static uintptr_t critical_value, backend_result, release_result;
static uintptr_t binary_static_calls, binary_dynamic_calls, count_static_calls, count_dynamic_calls, release_calls, delete_calls;
static uintptr_t observed_maximum, observed_initial, observed_storage, observed_kind, observed_zero_arguments;
static uintptr_t critical(void){return critical_value;}
static uintptr_t binary_static(uintptr_t l,uintptr_t i,uintptr_t b,uintptr_t s,uintptr_t k){binary_static_calls++;observed_maximum=l;observed_initial=i;observed_zero_arguments=b;observed_storage=s;observed_kind=k;return backend_result;}
static uintptr_t binary_dynamic(uintptr_t l,uintptr_t i,uintptr_t k){binary_dynamic_calls++;observed_maximum=l;observed_initial=i;observed_kind=k;return backend_result;}
static uintptr_t count_static(uintptr_t m,uintptr_t i,uintptr_t s){count_static_calls++;observed_maximum=m;observed_initial=i;observed_storage=s;return backend_result;}
static uintptr_t count_dynamic(uintptr_t m,uintptr_t i){count_dynamic_calls++;observed_maximum=m;observed_initial=i;return backend_result;}
static uintptr_t release_plain(uintptr_t o,uintptr_t a,uintptr_t b,uintptr_t c){release_calls++;observed_storage=o;observed_zero_arguments=a|b|c;return release_result;}
static void delete_object(uintptr_t o){delete_calls++;observed_storage=o;}
#define OPEN_CFW_BOOTLOADER_CRITICAL_CONTEXT() critical()
#define OPEN_CFW_BOOTLOADER_RUNTIME_BINARY_STATIC_419C9C(l,i,b,s,k) binary_static((l),(i),(b),(s),(k))
#define OPEN_CFW_BOOTLOADER_RUNTIME_BINARY_DYNAMIC_419D08(l,i,k) binary_dynamic((l),(i),(k))
#define OPEN_CFW_BOOTLOADER_RUNTIME_SEMAPHORE_STATIC_419E62(m,i,s) count_static((m),(i),(s))
#define OPEN_CFW_BOOTLOADER_RUNTIME_SEMAPHORE_DYNAMIC_419E94(m,i) count_dynamic((m),(i))
#define OPEN_CFW_BOOTLOADER_RUNTIME_HANDLE_RELEASE_PLAIN_419EC0(o,a,b,c) release_plain((o),(a),(b),(c))
#define OPEN_CFW_BOOTLOADER_RUNTIME_SEMAPHORE_DELETE_41A470(o) delete_object((o))
#include "../../components/bootloader/core_overlay/runtime_semaphore_create_416762.c"
void open_cfw_test_semaphore_reset(uintptr_t c,uintptr_t r,uintptr_t g){critical_value=c;backend_result=r;release_result=g;binary_static_calls=binary_dynamic_calls=count_static_calls=count_dynamic_calls=release_calls=delete_calls=0;observed_maximum=observed_initial=observed_storage=observed_kind=observed_zero_arguments=0;}
#define GETTER(n) uintptr_t open_cfw_test_semaphore_##n(void){return n;}
GETTER(binary_static_calls) GETTER(binary_dynamic_calls) GETTER(count_static_calls) GETTER(count_dynamic_calls) GETTER(release_calls) GETTER(delete_calls) GETTER(observed_maximum) GETTER(observed_initial) GETTER(observed_storage) GETTER(observed_kind) GETTER(observed_zero_arguments)
