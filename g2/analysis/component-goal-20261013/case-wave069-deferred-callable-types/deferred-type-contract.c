#include <stdint.h>
extern void vEventGroupSetBitsCallback(void *,uint32_t);
extern void vEventGroupClearBitsCallback(void *,uint32_t);
_Static_assert(__builtin_types_compatible_p(__typeof__(&vEventGroupSetBitsCallback),void (*)(void *,uint32_t)), "set callback");
_Static_assert(__builtin_types_compatible_p(__typeof__(&vEventGroupClearBitsCallback),void (*)(void *,uint32_t)), "clear callback");
_Static_assert(!__builtin_types_compatible_p(void (*)(uint32_t,uint32_t),void (*)(void *,uint32_t)), "original callback type differs");
_Static_assert(sizeof(void *)==4 && sizeof(uint32_t)==4, "pinned word ABI");
