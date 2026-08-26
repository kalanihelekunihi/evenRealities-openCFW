import subprocess
import tempfile
import textwrap
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "components/shared/cordio"
SOURCES = [
    SOURCE_DIR / "runtime_cordio_l2c_main.c",
    SOURCE_DIR / "runtime_cordio_l2c_master.c",
    SOURCE_DIR / "runtime_cordio_l2c_slave.c",
]


class CordioL2cSourceTests(unittest.TestCase):
    def test_host_routing_signaling_updates_and_bounds(self) -> None:
        harness = textwrap.dedent(r"""
            #include <assert.h>
            #include <stdint.h>
            #include <stdlib.h>
            #include <string.h>
            #include "runtime_cordio_l2c.h"

            struct open_cfw_cordio_l2c_control_block
                open_cfw_cordio_l2c_control_block;
            struct open_cfw_cordio_l2c_slave_control_block
                open_cfw_cordio_l2c_slave_control_block;

            static void (*acl_callback)(uint8_t *);
            static void (*flow_callback)(uint16_t,uint8_t);
            static uint8_t roles[4];
            static int alloc_fail, frees, sends, starts, stops;
            static int att_data, smp_data, cid_data, controls[3];
            static int master_rx, slave_rx, indications, confirmations, rejects;
            static uint8_t *last_sent;
            static uint16_t last_handle, last_result, last_cid, last_length;
            static uint8_t last_identifier;
            static struct open_cfw_cordio_l2c_connection_specification last_spec;

            uint8_t open_cfw_cordio_dm_connection_id_by_handle(uint16_t h) {
                return h==0x1111U?1U:(h==0x2222U?2U:0U);
            }
            uint8_t open_cfw_cordio_dm_connection_role(uint8_t id) {
                return id<4U?roles[id]:0xFFU;
            }
            void open_cfw_cordio_hci_acl_register(
                void (*a)(uint8_t *),void (*f)(uint16_t,uint8_t)) {
                acl_callback=a;flow_callback=f;
            }
            void open_cfw_cordio_hci_send_acl_data(uint8_t *p) {
                sends++;last_sent=p;last_handle=(uint16_t)(p[0]|(p[1]<<8));
                last_length=(uint16_t)(p[4]|(p[5]<<8));
                last_cid=(uint16_t)(p[6]|(p[7]<<8));
            }
            void *open_cfw_cordio_wsf_message_data_allocate_candidate(
                uint16_t n,uint8_t tail) {
                assert(tail==0U);return alloc_fail?NULL:calloc(1,n);
            }
            void open_cfw_cordio_wsf_message_free_candidate(void *p) {
                frees++;free(p);
            }
            void open_cfw_cordio_wsf_timer_start_sec_candidate(
                void *p,uint32_t seconds) {
                assert(p==open_cfw_cordio_l2c_slave_control_block.request_timer);
                assert(seconds==30U);starts++;
            }
            void open_cfw_cordio_wsf_timer_stop_candidate(void *p) {
                assert(p==open_cfw_cordio_l2c_slave_control_block.request_timer);
                stops++;
            }
            void open_cfw_cordio_dm_l2c_connection_update_indication(
                uint8_t id,uint16_t h,
                struct open_cfw_cordio_l2c_connection_specification *s) {
                indications++;last_identifier=id;last_handle=h;last_spec=*s;
            }
            void open_cfw_cordio_dm_l2c_connection_update_confirmation(
                uint16_t h,uint16_t result) {
                confirmations++;last_handle=h;last_result=result;
            }
            void open_cfw_cordio_dm_l2c_command_reject_indication(
                uint16_t h,uint16_t reason) {
                rejects++;last_handle=h;last_result=reason;
            }
            static void att(uint16_t h,uint16_t n,uint8_t *p) {
                assert(h==0x111U&&n==2U&&p!=NULL);att_data++;
            }
            static void smp(uint16_t h,uint16_t n,uint8_t *p) {
                (void)h;(void)n;(void)p;smp_data++;
            }
            static void cid(uint16_t h,uint16_t c,uint16_t n,uint8_t *p) {
                (void)h;(void)n;(void)p;assert(c==0x40U);cid_data++;
            }
            static void ctrl0(struct open_cfw_cordio_l2c_message_header *m) {
                assert(m->parameter==1U&&m->event==1U);controls[0]++;
            }
            static void ctrl1(struct open_cfw_cordio_l2c_message_header *m) {
                assert(m->parameter==1U&&m->event==1U);controls[1]++;
            }
            static void ctrl2(struct open_cfw_cordio_l2c_message_header *m) {
                assert(m->parameter==1U&&m->event==1U);controls[2]++;
            }
            static void master(uint16_t h,uint16_t n,uint8_t *p) {
                assert(h==0x1111U&&n==4U&&p!=NULL);master_rx++;
            }
            static void slave(uint16_t h,uint16_t n,uint8_t *p) {
                assert(h==0x2222U&&n==4U&&p!=NULL);slave_rx++;
            }
            static void put16(uint8_t *p,uint16_t v) {
                p[0]=(uint8_t)v;p[1]=(uint8_t)(v>>8);
            }
            static uint8_t *acl(uint16_t h,uint16_t cid,uint16_t n) {
                uint8_t *p=calloc(1,8U+n);assert(p);
                put16(p,h);put16(p+2,(uint16_t)(n+4U));put16(p+4,n);
                put16(p+6,cid);return p;
            }
            static uint8_t *signal_packet(uint8_t code,uint8_t id,uint16_t n) {
                uint8_t *p=calloc(1,12U+n);assert(p);p[8]=code;p[9]=id;
                put16(p+10,n);return p;
            }

            int main(void) {
                uint8_t *p;
                struct open_cfw_cordio_l2c_connection_specification spec={6,12,0,10,0,0};
                struct open_cfw_cordio_l2c_message_header timeout={0x2222U,1U,0U};

                open_cfw_cordio_l2c_initialize();
                assert(acl_callback&&flow_callback);
                assert(open_cfw_cordio_l2c_control_block.identifier==1U);
                open_cfw_cordio_l2c_register(4U,att,ctrl0);
                open_cfw_cordio_l2c_register(6U,smp,ctrl1);
                open_cfw_cordio_l2c_control_block.cid_data_callback=cid;
                open_cfw_cordio_l2c_control_block.coc_control_callback=ctrl2;

                p=acl(0xF111U,4U,2U);acl_callback(p);assert(att_data==1&&frees==1);
                p=acl(0x111U,6U,2U);acl_callback(p);assert(smp_data==1&&frees==2);
                p=acl(0x111U,0x40U,2U);acl_callback(p);assert(cid_data==1&&frees==3);
                p=acl(0x111U,4U,2U);p[2]=1U;p[3]=0U;acl_callback(p);
                assert(att_data==1&&frees==4);

                flow_callback(0x1111U,1U);assert(controls[0]==1&&controls[1]==1&&controls[2]==1);
                flow_callback(0x9999U,1U);assert(controls[0]==1);

                roles[1]=0U;roles[2]=1U;
                open_cfw_cordio_l2c_control_block.master_signaling_callback=master;
                open_cfw_cordio_l2c_control_block.slave_signaling_callback=slave;
                {uint8_t q[12]={0};open_cfw_cordio_l2c_receive_signaling_packet(0x1111U,4U,q);
                 open_cfw_cordio_l2c_receive_signaling_packet(0x2222U,4U,q);}
                assert(master_rx==1&&slave_rx==1);
                open_cfw_cordio_l2c_receive_signaling_packet(0x1111U,3U,NULL);

                p=calloc(1,10U);open_cfw_cordio_l2c_data_request(4U,0x1234U,2U,p);
                assert(sends==1&&last_handle==0x1234U&&last_cid==4U&&last_length==2U);
                free(last_sent);last_sent=NULL;
                p=calloc(1,8U);open_cfw_cordio_l2c_data_request(4U,1U,0xFFFFU,p);
                assert(sends==1&&frees==5);

                open_cfw_cordio_l2c_send_command_reject(0x1111U,9U,0x1234U);
                assert(sends==2&&last_sent[8]==1U&&last_sent[9]==9U);
                assert(last_sent[12]==0x34U&&last_sent[13]==0x12U);free(last_sent);

                open_cfw_cordio_l2c_master_initialize();
                p=signal_packet(0x12U,7U,8U);put16(p+12,6U);put16(p+14,12U);
                put16(p+16,0U);put16(p+18,10U);
                open_cfw_cordio_l2c_master_receive_signaling_packet(0x1111U,12U,p);
                assert(indications==1&&last_identifier==7U&&last_handle==0x1111U);
                assert(last_spec.interval_minimum==6U&&last_spec.interval_maximum==12U);
                free(p);
                p=signal_packet(0x12U,8U,8U);put16(p+12,5U);put16(p+14,12U);
                put16(p+16,0U);put16(p+18,10U);
                open_cfw_cordio_l2c_master_receive_signaling_packet(0x1111U,12U,p);
                assert(sends==3&&last_sent[8]==0x13U&&last_sent[9]==8U);
                assert(last_sent[12]==1U);free(last_sent);free(p);
                open_cfw_cordio_l2c_master_receive_signaling_packet(0x1111U,0U,NULL);

                open_cfw_cordio_l2c_slave_initialize();
                open_cfw_cordio_l2c_slave_handler_initialize(9U);
                assert(open_cfw_cordio_l2c_slave_control_block.request_timer[10]==1U);
                assert(open_cfw_cordio_l2c_slave_control_block.request_timer[12]==9U);
                open_cfw_cordio_l2c_control_block.identifier=1U;
                open_cfw_cordio_l2c_connection_update_request(0x2222U,&spec);
                assert(starts==1&&sends==4&&last_sent[8]==0x12U&&last_sent[9]==1U);
                assert(open_cfw_cordio_l2c_slave_control_block.signaling_id[0]==0U);
                assert(open_cfw_cordio_l2c_slave_control_block.signaling_id[1]==1U);
                free(last_sent);
                p=signal_packet(0x13U,1U,2U);put16(p+12,0U);
                open_cfw_cordio_l2c_slave_receive_signaling_packet(0x2222U,6U,p);
                assert(stops==1&&confirmations==1&&last_result==0U);
                assert(open_cfw_cordio_l2c_slave_control_block.signaling_id[1]==0U);free(p);

                {uint8_t reason[2]={0x55U,0x00U};
                 open_cfw_cordio_l2c_signaling_request(0x1111U,0x20U,2U,reason);}
                assert(starts==2&&sends==5);last_identifier=last_sent[9];free(last_sent);
                p=signal_packet(1U,last_identifier,2U);put16(p+12,0x55U);
                open_cfw_cordio_l2c_slave_receive_signaling_packet(0x1111U,6U,p);
                assert(stops==2&&rejects==1&&last_result==0x55U);free(p);

                alloc_fail=1;starts=0;
                open_cfw_cordio_l2c_connection_update_request(0x2222U,&spec);
                assert(starts==0);alloc_fail=0;
                open_cfw_cordio_l2c_slave_control_block.signaling_id[1]=4U;
                open_cfw_cordio_l2c_slave_handler(0U,&timeout);
                assert(confirmations==2&&last_result==1U);
                assert(open_cfw_cordio_l2c_slave_control_block.signaling_id[1]==0U);
                open_cfw_cordio_l2c_slave_handler(1U,NULL);
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
                 "-I", str(SOURCE_DIR), *map(str, SOURCES),
                 str(harness_path), "-o", str(executable)], check=True
            )
            subprocess.run([str(executable)], check=True)

    def test_complete_and_isolated_cortex_m55_builds(self) -> None:
        selections = {
            SOURCES[0]: ("MAIN", [
                "DEFAULT_DATA", "DEFAULT_CID_DATA", "DEFAULT_CONTROL",
                "SIGNALING", "ACL", "FLOW", "REJECT", "ALLOCATE",
                "INITIALIZE", "REGISTER", "DATA_REQUEST",
            ]),
            SOURCES[1]: ("MASTER", ["RECEIVE", "INITIALIZE", "RESPONSE"]),
            SOURCES[2]: ("SLAVE", [
                "TIMEOUT", "RECEIVE", "INITIALIZE", "SIGNAL_REQUEST",
                "UPDATE_REQUEST", "HANDLER_INIT", "HANDLER",
            ]),
        }
        with tempfile.TemporaryDirectory() as directory:
            for source, (module, selectors) in selections.items():
                for selector in [None, *selectors]:
                    command = [
                        "clang", "--target=thumbv7em-none-eabi", "-mthumb",
                        "-mcpu=cortex-m55", "-O2", "-ffreestanding",
                        "-fno-builtin", "-Wall", "-Wextra", "-Werror",
                        "-I", str(SOURCE_DIR),
                    ]
                    if selector:
                        command.append(
                            f"-DOPEN_CFW_L2C_{module}_{selector}_ONLY=1"
                        )
                    command += ["-c", str(source), "-o", str(
                        Path(directory) / f"{module}-{selector or 'all'}.o"
                    )]
                    subprocess.run(command, check=True)


if __name__ == "__main__":
    unittest.main()
