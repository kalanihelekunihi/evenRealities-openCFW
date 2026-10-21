#ifndef R1_MEMORY_RUNTIME_ENDIAN_H
#define R1_MEMORY_RUNTIME_ENDIAN_H
/* Minimal freestanding bridge for the pinned memory source's endian tests.
 * Values come from the target compiler, not host headers. */
#define __LITTLE_ENDIAN __ORDER_LITTLE_ENDIAN__
#define __BIG_ENDIAN __ORDER_BIG_ENDIAN__
#define __BYTE_ORDER __BYTE_ORDER__
#if __BYTE_ORDER != __LITTLE_ENDIAN
#error R1 memory runtime targets little-endian Cortex-M4
#endif
#endif
