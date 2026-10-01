#include "ring_tx_budget.h"
#include <assert.h>
#include <stdio.h>
int main(void) {
 const unsigned lengths[]={0,8,9,12,13,40,41,44,45,456,457,460,461};
 for(unsigned h=12;h<=16;h+=4)for(unsigned i=0;i<sizeof(lengths)/sizeof(*lengths);i++) {
  unsigned cls=0;bool ok=g2_ring_inline_budget(lengths[i],h,65535,&cls);
  printf("inline_h%u_payload%u %u\n",h,lengths[i],ok?cls:0);
 }
 assert(g2_ring_inline_budget(20,12,23,NULL));
 assert(!g2_ring_inline_budget(21,12,23,NULL));
 assert(!g2_ring_inline_budget(SIZE_MAX,12,65535,NULL));
 assert(!g2_ring_inline_budget(1,SIZE_MAX,65535,NULL));
 assert(!g2_ring_inline_budget(0,12,2,NULL));
 assert(!g2_wsf_message_class(65528));
 return 0;
}
