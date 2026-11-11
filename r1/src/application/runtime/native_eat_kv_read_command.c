/* Stock 0x4f3a0: EAT named NV-record slice diagnostic. */
#include <stdint.h>

extern int32_t r1_native_sscanf(const char *input,const char *format,...);
extern uint32_t r1_factory_read_lookup(const char *name,void *destination,
                                        uint32_t offset,uint32_t length);
extern int32_t r1_native_snprintf(char *output,uint32_t capacity,const char *format,...);
extern void r1_eat_respond_format(const char *format,...);

void r1_eat_callback_0004f3a0(char *argument)
{
 char name[16];
 uint16_t length=0u,offset=0u;
 if(r1_native_sscanf(argument,"%9[^,],%hu,%hu",name,&offset,&length)!=3){
  r1_eat_respond_format(
   "ERROR: Invalid parameter format. Use: AT^KV_READ=name,offset,length\r\n");
  return;
 }
 if(length==0u||length>16u){
  r1_eat_respond_format("ERROR: Invalid length (must be 1-16)\r\n");
  return;
 }
 uint8_t bytes[16]={0};
 const uint32_t status=r1_factory_read_lookup(name,bytes,offset,length);
 if(status){
  r1_eat_respond_format("ERROR: Read failed, status=%d\r\n",status);
  return;
 }
 char hex[64]={0};
 uint16_t used=0u;
 for(uint16_t i=0u;i<length;++i){
  int32_t written=r1_native_snprintf(hex+used,64u-used,"%02X ",bytes[i]);
  if(written>0)used=(uint16_t)(used+(uint32_t)written);
 }
 r1_eat_respond_format("[%s]: %s\r\n",name,hex);
}
