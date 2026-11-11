#include <stdint.h>

/* Native 0x322f2c..0x322fdc: handle a connection parameter request held at
 * record+684 (interval min/max, latency, timeout). An invalid request
 * (max below the record's minimum +692 when min != max, or failing
 * validation) is rejected with 0x1e. A request matching the current
 * interval (+266), latency (+260) and timeout (+382, in 10 ms units) is
 * applied directly; otherwise it is forwarded to the host as LL event 16,
 * and rejected with 0x1a if the event cannot be posted. */
extern uint32_t opencfw_em9305_ll_connection_parameters_validate_30a6b4(uintptr_t);
extern uint32_t opencfw_em9305_ll_connection_mode_30c944(uint32_t,uint32_t);
extern uint32_t opencfw_em9305_ll_connection_modify_30c998(uint32_t,uintptr_t);
extern uint32_t opencfw_em9305_ll_event_callback_30e79c(uintptr_t);

struct init_request_322f2c {
    uint16_t interval_min;
    uint16_t interval_max;
    uint32_t latency_timeout;
    uint32_t reserved;
};

struct init_event_322f2c {
    uint16_t handle;
    uint16_t event;
    uint16_t id;
    uint16_t interval_min;
    uint16_t interval_max;
    uint16_t latency;
    uint16_t timeout;
};

uint32_t opencfw_em9305_child_322f2c(uintptr_t record)
{
    struct init_event_322f2c event;
    struct init_request_322f2c request;
    volatile uint16_t *params=(volatile uint16_t *)(record+684u);
    uint32_t base=*(volatile uint32_t *)(uintptr_t)0x805c70u;
    uint32_t id=(uint8_t)((int32_t)((uint32_t)record-base)/912);
    uint32_t low=params[0];
    uint32_t high=params[1];
    request.reserved=0u;
    request.latency_timeout=*(volatile uint32_t *)(record+688u);
    request.interval_min=(uint16_t)low;
    request.interval_max=(uint16_t)high;
    if(low!=high&&high<*(volatile uint8_t *)(record+692u))
        return opencfw_em9305_ll_connection_mode_30c944(id,0x1eu);
    if(opencfw_em9305_ll_connection_parameters_validate_30a6b4((uintptr_t)&request)!=0u)
        return opencfw_em9305_ll_connection_mode_30c944(id,0x1eu);
    low=params[0];
    uint32_t latency=params[2];
    high=params[1];
    if(low==*(volatile uint16_t *)(record+266u)&&high==low&&
       latency==*(volatile uint16_t *)(record+260u)&&
       params[3]*10u==*(volatile uint16_t *)(record+382u))
        return opencfw_em9305_ll_connection_modify_30c998(id,(uintptr_t)&request);
    event.timeout=params[3];
    event.latency=(uint16_t)latency;
    event.interval_max=(uint16_t)high;
    event.interval_min=(uint16_t)low;
    event.id=(uint16_t)id;
    event.event=16u;
    event.handle=(uint16_t)id;
    uint32_t status=opencfw_em9305_ll_event_callback_30e79c((uintptr_t)&event);
    if(status!=0u) return status;
    return opencfw_em9305_ll_connection_mode_30c944(id,0x1au);
}
