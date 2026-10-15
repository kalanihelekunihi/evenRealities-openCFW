#!/usr/bin/env python3
"""Link each actual provider once into the shared native board component."""
import hashlib,json,subprocess
from pathlib import Path
from build_source_candidates import undefined_symbols
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    output=BASE/'board';output.mkdir(exist_ok=True);receipt=output/'report.json';receipt.unlink(missing_ok=True)
    reports={name:json.loads((BASE/name).read_text()) for name in ('i2c5/report.json','gpio/report.json','adc/report.json','application-sdk/report.json')}
    objects=[BASE/'i2c5/st25-i2c5-registry.o',BASE/'gpio/stock_named_gpio.o',BASE/'adc/stock_named_adc.o']
    assert sha(objects[0])==reports['i2c5/report.json']['relocatable_sha256']
    for path,name in zip(objects[1:],('gpio/report.json','adc/report.json')):assert sha(path)==reports[name]['units'][0]['object_sha256']
    for suffix in ('nrfx_gpiote.c','nrfx_saadc.c'):
        row=next(x for x in reports['application-sdk/report.json']['units'] if x['source'].endswith('/'+suffix));obj=Path(row['command'][-1]);assert sha(obj)==row['object_sha256'] and sha(ROOT/row['source'])==row['source_sha256'];objects.append(obj)
    runtime_report=BASE/'runtime/report.json';runtime=json.loads(runtime_report.read_text());runtime_object=BASE/'runtime/memory-runtime.o';assert sha(runtime_object)==runtime['relocatable_sha256']
    objects.append(runtime_object)
    integer_report=BASE/'integer-runtime/report.json';integer=json.loads(integer_report.read_text());integer_object=BASE/'integer-runtime/integer-runtime.o';assert sha(integer_object)==integer['relocatable_sha256'];objects.append(integer_object)
    sdk_critical_report=BASE/'sdk-critical/report.json';sdk_critical=json.loads(sdk_critical_report.read_text());sdk_critical_object=BASE/'sdk-critical/critical-only.o';assert sha(sdk_critical_object)==sdk_critical['selected_object_sha256'];objects.append(sdk_critical_object)
    seam_report=BASE/'board-seams/report.json';seams=json.loads(seam_report.read_text());seam_object=BASE/'board-seams/stock_seams.o';assert sha(seam_object)==seams['units'][0]['object_sha256']
    objects.append(seam_object)
    log_report=BASE/'structured-log/report.json';log=json.loads(log_report.read_text());log_object=BASE/'structured-log/structured_log.o';assert sha(log_object)==log['units'][0]['object_sha256']
    objects.append(log_object)
    critical_report=BASE/'rtos-critical/report.json';critical=json.loads(critical_report.read_text());critical_object=BASE/'rtos-critical/critical-only.o';assert sha(critical_object)==critical['selected_object_sha256']
    objects.append(critical_object)
    ticks_report=BASE/'rtos-ticks/report.json';ticks=json.loads(ticks_report.read_text());ticks_object=BASE/'rtos-ticks/ticks-only.o';assert sha(ticks_object)==ticks['selected_object_sha256']
    objects.append(ticks_object)
    encode_report=BASE/'structured-encode/report.json';encode=json.loads(encode_report.read_text());encode_object=BASE/'structured-encode/structured_encode.o';assert sha(encode_object)==encode['units'][0]['object_sha256']
    objects.append(encode_object)
    float_report=BASE/'structured-float/report.json';floating=json.loads(float_report.read_text());float_object=BASE/'structured-float/structured_float.o';assert sha(float_object)==floating['units'][0]['object_sha256']
    objects.append(float_object)
    cache_reports={}
    for name in ('structured-cache','structured-cache-copy','native-events','connection-handle','native-tx','native-task-lifecycle','native-tasks','native-sync','native-watchdog','native-event-dispatch','native-output','native-ble-send','native-bae8-send'):
        path=BASE/(name+'/report.json');row=json.loads(path.read_text());obj=BASE/(name+'/'+name.replace('-','_')+'.o');assert sha(obj)==row['units'][0]['object_sha256'];objects.append(obj);cache_reports[name+'/report.json']=sha(path)
    current_task=BASE/'native-watchdog/current-task-only.o';watchdog=json.loads((BASE/'native-watchdog/report.json').read_text());assert sha(current_task)==watchdog['selected_current_task_sha256'];objects.append(current_task)
    startup_report=BASE/'watchdog-logging/report.json';startup=json.loads(startup_report.read_text());startup_object=BASE/'watchdog-logging/native-watchdog-logging.o';assert sha(startup_object)==startup['relocatable_sha256'];objects.append(startup_object);cache_reports['watchdog-logging/report.json']=sha(startup_report)
    context_report=BASE/'sdk-link-context/report.json';context=json.loads(context_report.read_text());context_object=BASE/'sdk-link-context/blcm_link_ctx_get.o';assert sha(context_object)==context['units'][0]['object_sha256'];assert context['provider_aliases']=={'r1_native_bae8_context_get':'blcm_link_ctx_get'};objects.append(context_object);cache_reports['sdk-link-context/report.json']=sha(context_report)
    index_report=BASE/'sdk-connection-events/report.json';index=json.loads(index_report.read_text());index_object=BASE/'sdk-connection-events/connection-events.o';assert sha(index_object)==index['selected_object_sha256'];objects.append(index_object);cache_reports['sdk-connection-events/report.json']=sha(index_report)
    dispatch_report=BASE/'sdk-ble-dispatch/report.json';dispatch=json.loads(dispatch_report.read_text());dispatch_object=BASE/'sdk-ble-dispatch/ble-dispatch.o';assert sha(dispatch_object)==dispatch['selected_object_sha256'];objects.append(dispatch_object);cache_reports['sdk-ble-dispatch/report.json']=sha(dispatch_report);observer_layout=dispatch['layout'];section_boundaries={prefix+str(i):pair[j] for i,pair in enumerate(observer_layout['ranges']) for j,prefix in enumerate(('__start_sdh_ble_observers','__stop_sdh_ble_observers'))}
    qwr_report=BASE/'sdk-qwr/report.json';qwr=json.loads(qwr_report.read_text());qwr_object=BASE/'sdk-qwr/qwr.o';assert sha(qwr_object)==qwr['selected_object_sha256'];objects.append(qwr_object);cache_reports['sdk-qwr/report.json']=sha(qwr_report)
    gatt_report=BASE/'sdk-gatt/report.json';gatt=json.loads(gatt_report.read_text());gatt_object=BASE/'sdk-gatt/gatt-init.o';assert sha(gatt_object)==gatt['selected_object_sha256'];objects.append(gatt_object);cache_reports['sdk-gatt/report.json']=sha(gatt_report)
    native_gatt_report=BASE/'native-gatt/report.json';native_gatt=json.loads(native_gatt_report.read_text());native_gatt_object=BASE/'native-gatt/native_gatt_observer.o';assert sha(native_gatt_object)==native_gatt['units'][0]['object_sha256'];objects.append(native_gatt_object);cache_reports['native-gatt/report.json']=sha(native_gatt_report)
    advertising_report=BASE/'sdk-advertising-init/report.json';advertising=json.loads(advertising_report.read_text());advertising_object=BASE/'sdk-advertising-init/advertising.o';assert sha(advertising_object)==advertising['selected_object_sha256'];objects.append(advertising_object);cache_reports['sdk-advertising-init/report.json']=sha(advertising_report)
    time_report=BASE/'structured-time/report.json';time=json.loads(time_report.read_text());time_object=BASE/'structured-time/structured_time.o';assert sha(time_object)==time['units'][0]['object_sha256']
    objects.append(time_object)
    linked=output/'native-board.o';subprocess.run(['arm-none-eabi-ld','-r','--defsym=r1_native_bae8_context_get=blcm_link_ctx_get',*['--defsym='+n+'='+a for n,a in section_boundaries.items()],*map(str,objects),'-o',str(linked)],check=True)
    remaining,_=undefined_symbols(linked)
    receipt.write_text(json.dumps(dict(input_reports={**cache_reports,**{name:sha(BASE/name) for name in reports},'sdk-critical/report.json':sha(sdk_critical_report),'integer-runtime/report.json':sha(integer_report),'runtime/report.json':sha(runtime_report),'board-seams/report.json':sha(seam_report),'structured-log/report.json':sha(log_report),'rtos-critical/report.json':sha(critical_report),'rtos-ticks/report.json':sha(ticks_report),'structured-encode/report.json':sha(encode_report),'structured-time/report.json':sha(time_report),'structured-float/report.json':sha(float_report)},objects={str(p.relative_to(ROOT)):sha(p) for p in objects},relocatable_sha256=sha(linked),remaining_symbols=remaining,provider_aliases=context['provider_aliases'],observer_section_boundary_bindings=section_boundaries,unresolved_data_anchors={name:address for name,address in {'r1_native_event_table_sensor':'0x20006750','r1_native_event_table_system':'0x20006e54','r1_native_event_table_storage':'0x200066fc','r1_native_bae8_service':'0x20006504',**observer_layout['contexts']}.items() if name in remaining},application_linked=False,scope='Actual native ADC/GPIO/TWI/registry/ST25 components and Nordic GPIOTE/SAADC, without duplicate inclusion or provider stubs'),indent=2)+'\n');print('Native board linked; remaining:',', '.join(remaining))
if __name__=='__main__':main()
