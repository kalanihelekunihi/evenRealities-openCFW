/* Public allocation extent for the native R1 task backend.
 * Upstream keeps StaticTask_t opaque. Its configured generic layout is not
 * the native 112-byte TCB, whose extra fields are recovered separately. */
#ifndef R1_NATIVE_FREERTOS_PUBLIC_H
#define R1_NATIVE_FREERTOS_PUBLIC_H
#define StaticTask_t R1UpstreamStaticTask_t
#include "../../../../third-party/upstream/freertos-kernel/include/FreeRTOS.h"
#undef StaticTask_t
/* Word-aligned storage only; this does not give upstream field semantics to
 * the native stack-depth, task-number, notification or allocation extensions. */
typedef struct { uint32_t native_storage[28]; } StaticTask_t;
_Static_assert(sizeof(StaticTask_t)==112, "native task allocation extent");
_Static_assert(_Alignof(StaticTask_t)==4, "native task allocation alignment");
_Static_assert(sizeof(R1UpstreamStaticTask_t)<=sizeof(StaticTask_t),
               "generic candidate must not exceed native reservation");
#endif
