/* Native buffer_add recursively inserts CR before every LF; no double formats. */
#include "sdk_common.h"
#undef NRF_ASSERT_PRESENT
#define NRF_ASSERT_PRESENT 0
#undef NRF_FPRINTF_FLAG_AUTOMATIC_CR_ON_LF_ENABLED
#define NRF_FPRINTF_FLAG_AUTOMATIC_CR_ON_LF_ENABLED 1
#undef NRF_FPRINTF_DOUBLE_ENABLED
#define NRF_FPRINTF_DOUBLE_ENABLED 0
