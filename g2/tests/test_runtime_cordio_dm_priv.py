import subprocess,tempfile,textwrap,unittest
from pathlib import Path
R=Path(__file__).resolve().parents[1];D=R/"components/shared/cordio";S=D/"runtime_cordio_dm_priv.c"
class T(unittest.TestCase):
 def test_privacy_behavior_and_all_target_profiles(self):
  h=textwrap.dedent(r'''
   #include <assert.h>
   #include <string.h>
   #include "runtime_cordio_dm_priv.h"
   static unsigned aes,rnd,add,rem,clear,seten,mode,peer,local,to,dev,send,locks,unlocks,calls;static uint8_t pool[128],cipher[16],last_event,last_status,last_enable;
   static void cb(void*p){struct open_cfw_cordio_dm_priv_header*h=p;calls++;last_event=h->event;last_status=h->status;}
   void open_cfw_cordio_security_aes(uint8_t*k,uint8_t*b,uint8_t h,uint16_t p,uint8_t e){aes++;assert(k&&b&&h==4&&(e==0x78||e==0x79));(void)p;}void open_cfw_cordio_security_random(uint8_t*p,uint8_t n){rnd++;while(n--)*p++=1;}
   void open_cfw_cordio_hci_add_resolving(uint8_t t,uint8_t*a,uint8_t*p,uint8_t*l){add++;assert(t==1&&a&&p&&l);}void open_cfw_cordio_hci_remove_resolving(uint8_t t,uint8_t*a){rem++;assert(t==1&&a);}void open_cfw_cordio_hci_clear_resolving(void){clear++;}void open_cfw_cordio_hci_set_address_resolution(uint8_t e){seten++;last_enable=e;}void open_cfw_cordio_hci_set_privacy_mode(uint8_t t,uint8_t*a,uint8_t m){mode++;assert(t==1&&a&&m==2);}void open_cfw_cordio_hci_read_peer_resolvable(uint8_t t,const uint8_t*a){peer++;assert(t==1&&a);}void open_cfw_cordio_hci_read_local_resolvable(uint8_t t,const uint8_t*a){local++;assert(t==1&&a);}void open_cfw_cordio_hci_set_rpa_timeout(uint16_t x){to++;assert(x==9);}
   void open_cfw_cordio_dm_device_pass_event_to_privacy(uint8_t e,uint8_t p,uint8_t a,uint8_t c){dev++;assert((e==0x0d||e==0x0c)&&p<2&&!a&&!c);}void*open_cfw_cordio_wsf_message_allocate(uint16_t n){assert(n<=sizeof(pool));memset(pool,0,sizeof(pool));return pool;}void open_cfw_cordio_wsf_message_send(uint8_t h,void*p){send++;assert(h==4&&p==pool);}void open_cfw_cordio_wsf_task_lock(void){locks++;}void open_cfw_cordio_wsf_task_unlock(void){unlocks++;}
   int main(void){union open_cfw_cordio_dm_priv_message m={0};uint8_t a[6]={1,2,3,4,5,6},k[16]={1};open_cfw_cordio_dm_priv_callback=cb;open_cfw_cordio_dm_priv_handler_id=4;
    m.header.parameter=7;memcpy(m.resolve.irk,k,16);memcpy(m.resolve.address,a,6);open_cfw_cordio_dm_privacy_action_resolve(&m);assert(aes==1&&(open_cfw_cordio_dm_priv_control.in_progress&1));open_cfw_cordio_dm_privacy_action_resolve(&m);assert(calls==1&&last_event==0x37&&last_status==7);
    memcpy(cipher,a,3);m.aes.ciphertext=cipher;open_cfw_cordio_dm_privacy_aes_resolve_complete(&m);assert(calls==2&&last_status==0&&!(open_cfw_cordio_dm_priv_control.in_progress&1));
    memset(&m,0,sizeof(m));memcpy(m.generate.irk,k,16);open_cfw_cordio_dm_privacy_action_generate(&m);assert(rnd==1&&aes==2&&(open_cfw_cordio_dm_priv_control.in_progress&2));m.aes.ciphertext=cipher;open_cfw_cordio_dm_privacy_aes_generate_complete(&m);assert(calls==3&&last_event==0x38&&m.raw[4]==1);
    memset(&m,0,sizeof(m));m.add.address_type=1;m.add.enable_ll_privacy=1;m.header.parameter=8;open_cfw_cordio_dm_privacy_action_add(&m);assert(add==1);m.remove.address_type=1;open_cfw_cordio_dm_privacy_action_remove(&m);open_cfw_cordio_dm_privacy_action_clear(&m);m.enable.enable=1;open_cfw_cordio_dm_privacy_action_enable(&m);m.mode.address_type=1;m.mode.mode=2;open_cfw_cordio_dm_privacy_action_mode(&m);assert(rem==1&&clear==1&&seten==1&&mode==1);
    m.header.event=21;m.header.status=0;open_cfw_cordio_dm_priv_ll_enabled=0;open_cfw_cordio_dm_privacy_hci_handler(&m.header);assert(m.header.event==0x3a&&seten==2);m.header.event=26;m.header.status=0;open_cfw_cordio_dm_privacy_hci_handler(&m.header);assert(open_cfw_cordio_dm_priv_ll_enabled==1&&dev==1);
    open_cfw_cordio_dm_privacy_initialize();assert(locks==1&&unlocks==1&&open_cfw_cordio_dm_priv_interfaces[6]==0x78a868&&open_cfw_cordio_dm_priv_interfaces[15]==0x78a874);
    open_cfw_cordio_dm_privacy_resolve(a,k,1);open_cfw_cordio_dm_privacy_add(1,a,k,k,1,2);open_cfw_cordio_dm_privacy_remove(1,a,3);open_cfw_cordio_dm_privacy_clear();open_cfw_cordio_dm_privacy_enable(1);open_cfw_cordio_dm_privacy_mode(1,a,2);open_cfw_cordio_dm_privacy_generate(k,4);assert(send==7);open_cfw_cordio_dm_privacy_read_peer(1,a);open_cfw_cordio_dm_privacy_read_local(1,a);open_cfw_cordio_dm_privacy_timeout(9);assert(peer==1&&local==1&&to==1);open_cfw_cordio_dm_privacy_reset();assert(!open_cfw_cordio_dm_priv_ll_enabled&&!open_cfw_cordio_dm_priv_control.in_progress);return 0;}
  ''')
  selectors=["RESOLVE_ACTION","RESOLVE_AES","ADD_ACTION","REMOVE_ACTION","CLEAR_ACTION","ENABLE_ACTION","MODE_ACTION","GENERATE_ACTION","GENERATE_AES","HCI","SET_ENABLE","MESSAGE","RESET","AES_MESSAGE","INIT","RESOLVE","ADD","REMOVE","CLEAR","ENABLE","MODE","READ_PEER","READ_LOCAL","TIMEOUT","GENERATE"]
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/"h.c";x=Path(d)/"x";p.write_text(h);subprocess.run(["cc","-std=c11","-Wall","-Wextra","-Werror","-I",str(D),str(S),str(p),"-o",str(x)],check=True);subprocess.run([str(x)],check=True)
   for q in [None,*selectors]:
    c=["clang","--target=thumbv7em-none-eabi","-mthumb","-mcpu=cortex-m55","-O2","-ffreestanding","-fno-builtin","-Wall","-Wextra","-Werror","-I",str(D),"-DOPEN_CFW_DM_PRIV_PRODUCTION=1"]
    if q:c.append(f"-DOPEN_CFW_DM_PRIV_{q}_ONLY=1")
    c += ["-c",str(S),"-o",str(Path(d)/f"{q or 'all'}.o")];subprocess.run(c,check=True)
if __name__=="__main__":unittest.main()
