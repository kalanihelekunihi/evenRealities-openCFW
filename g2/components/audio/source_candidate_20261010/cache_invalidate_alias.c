/* Stock 0x475014 is the source-backed cache invalidate body. */
#include "../../foundation/cache_maintenance/cache_maintenance.c"

/* The audio caller passes R0=0, R1=1 and ignores the returned R0. */
__asm__(".global stock_bus_flush\n"
        ".set stock_bus_flush, opencfw_cache_invalidate\n");
