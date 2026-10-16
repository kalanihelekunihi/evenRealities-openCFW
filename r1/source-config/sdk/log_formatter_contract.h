/* Native formatting uses ASCII printability, not a toolchain ctype table ABI. */
#include "logger_frontend_contract.h"
#include <ctype.h>
extern int r1_log_ascii_isprint(int value);
#undef isprint
#define isprint(value) r1_log_ascii_isprint(value)
