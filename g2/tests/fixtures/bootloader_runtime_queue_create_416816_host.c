/* SPDX-License-Identifier: GPL-3.0-or-later */
#include <stdint.h>
static uintptr_t critical_value,result_value,static_calls,dynamic_calls,observed_count,observed_size,observed_messages,observed_control,observed_kind;
static uintptr_t critical(void){return critical_value;}
static uintptr_t make_static(uintptr_t c,uintptr_t s,uintptr_t m,uintptr_t x,uintptr_t k){static_calls++;observed_count=c;observed_size=s;observed_messages=m;observed_control=x;observed_kind=k;return result_value;}
static uintptr_t make_dynamic(uintptr_t c,uintptr_t s,uintptr_t k){dynamic_calls++;observed_count=c;observed_size=s;observed_kind=k;return result_value;}
#define OPEN_CFW_BOOTLOADER_CRITICAL_CONTEXT() critical()
#define OPEN_CFW_BOOTLOADER_RUNTIME_QUEUE_STATIC_419C9C(c,s,m,x,k) make_static((c),(s),(m),(x),(k))
#define OPEN_CFW_BOOTLOADER_RUNTIME_QUEUE_DYNAMIC_419D08(c,s,k) make_dynamic((c),(s),(k))
#include "../../components/bootloader/core_overlay/runtime_queue_create_416816.c"
void open_cfw_test_queue_reset(uintptr_t c,uintptr_t r){critical_value=c;result_value=r;static_calls=dynamic_calls=observed_count=observed_size=observed_messages=observed_control=observed_kind=0;}
#define G(n) uintptr_t open_cfw_test_queue_##n(void){return n;}
G(static_calls) G(dynamic_calls) G(observed_count) G(observed_size) G(observed_messages) G(observed_control) G(observed_kind)
