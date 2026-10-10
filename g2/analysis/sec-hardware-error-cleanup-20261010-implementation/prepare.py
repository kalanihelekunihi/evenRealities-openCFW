from pathlib import Path
import json,hashlib
D=Path(__file__).parent;R=next(p for p in D.resolve().parents if (p/'g2/blobs').exists());raw=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes();sha=lambda x:hashlib.sha256(x).hexdigest();assert sha(raw)=='36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863';rows=[]
for a,b,n in [(0x536234,0x536324,'callback'),(0x4bf9ec,0x4bfa00,'message-dequeue'),(0x4bf9b0,0x4bf9ba,'message-free'),(0x538c4a,0x538c6e,'queue-dequeue')]:
 x=raw[a-0x437fe0:b-0x437fe0];(D/(n+'.bin')).write_bytes(x);rows.append(dict(name=n,start=hex(a),end=hex(b),file_offset=hex(a-0x437fe0),sha256=sha(x)))
assert int.from_bytes(raw[0x5363e8-0x437fe0:0x5363ec-0x437fe0],'little')==0x20072cb8
(D/'original-receipts.json').write_text(json.dumps(rows,indent=2)+'\n')
pre=r'''#include <stdint.h>
#include <stddef.h>
#include <string.h>
#include <stdlib.h>
typedef uint8_t wsfHandlerId_t;
typedef struct {uint16_t param;uint8_t event,status;} Header;
typedef struct {Header hdr;struct{uint8_t randNum[8];}leRandCmdCmpl;struct{uint8_t data[16];}leEncryptCmdCmpl;} hciEvt_t;
typedef struct {uint32_t id;uint8_t type;} secQueueBuf_t;
typedef struct {secQueueBuf_t nodes[8];uint32_t n,pos,id;} Queue;
static struct {uint8_t rand[32],randTop;Queue pubKeyQueue,dhKeyQueue,aesEncQueue;void(*hciCbackTbl[8])(secQueueBuf_t*,hciEvt_t*,wsfHandlerId_t);}secCb;
static uint32_t events[128],count;
#define HCI_LE_RAND_CMD_CMPL_CBACK_EVT 28
#define HCI_LE_ENCRYPT_CMD_CMPL_CBACK_EVT 27
#define HCI_LE_READ_LOCAL_P256_PUB_KEY_CMPL_CBACK_EVT 37
#define HCI_LE_GENERATE_DHKEY_CMPL_CBACK_EVT 38
#define HCI_HW_ERROR_CBACK_EVT 20
#define HCI_RAND_LEN 8
#define SEC_HCI_RAND_MULT 4
#define SEC_TYPE_CCM 3
#define SEC_TYPE_CMAC 1
#define SEC_TYPE_AES_REV 4
#define HCI_ENCRYPT_DATA_LEN 16
#define WSF_ASSERT(x) do{if(!(x))abort();}while(0)
static void WStrReverse(void*p,uint32_t n){abort();}
static void*WsfMsgDeq(Queue*q,wsfHandlerId_t*h){events[count++]=100+q->id;if(q->pos==q->n)return NULL;secQueueBuf_t*p=&q->nodes[q->pos++];*h=p->id;return p;}
static void WsfMsgFree(secQueueBuf_t*p){events[count++]=200+p->id;}
static void cb(secQueueBuf_t*p,hciEvt_t*e,wsfHandlerId_t h){events[count++]=900;}
'''
post=r'''
void test(uint32_t p,uint32_t d,uint32_t a){memset(&secCb,0,sizeof(secCb));count=0;Queue*qs[]={&secCb.pubKeyQueue,&secCb.dhKeyQueue,&secCb.aesEncQueue};uint32_t ns[]={p,d,a};for(uint32_t i=0;i<3;i++){qs[i]->id=i;qs[i]->n=ns[i];for(uint32_t k=0;k<ns[i];k++){qs[i]->nodes[k].id=i*10+k;qs[i]->nodes[k].type=0;} }for(uint32_t i=0;i<8;i++)secCb.hciCbackTbl[i]=cb;hciEvt_t evt={0};evt.hdr.event=20;secHciCback(&evt);}
uint32_t event_count(void){return count;}uint32_t event_at(uint32_t i){return events[i];}uint32_t remaining(uint32_t i){Queue*qs[]={&secCb.pubKeyQueue,&secCb.dhKeyQueue,&secCb.aesEncQueue};return qs[i]->n-qs[i]->pos;}
'''
bodies={}
for name in ['sdk','public']:
 t=(D/(name+'-sec_main.c')).read_text();a=t.index('static void secHciCback(');i=t.index('{',a);depth=0
 while i<len(t):
  depth+=(t[i]=='{')-(t[i]=='}');i+=1
  if depth==0:break
 body=t[a:i];bodies[name]=dict(file_sha256=sha((D/(name+'-sec_main.c')).read_bytes()),body_sha256=sha(body.encode()));(D/(name+'-projection.c')).write_text(pre+body+post)
(D/'source-body-receipts.json').write_text(json.dumps(bodies,indent=2)+'\n');print(rows[0])
