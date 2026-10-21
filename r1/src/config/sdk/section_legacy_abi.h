/* Cache compiler abstractions as Clang/GCC, then select only the SDK's
 * non-GNU multi-range section ABI. Iterator implementation keeps the selector
 * off for its two body branches; other translation units restore it here. */
#include "sdk_common.h"
#include "nrf_section.h"
#include "app_util.h"
#pragma push_macro("__GNUC__")
#undef __GNUC__
#include "nrf_section_iter.h"
#ifndef R1_SECTION_ITERATOR_IMPLEMENTATION
#pragma pop_macro("__GNUC__")
#endif
_Static_assert(sizeof(nrf_section_set_t)==12,"stock multi-range set");
_Static_assert(sizeof(nrf_section_iter_t)==12,"stock multi-range cursor");
