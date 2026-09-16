# SPDX-License-Identifier: MIT
"""Source-level expected startup sequence independent of instruction decoding."""
def expected(symbols,mode,chip,control,trim,seed):
    mask=0xffffffff;stack=0x2006fff0;memory={stack+i:seed&255 for i in range(4)}
    events=[('gx_cache_init',),('gx_dma_init',),('gx_console_init',1,115200),('gx_pmu_get_wakeup_source',)]
    def emit(key,value=None):
        event=('printf',symbols['sys_'+key]);events.append(event if value is None else (*event,value))
    if mode<2:
        for key in ('title','copyright','rights'):emit(key)
        for key in ('board','version'):emit(key+'_format',symbols['sys_'+key])
        emit('release_format',0x42555858);emit('date_format',symbols['sys_date'])
        flash=0x20010000+seed*4
        events.extend([('gx_spi_flash_probe',0,0,6144000,2048),('gx_spi_flash_getinfo',flash,2)])
        vendor={0x854012:'puya',0x856013:'puya',0x1c3812:'esmt',0x1c3813:'esmt',0x5e3414:'zbit'}.get(chip)
        if vendor:emit('vendor_format',symbols['sys_'+vendor])
        events.append(('gx_spi_flash_gettype',flash));emit('type_format',0x20020000+seed*4);emit('id_format',chip)
        events.append(('gx_spi_flash_getinfo',flash,3));emit('size_format',(seed*65536)&mask)
        for module,key in ((10,'cpu'),(6,'sram'),(12,'npu'),(13,'flash')):
            events.append(('gx_clock_get_module_frequence',module));emit(key+'_format',(seed*1000000+module)&mask)
        events.append(('gx_analog_get_ldo_dig_ctrl',))
        if control==2:emit('bypass')
        else:
            events.append(('gx_pmu_ctrl_get',8));config=(seed<<8)|trim
            for i in range(4):memory[stack+i]=(config>>(8*i))&255
            values=(950,924,897,871,845,819,792,766,740,714,687,661);index=config&15
            emit('trim_format',values[index] if index<12 else mask)
        events.extend([(name,) for name in ('gx_gpio_init','BoardInit','gx_rtc_init')]);events.extend([('gx_rtc_set_tick',0),('gx_rtc_start_tick',)])
    events.extend([(name,) for name in ('gx_timer_init','gx_irq_init','device_list_init','spi_master_v3_probe','open_cfw_gx8002_power_initialize')])
    return events,memory
