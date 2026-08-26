import subprocess
import tempfile
import textwrap
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "components/shared/cordio"
SOURCE = SOURCE_DIR / "runtime_cordio_dm_adv.c"


class CordioDmAdvSourceTests(unittest.TestCase):
    def test_host_messages_state_events_utilities_and_bounds(self) -> None:
        harness = textwrap.dedent(r"""
            #include <assert.h>
            #include <stdint.h>
            #include <stdlib.h>
            #include <string.h>
            #include "runtime_cordio_dm_adv.h"

            struct open_cfw_cordio_dm_adv_control_block
                open_cfw_cordio_dm_adv_control_block;
            struct open_cfw_cordio_dm_main_control_block
                open_cfw_cordio_dm_main_control_block;

            static unsigned allocations, sends, locks, unlocks, passes;
            static uint16_t allocation_length;
            static uint8_t sent_handler;
            static uint8_t *sent_message;
            static int allocation_failure;
            static struct open_cfw_cordio_dm_connection_complete_event passed;

            void *open_cfw_cordio_wsf_message_allocate_candidate(uint16_t n) {
                allocations++; allocation_length=n;
                return allocation_failure ? NULL : calloc(1U,n);
            }
            void open_cfw_cordio_wsf_message_send_candidate(uint8_t h,void *p) {
                sends++; sent_handler=h; sent_message=p;
            }
            void open_cfw_cordio_wsf_task_lock_candidate(void) { locks++; }
            void open_cfw_cordio_wsf_task_unlock_candidate(void) { unlocks++; }
            void open_cfw_cordio_dm_device_pass_hci_event_to_connection(
                struct open_cfw_cordio_dm_connection_complete_event *event) {
                passes++; passed=*event;
            }
            static uint16_t u16(const uint8_t *p) {
                return (uint16_t)(p[0] | ((uint16_t)p[1] << 8));
            }
            static void release_message(void) {
                free(sent_message); sent_message=NULL;
            }

            int main(void) {
                uint8_t peer[6]={1,2,3,4,5,6};
                uint8_t handles[2]={1,0};
                uint16_t durations[2]={0x1234,0x5678};
                uint8_t maxima[2]={9,10};
                uint8_t data[3]={0xAA,0xBB,0xCC};
                uint8_t ad[32]={0}; uint16_t ad_len=0;
                uint8_t value[4]={7,8,9,10};
                uint8_t malformed[4]={5,1,2,3}; uint16_t malformed_len=4;

                open_cfw_cordio_dm_main_control_block.handler_id=0x2AU;
                open_cfw_cordio_dm_adv_initialize();
                assert(open_cfw_cordio_dm_adv_control_block.advertising_type[0]==0xFFU);
                assert(open_cfw_cordio_dm_adv_control_block.advertising_type[1]==0xFFU);
                assert(open_cfw_cordio_dm_adv_control_block.interval_minimum[1]==1600U);
                assert(open_cfw_cordio_dm_adv_control_block.interval_maximum[1]==1920U);
                assert(open_cfw_cordio_dm_adv_control_block.channel_map[0]==7U);
                assert(open_cfw_cordio_dm_adv_control_block.advertising_timer[12]==0x2AU);
                assert(open_cfw_cordio_dm_main_control_block.advertising_address_type==0U);
                open_cfw_cordio_dm_adv_control_block.advertising_type[0]=4U;
                open_cfw_cordio_dm_adv_control_block_initialize(2U);
                assert(open_cfw_cordio_dm_adv_control_block.advertising_type[0]==4U);

                memcpy(open_cfw_cordio_dm_adv_control_block.peer_address[1],peer,6U);
                open_cfw_cordio_dm_adv_control_block.peer_address_type[1]=3U;
                open_cfw_cordio_dm_adv_generate_connection_complete(1U,5U);
                assert(passes==1U&&passed.header.event==2U&&passed.header.status==5U);
                assert(passed.status==5U&&passed.role==1U&&passed.address_type==3U);
                assert(memcmp(passed.peer_address,peer,6U)==0);
                open_cfw_cordio_dm_adv_generate_connection_complete(2U,0U);
                assert(passes==1U);

                open_cfw_cordio_dm_adv_configure(1U,4U,3U,peer);
                assert(sends==1U&&sent_handler==0x2AU&&allocation_length==14U);
                assert(sent_message[2]==0U&&sent_message[4]==1U&&sent_message[5]==4U);
                assert(sent_message[6]==3U&&memcmp(sent_message+7,peer,6U)==0);
                release_message();
                open_cfw_cordio_dm_adv_configure(2U,0U,0U,peer);
                open_cfw_cordio_dm_adv_configure(0U,0U,0U,NULL);
                assert(sends==1U);

                open_cfw_cordio_dm_adv_set_data(0U,2U,1U,3U,data);
                assert(sends==2U&&allocation_length==11U&&sent_message[2]==1U);
                assert(sent_message[4]==0U&&sent_message[5]==2U);
                assert(sent_message[6]==1U&&sent_message[7]==3U);
                assert(memcmp(sent_message+8,data,3U)==0); release_message();
                open_cfw_cordio_dm_adv_set_data(0U,0U,2U,3U,data);
                open_cfw_cordio_dm_adv_set_data(0U,0U,0U,3U,NULL);
                assert(sends==2U);

                open_cfw_cordio_dm_adv_start(2U,handles,durations,maxima);
                assert(sends==3U&&allocation_length==14U&&sent_message[2]==2U);
                assert(sent_message[4]==2U&&sent_message[5]==1U&&sent_message[6]==0U);
                assert(u16(sent_message+8)==0x1234U&&u16(sent_message+10)==0x5678U);
                assert(sent_message[12]==9U&&sent_message[13]==10U); release_message();
                {uint8_t bad[1]={2U};
                 open_cfw_cordio_dm_adv_start(1U,bad,durations,maxima);}
                open_cfw_cordio_dm_adv_start(1U,NULL,durations,maxima);
                assert(sends==3U);

                open_cfw_cordio_dm_adv_stop(2U,handles);
                assert(sends==4U&&allocation_length==8U&&sent_message[2]==3U);
                assert(sent_message[4]==2U&&sent_message[5]==1U&&sent_message[6]==0U);
                release_message();
                open_cfw_cordio_dm_adv_stop(3U,handles); assert(sends==4U);

                open_cfw_cordio_dm_adv_remove_set(1U);
                assert(sends==5U&&allocation_length==6U&&sent_message[2]==4U);
                assert(sent_message[4]==1U); release_message();
                open_cfw_cordio_dm_adv_clear_sets();
                assert(sends==6U&&allocation_length==4U&&sent_message[2]==5U);
                release_message();
                open_cfw_cordio_dm_adv_set_random_address(0U,peer);
                assert(sends==7U&&allocation_length==12U&&sent_message[2]==6U);
                assert(sent_message[4]==0U&&memcmp(sent_message+5,peer,6U)==0);
                release_message();

                open_cfw_cordio_dm_adv_set_interval(1U,32U,64U);
                assert(locks==1U&&unlocks==1U);
                assert(open_cfw_cordio_dm_adv_control_block.interval_minimum[1]==32U);
                open_cfw_cordio_dm_adv_set_interval(1U,65U,64U);
                assert(locks==1U);
                open_cfw_cordio_dm_adv_set_channel_map(1U,5U);
                assert(locks==2U&&unlocks==2U);
                assert(open_cfw_cordio_dm_adv_control_block.channel_map[1]==5U);
                open_cfw_cordio_dm_adv_set_channel_map(1U,0U);
                assert(locks==2U);
                open_cfw_cordio_dm_adv_set_address_type(3U);
                assert(locks==3U&&unlocks==3U);
                assert(open_cfw_cordio_dm_main_control_block.advertising_address_type==3U);

                assert(open_cfw_cordio_dm_adv_set_element(0xFFU,3U,data,
                    &ad_len,ad,sizeof(ad))==1U);
                assert(ad_len==5U&&ad[0]==4U&&ad[1]==0xFFU&&ad[4]==0xCCU);
                assert(open_cfw_cordio_dm_adv_set_element(0xFFU,3U,value,
                    &ad_len,ad,sizeof(ad))==1U);
                assert(ad_len==5U&&ad[2]==7U&&ad[4]==9U);
                assert(open_cfw_cordio_dm_adv_set_element(0xFFU,4U,value,
                    &ad_len,ad,sizeof(ad))==1U);
                assert(ad_len==6U&&ad[0]==5U&&ad[5]==10U);
                {uint16_t before=ad_len; uint8_t copy[32]; memcpy(copy,ad,32U);
                 assert(open_cfw_cordio_dm_adv_set_element(0xFFU,29U,value,
                    &ad_len,ad,6U)==0U); assert(ad_len==before);
                 assert(memcmp(copy,ad,32U)==0);}
                assert(open_cfw_cordio_dm_adv_set_element(1U,1U,value,
                    &malformed_len,malformed,sizeof(malformed))==0U);

                ad_len=0U; memset(ad,0,sizeof(ad));
                assert(open_cfw_cordio_dm_adv_set_name(4U,value,&ad_len,ad,8U)==1U);
                assert(ad_len==6U&&ad[0]==5U&&ad[1]==9U&&ad[5]==10U);
                ad_len=0U; memset(ad,0,sizeof(ad));
                assert(open_cfw_cordio_dm_adv_set_name(4U,value,&ad_len,ad,5U)==1U);
                assert(ad_len==5U&&ad[0]==4U&&ad[1]==8U);
                assert(open_cfw_cordio_dm_adv_set_name(1U,value,
                    &malformed_len,malformed,sizeof(malformed))==0U);

                allocation_failure=1;
                open_cfw_cordio_dm_adv_clear_sets();
                assert(allocations>sends&&sent_message==NULL);
                return 0;
            }
        """)
        with tempfile.TemporaryDirectory() as directory:
            temporary = Path(directory)
            harness_path = temporary / "harness.c"
            executable = temporary / "test"
            harness_path.write_text(harness)
            subprocess.run(
                ["cc", "-std=c11", "-Wall", "-Wextra", "-Werror",
                 "-I", str(SOURCE_DIR), str(SOURCE), str(harness_path),
                 "-o", str(executable)], check=True
            )
            subprocess.run([str(executable)], check=True)

    def test_complete_and_isolated_cortex_m55_builds(self) -> None:
        selectors = [
            "CB_INIT", "INIT", "CONN_COMPLETE", "CONFIGURE", "SET_DATA",
            "START", "STOP", "REMOVE", "CLEAR", "SET_RANDOM",
            "SET_INTERVAL", "SET_CHANNEL", "SET_ADDRESS_TYPE",
            "SET_ELEMENT", "SET_NAME",
        ]
        with tempfile.TemporaryDirectory() as directory:
            for selector in [None, *selectors]:
                command = [
                    "clang", "--target=thumbv7em-none-eabi", "-mthumb",
                    "-mcpu=cortex-m55", "-O2", "-ffreestanding",
                    "-fno-builtin", "-Wall", "-Wextra", "-Werror",
                    "-I", str(SOURCE_DIR),
                ]
                if selector:
                    command.append(f"-DOPEN_CFW_DM_ADV_{selector}_ONLY=1")
                command += ["-DOPEN_CFW_DM_ADV_PRODUCTION=1", "-c",
                            str(SOURCE), "-o",
                            str(Path(directory) / f"{selector or 'all'}.o")]
                subprocess.run(command, check=True)


if __name__ == "__main__":
    unittest.main()
