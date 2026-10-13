/* Destination 2, selected commands, logging disabled at entry. Child calls are boundaries. */
#include <stdint.h>
extern void case_send(const uint8_t*,uint32_t),case_ack(uint32_t);
extern void case_control_a(uint32_t),case_control_b(uint32_t);
void case_local_selected(const uint8_t *p,uint32_t n,uint32_t mode){
 (void)mode;uint8_t reply[7];
 switch(p[0]){
 case 0x50:{const uint8_t bytes[7]={0x50,1,3,3,1,2,0x39};for(int i=0;i<7;i++)reply[i]=bytes[i];case_send(reply,7);break;}
 case 0x5c:reply[0]=0x5c;reply[1]=1;reply[2]=3;reply[3]=1;reply[4]=!*(uint8_t*)0x20000880u;case_send(reply,5);break;
 case 0x5d:if(n>=6){if(p[4])case_control_a(!p[5]);else case_control_b(!p[5]);case_ack(0x5d);}break;
 case 0x68:if(n>=5){*(uint8_t*)0x200000bfu=!!p[4];case_ack(0x68);}break;
 }
}
