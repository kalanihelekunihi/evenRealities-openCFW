#include "ring_actions.h"
#include <assert.h>
#include <stdio.h>
int main(void) {
 const uint8_t types[]={1,2,0,5,4,8};
 const uint32_t expected[]={0,1,3,4,5,14};
 for(unsigned i=0;i<6;i++) {
  uint32_t event=99;uint8_t body[12];
  assert(g2_ring_type_to_input(types[i],&event)&&event==expected[i]);
  g2_app_input_body(body,4,event,7,9);
  printf("manager_to_app_packet_%u ",event);
  for(unsigned j=0;j<12;j++)printf("%02x",body[j]);
  puts("");
 }
 uint32_t event=99;
 assert(!g2_ring_type_to_input(255,&event)&&event==99);
 return 0;
}
