/* Native HciDrvHandler 0x4b4ab2.  Drains serial receive and the transmit ring
 * under the actual WSF timer/radio recovery state machine.  RAM/MMIO cells
 * below are native literals, not fabricated initial configuration. */
#include <stdint.h>
extern void audio_ble_hci_read_buf_size_cmd_52b620(void); /* native 0x52b620 */
extern void WsfTimerStartMs(void *,uint32_t); /* native 0x52a4c4 */
extern void WsfTimerStop(void *); /* selected 0x52a4d2 */
extern uint32_t audio_ble_hci_serial_rx_incoming_530186(void *,uint16_t);
extern void audio_ble_wsf_set_event(uint32_t,uint32_t);
extern int32_t audio_ble_radio_exchange_receive_52e1ea(void *,void *,uint32_t *);
extern int32_t audio_ble_radio_exchange_begin_52e0d2(void *,const void *,uint32_t);
extern uint32_t audio_ble_hci_ring_consume_5300e2(void *,void *,uint32_t);
extern void audio_ble_hci_error_check_4b47ae(uint32_t);
extern void audio_ble_hci_boot_delay_491102(uint32_t);
extern void audio_ble_hci_driver_radio_shutdown(void);
extern void audio_ble_hci_driver_radio_boot(uint8_t);
extern void audio_ble_hci_driver_empty_queue_4b4d18(void);
extern void audio_ble_dm_device_reset(void);
#define W(a) (*(volatile uint32_t *)(uintptr_t)(a))
#define B(a) (*(volatile uint8_t *)(uintptr_t)(a))
static uint32_t get32(const volatile uint8_t *p) {
    return (uint32_t)p[0]|((uint32_t)p[1]<<8u)|((uint32_t)p[2]<<16u)|((uint32_t)p[3]<<24u);
}
static void restart(void) {
    audio_ble_hci_driver_radio_shutdown();
    audio_ble_hci_driver_radio_boot(0u);
    audio_ble_hci_driver_empty_queue_4b4d18();
    audio_ble_dm_device_reset();
}
uint32_t audio_ble_handler_4b4ab2(uint32_t ignored,const void *message,
                                    uint32_t ignored3,uint32_t high) {
    (void)ignored;(void)ignored3;
    if(message!=0 && ((const uint8_t *)message)[2u]==2u) {
        audio_ble_hci_read_buf_size_cmd_52b620();
        WsfTimerStartMs((void *)(uintptr_t)0x20073e64u,10000u);
        return high;
    }
    uint32_t iterations=0u,received_blocks=0u,write_failures=0u,next=0u;
    uint32_t total=W(0x20074638u),done=W(0x2007463cu);
    if(done<total) {
        uint32_t got=audio_ble_hci_serial_rx_incoming_530186(
            (void *)(uintptr_t)(W(0x20000dacu)+done),(uint16_t)(total-done));
        done+=got;W(0x2007463cu)=done;
        if(done!=total) {
            audio_ble_wsf_set_event(B(0x20074fcbu),1u);
            return high;
        }
        W(0x20074638u)=0u;W(0x2007463cu)=0u;
    }
    for(;;) {
        next=iterations+1u;
        if(iterations>=1000u)break;
        iterations=next;
        if((W(0x40010410u)&0x00200000u)!=0u) {
            high=W(0x20074640u);
            WsfTimerStop((void *)(uintptr_t)0x20073e64u);
            WsfTimerStartMs((void *)(uintptr_t)0x20073e64u,10000u);
            W(0x20074638u)=0u;
            int32_t result=audio_ble_radio_exchange_receive_52e1ea(
                (void *)(uintptr_t)W(0x20074630u),
                (void *)(uintptr_t)0x200704ecu,
                (uint32_t *)(uintptr_t)0x20074638u);
            if(W(0x20074638u)>0x100u)
                audio_ble_hci_error_check_4b47ae(0x09000002u);
            if(result==0) {
                uint32_t tries=0u;
                while(tries<2000u && (W(0x40010410u)&0x00200000u)!=0u &&
                      W(0x20074640u)==high) {
                    audio_ble_hci_boot_delay_491102(1u);
                    tries++;
                }
                uint32_t got=audio_ble_hci_serial_rx_incoming_530186(
                    (void *)(uintptr_t)W(0x20000dacu),
                    (uint16_t)W(0x20074638u));
                W(0x2007463cu)=got;
                if(got!=W(0x20074638u)) {
                    audio_ble_wsf_set_event(B(0x20074fcbu),1u);
                    break;
                }
                W(0x20074638u)=0u;W(0x2007463cu)=0u;
                received_blocks++;
            } else {
                audio_ble_hci_error_check_4b47ae((uint32_t)result);
                restart();
                return high;
            }
            if(received_blocks>3u) {
                audio_ble_wsf_set_event(B(0x20074fcbu),1u);
                break;
            }
        } else {
            volatile uint8_t *ring=(volatile uint8_t *)(uintptr_t)0x20073ba8u;
            if(get32(ring+8u)==0u)break;
            uint32_t pointer=get32(ring+0x14u)+get32(ring+4u);
            uint32_t length=get32((volatile uint8_t *)(uintptr_t)pointer);
            int32_t result=audio_ble_radio_exchange_begin_52e0d2(
                (void *)(uintptr_t)W(0x20074630u),
                (const void *)(uintptr_t)(pointer+4u),length);
            if(result==0) {
                WsfTimerStop((void *)(uintptr_t)0x20073e64u);
                WsfTimerStartMs((void *)(uintptr_t)0x20073e64u,10000u);
                (void)audio_ble_hci_ring_consume_5300e2((void *)ring,0,1u);
                write_failures=0u;iterations=0u;
            } else {
                write_failures++;
                if(write_failures>=0x2711u) {
                    audio_ble_wsf_set_event(B(0x20074fcbu),1u);
                    break;
                }
            }
        }
    }
    if(next==1000u) {
        audio_ble_hci_error_check_4b47ae(0x09000006u);
        restart();
    }
    return high;
}
