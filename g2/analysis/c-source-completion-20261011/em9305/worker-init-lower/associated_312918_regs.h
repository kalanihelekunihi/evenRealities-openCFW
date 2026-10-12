#ifndef OPENCFW_ASSOCIATED_312918_REGS_H
#define OPENCFW_ASSOCIATED_312918_REGS_H
#include <stdint.h>

/* R2-R7 at entry, overwritten with their native exit projections. */
struct opencfw_associated_312918_regs {
    uint32_t r2, r3, r4, r5, r6, r7;
};

#endif
