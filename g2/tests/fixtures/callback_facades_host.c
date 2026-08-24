#include <stdint.h>
#include <string.h>
uint32_t open_cfw_test_charge_list;
uint32_t open_cfw_test_msg_list;
const char open_cfw_test_charge_type[]="BAT_INFO";
const char open_cfw_test_msg_type[]="MSG_COUNT";
static uint32_t words[20];
void open_cfw_test_callback_reset(void){uint32_t i;for(i=0;i<20;i++)words[i]=0;}
uint32_t open_cfw_test_callback_word(uint32_t i){return i<20?words[i]:0;}
void open_cfw_test_callback_set(uint32_t i,uint32_t v){if(i<20)words[i]=v;}
static uint32_t list_id(void *p){return p==&open_cfw_test_charge_list?1u:(p==&open_cfw_test_msg_list?2u:0u);}
void open_cfw_test_callback_init(void *l,const char*t){words[0]++;words[1]=list_id(l);words[2]=(uint32_t)(t&&strcmp(t,words[1]==1?"BAT_INFO":"MSG_COUNT")==0);}
void open_cfw_test_callback_deinit(void*l){words[3]++;words[4]=list_id(l);}
uint32_t open_cfw_test_callback_register(void*l,uintptr_t c){words[5]++;words[6]=list_id(l);words[7]=(uint32_t)c;return words[8];}
void open_cfw_test_callback_unregister(void*l,uintptr_t c){words[9]++;words[10]=list_id(l);words[11]=(uint32_t)c;}
void open_cfw_test_callback_notify(void*l,uint32_t e,uint32_t*v){words[12]++;words[13]=list_id(l);words[14]=e;words[15]=*v;*v+=words[16];}
