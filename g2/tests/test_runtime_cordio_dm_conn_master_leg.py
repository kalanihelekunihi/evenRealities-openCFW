import subprocess,tempfile,textwrap,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; SD=ROOT/"components/shared/cordio"; SRC=SD/"runtime_cordio_dm_conn_master_leg.c"
class DmConnMasterLegSourceTests(unittest.TestCase):
 def test_open_action_init_and_bounds(self):
  h=textwrap.dedent(r'''
   #include <assert.h>
   #include <stdint.h>
   #include "runtime_cordio_dm_conn_master_leg.h"
   static unsigned scans,creates,privacy,locks,unlocks,maps;static uint8_t peer[6],own;
   uint8_t open_cfw_cordio_dm_scan_phy_to_index(uint8_t p){scans++;assert(p==1);return 0;}
   uint8_t open_cfw_cordio_dm_link_layer_address_type(uint8_t t){maps++;return t+2;}
   void open_cfw_cordio_hci_create_connection(uint16_t i,uint16_t w,uint8_t f,uint8_t pt,uint8_t *p,uint8_t o,struct open_cfw_cordio_dm_connection_spec*s){creates++;assert(i==16&&w==8&&f==3&&pt==1&&s==&open_cfw_cordio_dm_conn_master_leg_connection_spec[0]);peer[0]=p[0];own=o;}
   void open_cfw_cordio_dm_device_pass_event_to_privacy(uint8_t e,uint8_t p,uint8_t a,uint8_t c){privacy++;assert(e==0x30&&p==1&&!a&&!c);}
   void open_cfw_cordio_wsf_task_lock(void){locks++;}void open_cfw_cordio_wsf_task_unlock(void){unlocks++;}
   int main(void){struct open_cfw_cordio_dm_connection_open_message m={0};uint8_t a[6]={9};
    open_cfw_cordio_dm_conn_master_leg_scan_interval[0]=16;open_cfw_cordio_dm_conn_master_leg_scan_window[0]=8;open_cfw_cordio_dm_conn_master_leg_initiator_filter_policy=3;open_cfw_cordio_dm_conn_master_leg_connection_address_type=1;
    open_cfw_cordio_dm_connection_master_legacy_open(1,1,a);assert(scans==1&&creates==1&&privacy==1&&peer[0]==9&&own==3&&maps==1);
    open_cfw_cordio_dm_connection_master_legacy_open(0,1,a);open_cfw_cordio_dm_connection_master_legacy_open(1,1,0);assert(creates==1);
    m.initiating_phys=1;m.address_type=1;m.peer_address[0]=7;open_cfw_cordio_dm_connection_master_legacy_action_open(0,&m);assert(creates==2&&peer[0]==7);open_cfw_cordio_dm_connection_master_legacy_action_open(0,0);
    open_cfw_cordio_dm_conn_master_leg_master_action_table=0x1111;open_cfw_cordio_dm_conn_master_leg_master_update_action_table=0x2222;open_cfw_cordio_dm_connection_master_legacy_initialize();assert(locks==1&&unlocks==1&&open_cfw_cordio_dm_conn_master_leg_action_sets[1]==0x1111&&open_cfw_cordio_dm_conn_master_leg_update_action_sets[1]==0x2222);return 0;}
  ''')
  with tempfile.TemporaryDirectory() as d:
   hp=Path(d)/"h.c";ex=Path(d)/"t";hp.write_text(h);subprocess.run(["cc","-std=c11","-Wall","-Wextra","-Werror","-I",str(SD),str(SRC),str(hp),"-o",str(ex)],check=True);subprocess.run([str(ex)],check=True)
 def test_full_and_isolated_target_builds(self):
  with tempfile.TemporaryDirectory() as d:
   for s in [None,"OPEN","ACTION_OPEN","INIT"]:
    c=["clang","--target=thumbv7em-none-eabi","-mthumb","-mcpu=cortex-m55","-O2","-ffreestanding","-fno-builtin","-Wall","-Wextra","-Werror","-I",str(SD),"-DOPEN_CFW_DM_CONN_MASTER_LEG_PRODUCTION=1"]
    if s:c.append(f"-DOPEN_CFW_DM_CONN_MASTER_LEG_{s}_ONLY=1")
    c += ["-c",str(SRC),"-o",str(Path(d)/f"{s or 'all'}.o")];subprocess.run(c,check=True)
if __name__=="__main__":unittest.main()
