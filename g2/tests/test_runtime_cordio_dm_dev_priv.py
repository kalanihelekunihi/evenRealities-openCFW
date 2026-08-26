import subprocess,tempfile,textwrap,unittest
from pathlib import Path
R=Path(__file__).resolve().parents[1];D=R/"components/shared/cordio";S=D/"runtime_cordio_dm_dev_priv.c"
class T(unittest.TestCase):
 def test_behavior_and_target_compile(self):
  h=textwrap.dedent(r'''
   #include <assert.h>
   #include <stdlib.h>
   #include "runtime_cordio_dm_dev_priv.h"
   static unsigned ts,tp,rnd,aes,setaddr,types,timeout,clear,send,locks,unlocks,cb;static uint8_t irk[16],last[6];
   void open_cfw_cordio_wsf_timer_start_seconds(void*p,uint16_t s){(void)p;ts++;assert(s==30);}void open_cfw_cordio_wsf_timer_stop(void*p){(void)p;tp++;}
   void open_cfw_cordio_security_random(uint8_t*p,uint8_t n){rnd++;while(n--)*p++=1;}void open_cfw_cordio_security_aes(uint8_t*k,uint8_t*p,uint8_t h,uint8_t z,uint8_t e){aes++;assert(k==irk&&p[2]==0x41&&h==4&&!z&&e==3);}
   uint8_t*open_cfw_cordio_dm_security_local_irk(void){return irk;}void open_cfw_cordio_hci_set_random_address(uint8_t*p){setaddr++;for(int i=0;i<6;i++)last[i]=p[i];}
   void open_cfw_cordio_dm_advertising_set_address_type(uint8_t x){types+=x+1;}void open_cfw_cordio_dm_scanning_set_address_type(uint8_t x){types+=x+1;}void open_cfw_cordio_dm_connection_master_set_address_type(uint8_t x){types+=x+1;}
   uint8_t open_cfw_cordio_hci_ll_privacy_supported(void){return 1;}void open_cfw_cordio_dm_privacy_set_timeout(uint16_t x){timeout++;assert(x==30);}void open_cfw_cordio_dm_privacy_clear_resolving_list(void){clear++;}
   void*open_cfw_cordio_wsf_message_allocate(uint16_t n){return calloc(1,n);}void open_cfw_cordio_wsf_message_send(uint8_t h,void*p){send++;assert(h==4);free(p);}void open_cfw_cordio_wsf_task_lock(void){locks++;}void open_cfw_cordio_wsf_task_unlock(void){unlocks++;}
   static void event(void*p){(void)p;cb++;}
   int main(void){struct open_cfw_cordio_dm_dev_priv_message m={0};open_cfw_cordio_dm_dev_priv_handler_id=4;open_cfw_cordio_dm_dev_priv_callback=event;
    m.change_interval=30;open_cfw_cordio_dm_dev_priv_control.advertising=1;open_cfw_cordio_dm_device_privacy_action_start(&m);assert(open_cfw_cordio_dm_dev_priv_control.use_resolvable&&ts==1&&rnd==1&&aes==1&&timeout==1&&types==6);
    m.ciphertext[0]=2;m.ciphertext[1]=3;m.ciphertext[2]=4;open_cfw_cordio_dm_device_privacy_action_aes_complete(&m);assert(open_cfw_cordio_dm_dev_priv_control.pending_address[0]==2);
    m.parameter=OPEN_CFW_DEV_PRIV_ADV_STOP;open_cfw_cordio_dm_device_privacy_action_rpa_stop(&m);assert(setaddr==1&&last[0]==2);
    m.parameter=OPEN_CFW_DEV_PRIV_ADV_SET_ADD;m.advertising_handle=1;m.connectable=1;open_cfw_cordio_dm_dev_priv_control.address_initialized=1;open_cfw_cordio_dm_device_privacy_action_control(&m);assert(open_cfw_cordio_dm_dev_priv_control.extended[1].configured);
    m.event=1;m.status=7;open_cfw_cordio_dm_device_privacy_hci_handler(&m);assert(cb==1);
    open_cfw_cordio_dm_device_privacy_start(8);open_cfw_cordio_dm_device_privacy_stop();assert(send==2);
    open_cfw_cordio_dm_device_privacy_initialize();assert(locks==1&&unlocks==1);open_cfw_cordio_dm_device_privacy_action_stop(&m);assert(clear==1&&tp>=1);open_cfw_cordio_dm_device_privacy_reset();return 0;}
  ''')
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/"h.c";x=Path(d)/"x";p.write_text(h);subprocess.run(["cc","-std=c11","-Wall","-Wextra","-Werror","-I",str(D),str(S),str(p),"-o",str(x)],check=True);subprocess.run([str(x)],check=True);subprocess.run(["clang","--target=thumbv7em-none-eabi","-mthumb","-mcpu=cortex-m55","-O2","-ffreestanding","-fno-builtin","-Wall","-Wextra","-Werror","-I",str(D),"-c",str(S),"-o",str(Path(d)/"t.o")],check=True)
if __name__=="__main__":unittest.main()
