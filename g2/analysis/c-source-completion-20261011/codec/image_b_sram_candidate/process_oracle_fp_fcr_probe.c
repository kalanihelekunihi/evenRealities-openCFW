/* Oracle probe only: inspect the CK804EF FCR rounding field.  This is not a
 * selected firmware provider.  QEMU's FCR rounding model is incomplete. */
#include <stdint.h>
int __fe_getround(void)
{
    unsigned code=(__builtin_csky_getfcrsi()>>24)&3u;
    static const unsigned llvm_mode[4]={0u,3u,2u,1u};
    return (int)llvm_mode[code];
}
