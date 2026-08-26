#include <stdint.h>
#include <stdlib.h>
#include <string.h>

unsigned char host_sec_state_storage[128];
static void *host_queue_items[3];
static uint8_t host_queue_handlers[3];
static void (*host_hci_callback)(const uint8_t *);
uint8_t host_sec_last_key[16],host_sec_last_text[16];
uint8_t host_sec_last_dh_x[32],host_sec_last_dh_y[32];
uint32_t host_sec_random_requests,host_sec_encrypt_requests,host_sec_public_requests,host_sec_dh_requests,host_sec_send_count,host_sec_free_count;
void *host_sec_last_sent;

static int queue_index(void *queue)
{
    uintptr_t base=(uintptr_t)host_sec_state_storage;
    uintptr_t offset=(uintptr_t)queue-base;
    if(offset==32U)return 0;if(offset==40U)return 1;if(offset==48U)return 2;return -1;
}

void host_sec_reset(void)
{
    memset(host_sec_state_storage,0,sizeof(host_sec_state_storage));memset(host_queue_items,0,sizeof(host_queue_items));
    memset(host_sec_last_key,0,16);memset(host_sec_last_text,0,16);memset(host_sec_last_dh_x,0,32);memset(host_sec_last_dh_y,0,32);
    host_sec_random_requests=host_sec_encrypt_requests=host_sec_public_requests=host_sec_dh_requests=host_sec_send_count=host_sec_free_count=0;host_sec_last_sent=NULL;host_hci_callback=NULL;
}
void host_sec_emit(const uint8_t *event){host_hci_callback(event);}
void *open_cfw_retained_cordio_sec_alloc(uint16_t n){return calloc(1,n);}
void open_cfw_retained_cordio_sec_free(void *p){++host_sec_free_count;free(p);}
void open_cfw_retained_cordio_sec_enqueue(void *q,uint8_t h,void *p){int i=queue_index(q);host_queue_items[i]=p;host_queue_handlers[i]=h;}
void *open_cfw_retained_cordio_sec_dequeue(void *q,uint8_t *h){int i=queue_index(q);void *p=host_queue_items[i];*h=host_queue_handlers[i];host_queue_items[i]=NULL;return p;}
void open_cfw_retained_cordio_sec_send(uint8_t h,void *p){(void)h;host_sec_last_sent=p;++host_sec_send_count;}
void *open_cfw_retained_cordio_sec_memcpy(void *d,const void *s,uint32_t n){return memcpy(d,s,n);}
void *open_cfw_retained_cordio_sec_memset(void *d,int v,uint32_t n){return memset(d,v,n);}
void open_cfw_retained_cordio_sec_reverse(uint8_t *p,uint32_t n){uint32_t i;for(i=0;i<n/2;i++){uint8_t x=p[i];p[i]=p[n-1-i];p[n-1-i]=x;}}
void open_cfw_retained_cordio_sec_reverse_copy(uint8_t *d,const uint8_t *s,uint32_t n){uint32_t i;for(i=0;i<n;i++)d[i]=s[n-1-i];}
void open_cfw_retained_cordio_sec_copy128(uint8_t *d,const uint8_t *s){memcpy(d,s,16);}
void open_cfw_retained_cordio_sec_xor128(uint8_t *d,const uint8_t *s){uint32_t i;for(i=0;i<16;i++)d[i]^=s[i];}
void open_cfw_retained_cordio_sec_hci_register(void (*f)(const uint8_t *)){host_hci_callback=f;}
void open_cfw_retained_cordio_sec_hci_random(void){++host_sec_random_requests;}
void open_cfw_retained_cordio_sec_hci_encrypt(const uint8_t *k,const uint8_t *t){memcpy(host_sec_last_key,k,16);memcpy(host_sec_last_text,t,16);++host_sec_encrypt_requests;}
void open_cfw_retained_cordio_sec_hci_public_key(void){++host_sec_public_requests;}
void open_cfw_retained_cordio_sec_hci_dh_key(const uint8_t *x,const uint8_t *y){memcpy(host_sec_last_dh_x,x,32);memcpy(host_sec_last_dh_y,y,32);++host_sec_dh_requests;}
