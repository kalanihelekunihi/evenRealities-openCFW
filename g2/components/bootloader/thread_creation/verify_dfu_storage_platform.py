#!/usr/bin/env python3
"""Native scatter-published platform/storage callbacks; ROM hardware modeled."""
import importlib.util,json,sys,hashlib,struct
from collections import Counter
from pathlib import Path
from unicorn import UC_HOOK_MEM_WRITE
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('cache_profile',HERE/'verify_dfu_storage_cache.py');c=importlib.util.module_from_spec(spec);spec.loader.exec_module(c);s=c.s;v=c.v
INIT_HELPER=s.ROOT/'g2/components/bootloader/initializer_callbacks/integration.py'
initv=None
if INIT_HELPER.exists():
 init_spec=importlib.util.spec_from_file_location('initializer_integration',INIT_HELPER);initv=importlib.util.module_from_spec(init_spec);init_spec.loader.exec_module(initv)
MACHINES=[]
LOCAL_PROVIDERS={}
NATIVE_DEVICE_INFO=False
NATIVE_DELAY_MATH=False
NATIVE_NOR_PROFILE=False
NATIVE_INITIALIZER_PROFILE=False
NATIVE_KERNEL_STATE_PROFILE=False
NATIVE_CONTEXT_IRQ_PROFILE=False
NATIVE_IOM_CONTEXT_PROFILE=False
NATIVE_IOM_CHILD_PROFILE=False
NATIVE_NVIC_PROFILE=False
NATIVE_SEMAPHORE_PROFILE=False
NATIVE_GPIO_DESCRIPTOR_PROFILE=False
NATIVE_ADC_CONTEXT_PROFILE=False
NATIVE_ADC_CONTROL_PROFILE=False
NATIVE_ADC_CONFIGURATION_PROFILE=False
NATIVE_ADC_SAMPLES_PROFILE=False
NATIVE_ADC_PROFILE_PROFILE=False
NATIVE_UART_PROFILE=False
NATIVE_SERVICE_PROFILE=False
NATIVE_MUTEX_PROFILE=False
NATIVE_ISR_PROFILE=False
ISR_ENTRIES={"opencfw_bl_kernel_queue_put_from_isr":0x41a024,"opencfw_bl_kernel_queue_get_from_isr":0x41a3b0,"opencfw_boot_queue_isr_task_count":0x41836c,"opencfw_boot_isr_thread_notify":0x418fe8,"opencfw_boot_pend_callback_isr":0x4196e6,"opencfw_boot_event_flags_deferred":0x419bae,"opencfw_bl_event_flags_set_isr":0x419bd2}
MUTEX_ENTRIES={"opencfw_boot_mutex_acquire":0x4166aa,"opencfw_boot_mutex_release":0x416710,"opencfw_bl_kernel_mutex_take_plain":0x41a24e,"opencfw_bl_kernel_mutex_take_tagged":0x419e22,"opencfw_bl_kernel_mutex_give_tagged":0x419de2,"opencfw_boot_current_task":0x418b4e,"opencfw_boot_mutex_claim_current":0x418d90,"opencfw_boot_mutex_inherit":0x418b7c,"opencfw_boot_mutex_disinherit_timeout":0x418ccc,"opencfw_boot_mutex_waiter_priority":0x41a492}
EXTRA={'opencfw_boot_platform_configure':0x41f846,'opencfw_bl_power_register_update':0x41d92c,'opencfw_boot_storage_range_valid':0x430a60,'opencfw_boot_storage_read':0x430a9c,'opencfw_boot_storage_program':0x430ac4,'opencfw_boot_storage_erase_validate':0x430aec,'opencfw_boot_mram_dispatch':0x42e4f4,'opencfw_boot_mram_aligned':0x42e514,'opencfw_boot_control_guard_begin':0x41bd92,'opencfw_boot_control_guard_end':0x41bde4,'opencfw_boot_control_mram':0x42e8a4,'opencfw_boot_control_critical_save':0x41b8ec,'opencfw_provider_4201ba':0x4201ba,'opencfw_provider_420002':0x420002,'opencfw_provider_420800':0x420800,'opencfw_provider_420890':0x420890,'opencfw_provider_420c5c':0x420c5c,'opencfw_bl_mspi_blocking_transfer':0x4262e0}
NOR_NATIVE={'opencfw_provider_4201ba','opencfw_provider_420002','opencfw_provider_420800','opencfw_provider_420890','opencfw_provider_420c5c'}
BLOCKING_PC=0x4262e0
class Machine(c.Machine):
 def __init__(self,*a,**kw):
  super().__init__(*a,**kw);MACHINES.append(self);entry_map=dict(EXTRA,**LOCAL_PROVIDERS)
  if NATIVE_MUTEX_PROFILE:entry_map.update(MUTEX_ENTRIES)
  if NATIVE_ISR_PROFILE:entry_map.update(ISR_ENTRIES)
  if NATIVE_KERNEL_STATE_PROFILE:entry_map['opencfw_boot_kernel_state']=0x416088
  if not NATIVE_NOR_PROFILE:
   for name in NOR_NATIVE|{'opencfw_bl_mspi_blocking_transfer'}:entry_map.pop(name,None)
  self.platform_entries={name:(self.symbols[name]&~1) if self.source else pc for name,pc in entry_map.items() if not self.source or name in self.symbols};self.actual_read.update(self.platform_entries.values());self.cpu.mem_map(0x0200f000,0x1000);self.rom_status=0;self.peripheral_writes=[];self.nor_transport=[];self.active_nor_transport_event=None;self.kernel_state_native_visits=0;self.nor_status2=0;self.nor_write_enabled=False;self.nor_four_byte_mode=False;self.pio_data=None;self.pio_offset=0
  if NATIVE_INITIALIZER_PROFILE and initv is not None:
   init_receipt=initv.configure(self,self.source,NATIVE_CONTEXT_IRQ_PROFILE,NATIVE_IOM_CONTEXT_PROFILE,NATIVE_IOM_CHILD_PROFILE,NATIVE_NVIC_PROFILE,NATIVE_SEMAPHORE_PROFILE,NATIVE_GPIO_DESCRIPTOR_PROFILE,NATIVE_ADC_CONTEXT_PROFILE,NATIVE_ADC_CONTROL_PROFILE,NATIVE_ADC_CONFIGURATION_PROFILE,NATIVE_ADC_SAMPLES_PROFILE,NATIVE_ADC_PROFILE_PROFILE,NATIVE_UART_PROFILE,NATIVE_SERVICE_PROFILE);self.initializer_native_entries=init_receipt['native_entries'];self.initializer_child_cuts=init_receipt['child_cuts'];self.platform_entries.update(self.initializer_native_entries)
  else:self.initializer_native_entries={};self.initializer_child_cuts={};self.initializer_events=[];self.initializer_native_visits={}
  self.initializer_active=False;self.initializer_return_pc=None;self.initializer_return_stack=[]
  self.mutex_native_visits={name:0 for name in MUTEX_ENTRIES} if NATIVE_MUTEX_PROFILE else {}
  self.initializer_visits=self.initializer_native_visits
  self.nor_entries={name:self.platform_entries[name] for name in NOR_NATIVE if name in self.platform_entries}
  self.native_nor_profile=set(self.nor_entries)==NOR_NATIVE
  self.blocking_entry=self.platform_entries.get('opencfw_bl_mspi_blocking_transfer')
  self.nor_native_visits={name:0 for name in NOR_NATIVE};self.normalized_init_table=None;self.exception_observations=[];self.interrupt_leaf_calls=[]
  if 'opencfw_boot_icache_enable' in LOCAL_PROVIDERS:
   self.cpu.mem_map(0xe001e000,0x1000)
   self.cpu.hook_add(UC_HOOK_MEM_WRITE,self.peripheral_write,begin=0xe000ef50,end=0xe000ef7f)
   self.cpu.hook_add(UC_HOOK_MEM_WRITE,self.peripheral_write,begin=0xe001e000,end=0xe001efff)
  if NATIVE_DEVICE_INFO:
   self.cpu.mem_map(0xe00fe000,0x1000)
   for name,pc in {'opencfw_boot_device_info_query':0x41d792,'opencfw_boot_device_info_initialize':0x41d294,'opencfw_boot_device_mode_configure':0x41d69c}.items():
    if not self.source or name in self.symbols:self.platform_entries[name]=(self.symbols[name]&~1) if self.source else pc
   self.actual_read.update(self.platform_entries.values())
  if NATIVE_DELAY_MATH and not any(lo==0 for lo,hi,flags in self.cpu.mem_regions()):self.cpu.mem_map(0,0x1000)
  if NATIVE_NVIC_PROFILE:self.cpu.hook_add(UC_HOOK_MEM_WRITE,self.peripheral_write,begin=0xe000e100,end=0xe000e17f)
  if NATIVE_IOM_CHILD_PROFILE:self.cpu.hook_add(UC_HOOK_MEM_WRITE,self.peripheral_write,begin=0x40050000,end=0x40057fff)
  if NATIVE_UART_PROFILE:
   for lo,hi in [(0x40039000,0x4003cfff),(0xe000e280,0xe000e2ff),(0xe000e400,0xe000e7ff)]:self.cpu.hook_add(UC_HOOK_MEM_WRITE,self.peripheral_write,begin=lo,end=hi)
  for lo,hi in [(0x40004000,0x40004fff),(0x40010000,0x40021fff),(0x40060000,0x40063fff)]:self.cpu.hook_add(UC_HOOK_MEM_WRITE,self.peripheral_write,begin=lo,end=hi)
 def peripheral_write(self,uc,access,address,size,value,user):
  # Record the actual store width; STRB hook values may retain upper register bits.
  record=[address,size,value&((1<<(size*8))-1)];self.peripheral_writes.append(record)
  if self.active_nor_transport_event is not None and 0x40060000<=address<0x40064000:
   offset=(address-0x40060000)%0x1000
   if offset==0x10:self.active_nor_transport_event['fifo_writes'].append(record.copy());self.active_nor_transport_event['fifo_write_indexes'].append(len(self.peripheral_writes)-1)
   elif offset==0x00:self.active_nor_transport_event['native_control_writes'].append(record.copy())
   elif offset==0x0c:self.active_nor_transport_event['pio_control_writes'].append(record.copy())
 def canonical_peripheral_writes(self):
  """Project TX FIFO words to the bytes actually carried by the PIO length."""
  records=[record.copy() for record in self.peripheral_writes]
  for event in self.nor_transport:
   if event['direction']!=1 or not event['fifo_writes']:continue
   remaining=event['length']
   for raw_record,index in zip(event['fifo_writes'],event['fifo_write_indexes']):
    width=max(0,min(raw_record[1],remaining));records[index][2]&=(1<<(8*width))-1 if width else 0;remaining-=width
   assert remaining==0,('TX FIFO provided fewer bytes than transfer length',event['instruction'],event['length'],event['fifo_writes'])
  return records
 def canonical_nor_transport(self):
  """Compare only transferred FIFO bytes while keeping raw words available."""
  result=[]
  for event in self.nor_transport:
   raw=b''.join((word[2]&0xffffffff).to_bytes(word[1],'little') for word in event['fifo_writes'])
   wire=raw[:event['length']] if event['direction']==1 else b''
   if event['direction']==1:
    expected_words=(event['length']+3)//4
    assert len(event['fifo_writes'])==expected_words,('FIFO word count differs from descriptor length',event['instruction'],event['length'],len(event['fifo_writes']),expected_words)
    for word in event['fifo_writes']:
     assert word[0]==0x40060000+event['module']*0x1000+0x10 and word[1]==4,('unexpected TX FIFO port/width',event['module'],word)
    assert len(event['native_control_writes'])==1,('expected one native MSPI control write per TX',event['instruction'],event['native_control_writes'])
    native_control=event['native_control_writes'][0][2]
    assert ((native_control>>16)&0xffff)==(event['length']&0xffff),('native PIO control length differs from descriptor length',event['instruction'],event['length'],hex(native_control))
    expected_control=[event['pio_control_field']] if event['pio_control_enabled'] else []
    actual_control=[word[2]&0xffff for word in event['pio_control_writes']]
    assert actual_control==expected_control,('PIO control write differs from caller 16-bit field',event['instruction'],event['pio_control_enabled'],event['pio_control_field'],actual_control)
    assert len(wire)==event['length'],('incomplete modeled FIFO transfer',event['instruction'],event['length'],event['fifo_writes'])
    assert wire.hex()==event['tx'],('FIFO wire bytes disagree with PIO source bytes',event['instruction'],event['tx'],wire.hex())
   projected={key:value for key,value in event.items() if key not in ('fifo_writes','fifo_write_indexes','return_pc')};projected['fifo_wire_bytes']=wire.hex();result.append(projected)
  return result
 def svc(self,uc,number,user):
  pc=uc.reg_read(v.a.UC_ARM_REG_PC);opcode=None
  try:opcode=bytes(uc.mem_read(pc-2,2)).hex()
  except Exception:pass
  observation=dict(number=number,phase=getattr(self,'phase',None),pc=hex(pc),opcode=opcode,lr=hex(uc.reg_read(v.a.UC_ARM_REG_LR)),control=uc.reg_read(v.a.UC_ARM_REG_CONTROL),fpccr=self.u(0xe000ef34) if any(lo<=0xe000ef34<=hi for lo,hi,*_ in uc.mem_regions()) else None)
  self.exception_observations.append(observation)
  assert number==2 and opcode=='02df',('unsupported/non-SVC-2 exception at SVC adapter',observation)
  super().svc(uc,number,user)
 def port_read(self,uc,access,address,size,value,user):
  if self.pio_data is None or not (0x40060000<=address<0x40064000) or (address-0x40060000)%0x1000!=0x14:return
  assert size==4
  word=self.pio_data[self.pio_offset:self.pio_offset+4].ljust(4,b'\0')
  uc.mem_write(address,word);self.pio_offset+=4
 def model_transfer(self,uc):
  handle,descriptor,timeout,_=self.args()
  length=self.u(descriptor)
  direction=uc.mem_read(descriptor+6,1)[0]
  instruction=int.from_bytes(uc.mem_read(descriptor+14,2),'little')
  address=self.u(descriptor+8);buffer=self.u(descriptor+20)
  tx=bytes(uc.mem_read(buffer,length)) if buffer and length and direction==1 else b''
  before=(self.nor_status2,self.nor_write_enabled,self.nor_four_byte_mode)
  rx=None
  self.pending_tx=None
  if direction==0 and instruction==0x05:rx=bytes([self.nor_status2])
  elif direction==0 and instruction==0x15:rx=bytes([0x20 if self.nor_four_byte_mode else 0])
  elif direction==0 and instruction==0x9f:rx=b'\x25\x39\xc2'
  elif direction==0 and instruction==0x6c:
   assert s.NOR<=address<=address+length<=s.NOR+s.SIZE,('NOR read outside synthetic device',hex(address),length)
   rx=bytes(uc.mem_read(address,length))
  elif direction==0 and instruction in (0x03,0x0b,0x13,0x0c):
   assert s.NOR<=address<=address+length<=s.NOR+s.SIZE,('NOR read outside synthetic device',hex(address),length)
   rx=bytes(uc.mem_read(address,length))
  elif direction==0 and length==0:rx=b''
  if direction==1:
   if instruction==0x06:self.nor_write_enabled=True;self.write_enable=True
   elif instruction==0x04:self.nor_write_enabled=False;self.write_enable=False
   elif instruction==0xb7 and self.nor_write_enabled:self.nor_four_byte_mode=True
   elif instruction==0x01 and length and self.nor_write_enabled:self.nor_status2=tx[0]
   elif instruction==0x20:
    assert self.write_enable and s.NOR<=address<=address+4096<=s.NOR+s.SIZE and address%4096==0,('invalid modeled NOR sector erase',hex(address),self.write_enable)
    uc.mem_write(address,b'\xff'*4096)
   elif instruction==0x02:self.pending_tx=[address,length,bytearray()]
  self.pio_data=rx;self.pio_offset=0
  event=dict(module=self.u(handle+4),instruction=instruction,direction=direction,length=length,tx=tx.hex(),rx=rx.hex() if rx is not None else None,timeout=timeout,state_before=list(before),state_after=[self.nor_status2,self.nor_write_enabled,self.nor_four_byte_mode],pio_control_enabled=bool(uc.mem_read(descriptor+12,1)[0]),pio_control_field=int.from_bytes(uc.mem_read(descriptor+14,2),'little'),native_control_writes=[],pio_control_writes=[],fifo_writes=[],fifo_write_indexes=[],return_pc=uc.reg_read(v.a.UC_ARM_REG_LR)&~1);self.nor_transport.append(event);self.active_nor_transport_event=event
 def code(self,uc,pc,size,user):
  # Preserve the existing seven-case ABI-level provider models after source
  # binding. Native output/TX and startup bodies are covered by dedicated
  # original-instruction suites; these integration models do not certify them.
  if self.source:
   output_entry=self.symbols.get('opencfw_boot_elog_output',0)&~1
   startup_entry=self.symbols.get('opencfw_provider_41fa50',0)&~1
   plain_entry=self.symbols.get('opencfw_boot_plain_printf',0)&~1
   if output_entry and pc==output_entry:
    if self.initializer_active and initv is not None and initv.handle_code(self,uc,pc,size,user):return
    pc=0x4176ce
   elif startup_entry!=0x41fa50 and pc==startup_entry:pc=0x41fa50
   elif plain_entry and pc==plain_entry:
    if self.initializer_active and initv is not None and initv.handle_code(self,uc,pc,size,user):return
    pc=0x415fae

  if NATIVE_ADC_CONTEXT_PROFILE and pc==0x48:
   address,out,count=self.args()[:3]
   assert address in {0x42003300,0x42003304,0x42003308,0x42003328,0x4200332c} and count==1,('unmodeled INFO request',hex(address),count)
   self.w(out,0)
   self.initializer_events.append(['adc-info-rom-zero-fixture',address,out,count])
   self.ret(0);return

  if NATIVE_KERNEL_STATE_PROFILE and pc==self.platform_entries.get('opencfw_boot_kernel_state'):self.kernel_state_native_visits+=1
  if self.active_nor_transport_event is not None and pc==self.active_nor_transport_event['return_pc']:self.active_nor_transport_event=None
  if pc==self.application_reset:self.boundary_events.append(['peripheral-write-sha256',len(self.peripheral_writes),hashlib.sha256(json.dumps(self.canonical_peripheral_writes(),separators=(",",":")).encode()).hexdigest()])
  if pc==0x40 and NATIVE_DELAY_MATH:self.boundary_events.append(['rom-delay-cycles',self.args()[0]]);self.ret();return
  if pc==0x41d792 and not NATIVE_DEVICE_INFO:
   selector,address,_,_=self.args();assert selector==1;mode=(self.u(0x40020014)>>2)&3;limit=int.from_bytes(uc.mem_read(0x43401c+2*mode,2),'little')<<10;self.w(address+0x2c,limit);self.ret();return
  if pc==0x0200ff20:
   key,operation,address,word_offset=self.args();words=self.u(uc.reg_read(v.a.UC_ARM_REG_SP));assert key==0x12344321 and operation==1;destination=0x400000+4*word_offset;assert (0x438000<=destination<=destination+4*words<=0x439000) or (0x7fe000<=destination<=destination+4*words<=0x7ff000);payload=bytes(uc.mem_read(address,words*4));self.boundary_events.append(['rom-mram-program',hex(destination),words,hashlib.sha256(payload).hexdigest(),self.rom_status]);
   if self.rom_status==0:uc.mem_write(destination,payload)
   self.ret(self.rom_status);return
  # Scope child providers to actual initializer frames. The table dispatcher
  # can tail through callback bodies that enter platform helpers, so keep a
  # return stack for the dispatcher and each callback instead of a single LR.
  if self.initializer_return_stack and pc==self.initializer_return_stack[-1][1]:
   completed_name,_=self.initializer_return_stack.pop()
   # The allocator-init row is the final priority-26 table callback. Stock
   # falls back to startup through a tail path, so the dispatcher LR is not a
   # reliable end marker; this callback return is the bounded window end.
   if completed_name=='opencfw_boot_allocator_init':self.initializer_return_stack.clear()
  initializer_frame_names={'opencfw_boot_init_table_default','opencfw_boot_init_callback_platform_sequence','opencfw_boot_init_callback_services','opencfw_boot_init_callback_redirect','opencfw_boot_allocator_init','opencfw_bl_platform_bringup','opencfw_bl_post_bringup_setup','opencfw_bl_platform_finish'}
  frame_entries={name:entry for name,entry in self.initializer_native_entries.items() if name in initializer_frame_names}
  if pc in frame_entries.values() and (pc==self.initializer_native_entries.get('opencfw_boot_init_table_default') or self.initializer_active):
   return_pc=uc.reg_read(v.a.UC_ARM_REG_LR)&~1
   if return_pc:
    frame_name=next(name for name,entry in frame_entries.items() if entry==pc)
    self.initializer_return_stack.append((frame_name,return_pc))
  self.initializer_active=bool(self.initializer_return_stack)
  irq_entry=self.initializer_child_cuts.get('platform-interrupt-enable')
  if pc==irq_entry:self.interrupt_leaf_calls.append(dict(lr=hex(uc.reg_read(v.a.UC_ARM_REG_LR)&~1),args=[hex(x) for x in self.args()[:3]],active=self.initializer_active))
  if pc==0x08002100:
   self.initializer_events.append(['allocator-log',4,self.args()[0]]);self.ret();return
  if pc==0x4176ce and self.u(uc.reg_read(v.a.UC_ARM_REG_SP))==0x13:
   self.initializer_events.append(['allocator-log',self.args()[0],0x13]);self.ret();return
  if self.initializer_native_entries and self.initializer_active:
   if initv.handle_code(self,uc,pc,size,user):return
  for name in self.mutex_native_visits:
   if pc==self.platform_entries[name]:self.mutex_native_visits[name]+=1
  for name,key,count in [('opencfw_boot_storage_read','image_read',1),('opencfw_boot_storage_program','image_program',1),('opencfw_boot_storage_erase_validate','image_erase',1)]:
   if pc==self.platform_entries[name]:self.storage_counts[key]+=count
  # In particular this bypasses the earlier41f846 descriptor substitution.
  for name,entry in self.nor_entries.items():
   if pc==entry:self.nor_native_visits[name]+=1
  for name,entry in self.initializer_native_entries.items():
   if pc==entry:
    if name=='opencfw_boot_init_table_default' and initv is not None:
     raw=bytes(uc.mem_read(self.initializer_table_address,initv.TABLE_SIZE));rows=[]
     for offset in range(0,len(raw),8):
      target,priority=struct.unpack_from('<II',raw,offset);label=None
      for symbol,stock_pc,_ in initv.CALLBACKS:
       expected=(self.symbols[symbol]&~1) if self.source else stock_pc
       if (target&~1)==expected:label=symbol;break
      rows.append([label,priority])
     self.normalized_init_table=rows
  if pc==self.blocking_entry:self.model_transfer(uc)
  if pc in self.platform_entries.values():
   assert any(lo<=pc<hi for lo,hi in self.exec_ranges)
   if not self.source:self.trace[hex(pc)]=bytes(uc.mem_read(pc,size)).hex()
   return
  super().code(uc,pc,size,user)
def main():
 global NATIVE_DEVICE_INFO,NATIVE_DELAY_MATH,NATIVE_NOR_PROFILE,NATIVE_INITIALIZER_PROFILE,NATIVE_KERNEL_STATE_PROFILE,NATIVE_CONTEXT_IRQ_PROFILE,NATIVE_IOM_CONTEXT_PROFILE,NATIVE_IOM_CHILD_PROFILE
 elf_arg=Path(sys.argv[sys.argv.index('--elf')+1]);_,_,source_symbols=v.elf.elf_info(elf_arg);configure_profiles(source_symbols)
 return run_profile()

def configure_profiles(source_symbols):
 global NATIVE_MUTEX_PROFILE,NATIVE_ISR_PROFILE
 global NATIVE_NVIC_PROFILE,NATIVE_SEMAPHORE_PROFILE,NATIVE_GPIO_DESCRIPTOR_PROFILE,NATIVE_ADC_CONTEXT_PROFILE,NATIVE_ADC_CONTROL_PROFILE,NATIVE_ADC_CONFIGURATION_PROFILE,NATIVE_ADC_SAMPLES_PROFILE,NATIVE_ADC_PROFILE_PROFILE,NATIVE_UART_PROFILE,NATIVE_SERVICE_PROFILE
 NATIVE_SERVICE_PROFILE="opencfw_boot_service_mutex_initialize" in source_symbols
 NATIVE_MUTEX_PROFILE="opencfw_bl_kernel_mutex_take_plain" in source_symbols
 NATIVE_ISR_PROFILE="opencfw_boot_pend_callback_isr" in source_symbols
 NATIVE_UART_PROFILE="opencfw_boot_uart_baud" in source_symbols and source_symbols["opencfw_boot_uart_baud"]<0x410000
 NATIVE_ADC_PROFILE_PROFILE="opencfw_bl_adc_profile_transfer" in source_symbols and source_symbols["opencfw_bl_adc_profile_transfer"]<0x410000
 NATIVE_ADC_SAMPLES_PROFILE="opencfw_bl_adc_enumerate" in source_symbols and source_symbols["opencfw_bl_adc_enumerate"]<0x410000
 NATIVE_ADC_CONFIGURATION_PROFILE="opencfw_bl_adc_context_configure" in source_symbols and source_symbols["opencfw_bl_adc_context_configure"]<0x410000
 NATIVE_ADC_CONTROL_PROFILE="opencfw_bl_adc_configure" in source_symbols and source_symbols["opencfw_bl_adc_configure"]<0x410000
 NATIVE_ADC_CONTEXT_PROFILE="opencfw_bl_adc_context_initialize" in source_symbols and source_symbols["opencfw_bl_adc_context_initialize"]<0x410000
 NATIVE_GPIO_DESCRIPTOR_PROFILE="opencfw_bl_descriptor_register" in source_symbols and source_symbols["opencfw_bl_descriptor_register"]<0x410000
 NATIVE_SEMAPHORE_PROFILE="opencfw_boot_semaphore_create" in source_symbols
 NATIVE_NVIC_PROFILE="opencfw_boot_context_nvic_enable" in source_symbols
 global NATIVE_DEVICE_INFO,NATIVE_DELAY_MATH,NATIVE_NOR_PROFILE,NATIVE_INITIALIZER_PROFILE,NATIVE_KERNEL_STATE_PROFILE,NATIVE_CONTEXT_IRQ_PROFILE,NATIVE_IOM_CONTEXT_PROFILE,NATIVE_IOM_CHILD_PROFILE
 NATIVE_DEVICE_INFO=True
 NATIVE_IOM_CHILD_PROFILE=initv is not None and set(initv.IOM_CHILD_ENTRIES)<=set(source_symbols)
 NATIVE_IOM_CONTEXT_PROFILE=all(name in source_symbols and source_symbols.get(alias)==source_symbols[name] for name,alias in [('opencfw_boot_context_claim','opencfw_bl_context_claim'),('opencfw_boot_context_transaction','opencfw_bl_config_transaction')])
 NATIVE_CONTEXT_IRQ_PROFILE=('opencfw_boot_context_interrupt_enable' in source_symbols and source_symbols.get('opencfw_bl_context_interrupt_enable')==source_symbols['opencfw_boot_context_interrupt_enable'])
 NATIVE_KERNEL_STATE_PROFILE=('opencfw_boot_kernel_state' in source_symbols and source_symbols.get('opencfw_bl_kernel_state')==source_symbols['opencfw_boot_kernel_state'])
 NATIVE_NOR_PROFILE={'opencfw_provider_4201ba','opencfw_provider_420002','opencfw_provider_420800','opencfw_provider_420890','opencfw_provider_420c5c','opencfw_bl_mspi_blocking_transfer'}<=set(source_symbols)
 initializer_required={'opencfw_boot_init_table_default','opencfw_boot_init_sort','opencfw_boot_init_priority_compare','opencfw_boot_init_callback_platform_sequence','opencfw_boot_init_callback_services','opencfw_boot_init_callback_redirect','opencfw_boot_allocator_init','opencfw_bl_platform_bringup','opencfw_bl_post_bringup_setup','opencfw_bl_platform_finish'}
 NATIVE_INITIALIZER_PROFILE=initializer_required<=set(source_symbols)
 NATIVE_DELAY_MATH=bool(NATIVE_DELAY_MATH or NATIVE_INITIALIZER_PROFILE or 'opencfw_boot_delay_us_math' in source_symbols)
 if NATIVE_INITIALIZER_PROFILE and initv is None:raise RuntimeError('source ELF contains native initializer callbacks but initializer_callbacks/integration.py is unavailable')
 return dict(nor=NATIVE_NOR_PROFILE,initializer=NATIVE_INITIALIZER_PROFILE,delay_math=NATIVE_DELAY_MATH)

def initializer_state(machine):
 state=dict(service_bytes=bytes(machine.cpu.mem_read(0x200267d8,0x1e)).hex(),adc_result=bytes(machine.cpu.mem_read(0x20027018,8)).hex(),redirect_mutex_slots=[machine.u(0x2002712c),machine.u(0x20027130)],platform_semaphore=machine.u(0x20027104),platform_context_handles=[machine.u(0x20026ed8+4*i) for i in range(8)],nor_timing_first_six=bytes(machine.cpu.mem_read(0x2000023c,6)).hex())
 if NATIVE_MUTEX_PROFILE:state.update(mutex_objects={hex(machine.u(a)):bytes(machine.cpu.mem_read(machine.u(a),80)).hex() for a in [0x200270e8,0x2002712c,0x20027130] if machine.u(a)},current_tcb=hex(machine.u(0x20027134)))
 if NATIVE_SERVICE_PROFILE:state.update(service_record_region=bytes(machine.cpu.mem_read(0x20026700,256)).hex(),service_mutex=machine.u(0x200270e8))
 if NATIVE_ADC_CONTEXT_PROFILE:
  state.update(adc_context=bytes(machine.cpu.mem_read(0x20026df0,72)).hex(),adc_trims=bytes(machine.cpu.mem_read(0x20026fc0,16)).hex(),adc_pair=bytes(machine.cpu.mem_read(0x20026fe0,8)).hex(),adc_pair_valid=machine.u(0x20027198)>>8&255,adc_flag=machine.u(0x2002702c))
 if NATIVE_ADC_PROFILE_PROFILE:state.update(adc_power_control=machine.u(0x40021004),adc_clock_users=[machine.u(0x20026e94),machine.u(0x20026e98)])
 if NATIVE_ADC_SAMPLES_PROFILE:state.update(adc_config=machine.u(0x40038000),adc_interrupt_enable=machine.u(0x40038200),adc_command_register=machine.u(0x40038008),adc_fifo_fixture_reads=machine.adc_sample_index)
 if NATIVE_ADC_CONFIGURATION_PROFILE:state.update(adc_context_register=machine.u(0x40038040),adc_channel_registers=[machine.u(0x4003800c+4*i) for i in range(8)])
 if NATIVE_ADC_CONTROL_PROFILE:state.update(adc_temperature_cache=machine.u(0x20027028))
 if NATIVE_IOM_CHILD_PROFILE:
  state.update(iom_pool_sha256=hashlib.sha256(machine.cpu.mem_read(0x2001455c,8*0x8a8)).hexdigest(),iom_prefixes=[list(struct.unpack('<2I',machine.cpu.mem_read(0x2001455c+i*0x8a8,8))) for i in range(8)],iom_transfers=[machine.u(0x20000374+i*16+4) for i in range(8)],iom_queue_states_sha256=hashlib.sha256(machine.cpu.mem_read(0x200262f0,12*44)).hexdigest(),iom_source_instance_configs={hex(address):bytes(machine.cpu.mem_read(address,20)).hex() for address in (0x2000034c,0x20000360)})
 return state
def nor_debug_summary(machine):
 return [dict(instruction=hex(e['instruction']),direction=e['direction'],length=e['length'],tx=e['tx'],fifo_words=[hex(w[2]) for w in e['fifo_writes']]) for e in machine.nor_transport[-8:]]

def run_profile():
 s.Machine=Machine
 try:s.main()
 except AssertionError:
  out=Path(sys.argv[sys.argv.index('--output')+1]);pairs=[]
  for left,right in zip(MACHINES[::2],MACHINES[1::2]):
   msp=right.cpu.reg_read(v.a.UC_ARM_REG_MSP);frame=None
   try:frame=bytes(right.cpu.mem_read(msp,32)).hex()
   except Exception:pass
   print('platform-profile-debug',dict(source=right.source,phase=getattr(right,'phase',None),reason=getattr(right,'reason',None),interrupt=getattr(right,'interrupt',None),exception_observations=right.exception_observations,svc_frame_address=hex(msp),svc_frame=frame,interrupt_leaf_calls=right.interrupt_leaf_calls,sp=hex(right.cpu.reg_read(v.a.UC_ARM_REG_SP)),msp=hex(msp),psp=hex(right.cpu.reg_read(v.a.UC_ARM_REG_PSP)),nor_native_visits=right.nor_native_visits,nor_command_counts=dict(Counter(hex(e['instruction']) for e in right.nor_transport)),nor_recent=nor_debug_summary(right),initializer_active=right.initializer_active,initializer_returns=right.initializer_return_stack,native_visits=right.initializer_native_visits,child_visits={k:v for k,v in right.initializer_child_visits.items() if v},events=right.initializer_events[-12:]))
   diffs=[dict(index=i,stock=a,source=b) for i,(a,b) in enumerate(zip(left.peripheral_writes,right.peripheral_writes)) if a!=b]
   pairs.append(dict(stock_writes=len(left.peripheral_writes),source_writes=len(right.peripheral_writes),first_differences=diffs[:32],stock_tail=left.peripheral_writes[-8:],source_tail=right.peripheral_writes[-8:]))
  out.parent.mkdir(parents=True,exist_ok=True);out.with_name('peripheral-divergence.json').write_text(json.dumps(pairs,indent=2)+'\n');raise
 except Exception:
  for m in MACHINES:
   msp=m.cpu.reg_read(v.a.UC_ARM_REG_MSP);frame=None
   try:frame=bytes(m.cpu.mem_read(msp,32)).hex()
   except Exception:pass
   print('platform-profile-debug',dict(source=m.source,phase=getattr(m,'phase',None),reason=getattr(m,'reason',None),interrupt=getattr(m,'interrupt',None),exception_observations=m.exception_observations,svc_frame_address=hex(msp),svc_frame=frame,interrupt_leaf_calls=m.interrupt_leaf_calls,pc=hex(m.cpu.reg_read(v.a.UC_ARM_REG_PC)),lr=hex(m.cpu.reg_read(v.a.UC_ARM_REG_LR)),nor_native_visits=m.nor_native_visits,nor_command_counts=dict(Counter(hex(e['instruction']) for e in m.nor_transport)),nor_recent=nor_debug_summary(m),initializer_active=m.initializer_active,initializer_returns=m.initializer_return_stack,native_visits=m.initializer_native_visits,child_visits={k:v for k,v in m.initializer_child_visits.items() if v},events=m.initializer_events[-12:]))
  raise
 out=Path(sys.argv[sys.argv.index('--output')+1]);r=json.loads(out.read_text());transport_pairs=[]
 for left,right in zip(MACHINES[::2],MACHINES[1::2]):
  if NATIVE_KERNEL_STATE_PROFILE:
   assert left.kernel_state_native_visits==right.kernel_state_native_visits,('kernel-state native path not matched/exercised',left.kernel_state_native_visits,right.kernel_state_native_visits)
  if left.native_nor_profile and right.native_nor_profile:
   left_canonical=left.canonical_nor_transport();right_canonical=right.canonical_nor_transport();assert left_canonical==right_canonical
   left_peripheral=left.canonical_peripheral_writes();right_peripheral=right.canonical_peripheral_writes();assert left_peripheral==right_peripheral,('canonical peripheral write mismatch',[(i,a,b) for i,(a,b) in enumerate(zip(left_peripheral,right_peripheral)) if a!=b][:8])
   assert left.nor_native_visits==right.nor_native_visits,('NOR native entry visit mismatch',left.nor_native_visits,right.nor_native_visits)
   assert all(left.nor_native_visits[name]>0 for name in NOR_NATIVE),('missing native NOR execution',left.nor_native_visits)
   commands={event['instruction'] for event in left.nor_transport}
   assert {0x05,0x15,0x01,0x04,0x06,0xb7,0x9f}<=commands,('missing modeled NOR transaction',commands)
   assert any(event['instruction']==0x9f and event['rx']=='2539c2' for event in left.nor_transport)
   padding=[]
   for event,source_event in zip(left.nor_transport,right.nor_transport):
    if event['direction']==1 and event['length']%4 and event['fifo_writes']:
     width=event['length']%4;mask=(1<<(8*width))-1;stock_raw=event['fifo_writes'][-1][2];source_raw=source_event['fifo_writes'][-1][2]
     if (stock_raw&~mask) or (source_raw&~mask):padding.append(dict(instruction=hex(event['instruction']),length=event['length'],wire_bytes=event['tx'],stock_last_fifo_word=hex(stock_raw),source_last_fifo_word=hex(source_raw),unused_stock_padding=hex(stock_raw&~mask),unused_source_padding=hex(source_raw&~mask),pio_control_field=event['pio_control_field'],pio_control_writes=[hex(x[2]) for x in event['pio_control_writes']]))
   raw_differences=[dict(index=i,stock=a,source=b) for i,(a,b) in enumerate(zip(left.peripheral_writes,right.peripheral_writes)) if a!=b]
   transport_pairs.append(dict(status='PASS',events=len(left.nor_transport),commands={hex(x):sum(e['instruction']==x for e in left.nor_transport) for x in sorted(commands)},native_entries=left.nor_native_visits,final_nor_device_state=[left.nor_status2,left.nor_write_enabled,left.nor_four_byte_mode],fifo_padding_records=padding,raw_peripheral_writes=dict(stock=len(left.peripheral_writes),source=len(right.peripheral_writes),stock_sha256=hashlib.sha256(json.dumps(left.peripheral_writes,separators=(",",":")).encode()).hexdigest(),source_sha256=hashlib.sha256(json.dumps(right.peripheral_writes,separators=(",",":")).encode()).hexdigest(),first_differences=raw_differences[:16])))
  else:transport_pairs.append(dict(status='not-enabled-missing-source-symbols',missing=sorted(NOR_NATIVE-set(right.nor_entries))))
  if left.initializer_native_entries and right.initializer_native_entries:
   left_events=initv.normalize_initializer_events(left.initializer_events);right_events=initv.normalize_initializer_events(right.initializer_events);assert left_events==right_events,('initializer native callflow mismatch',left_events,right_events)
   retained=right.initializer_native_entries.keys()
   left_semantic,left_diagnostic=initv.split_initializer_native_visits(left.initializer_native_visits);right_semantic,right_diagnostic=initv.split_initializer_native_visits(right.initializer_native_visits)
   left_counts={name:left_semantic.get(name,0) for name in retained if name in left_semantic};right_counts={name:right_semantic.get(name,0) for name in retained if name in right_semantic}
   assert left_counts==right_counts,('initializer native counts mismatch',left_counts,right_counts)
   assert all(left_diagnostic.get(name,0)>0 and right_diagnostic.get(name,0)>0 for name in left_diagnostic.keys()|right_diagnostic.keys()),('initializer comparator was not exercised',left_diagnostic,right_diagnostic)
   assert left.normalized_init_table==right.normalized_init_table,('initializer table data mismatch',left.normalized_init_table,right.normalized_init_table)
   left_initializer_state=initializer_state(left);right_initializer_state=initializer_state(right)
   assert left_initializer_state==right_initializer_state,('initializer state mismatch',left_initializer_state,right_initializer_state)
  else:pass
 r['iom_initializer_execution']=dict(enabled=NATIVE_IOM_CHILD_PROFILE,fixture='Eight synthetic IOM blocks expose subtype0/subtype1 mode fields0x20 and idle acknowledgement4; MMIO RAM does not simulate asynchronous queue consumption, peripheral timing or physical register read-only fields.')
 r['kernel_state_execution']=dict(enabled=NATIVE_KERNEL_STATE_PROFILE,case_pairs=[dict(stock=left.kernel_state_native_visits,source=right.kernel_state_native_visits) for left,right in zip(MACHINES[::2],MACHINES[1::2])],scope='Stock416088/source no-argument uint32 wrapper and runtime flag query execute; scheduler/IRQ delivery remains modeled.')
 r['nor_transport_model']=dict(status='PASS' if NATIVE_NOR_PROFILE else 'not-enabled',case_pairs=transport_pairs,inputs={'status_05':'status register 2 starts at 0; write-register 1 updates it after WREN','status_15':'bit 5 follows the synthetic B7 four-byte-mode state','wren_wrdi':'commands 06 and 04 toggle the synthetic write-enable state','write_01':'writes one transmitted status byte when write-enabled','enter_b7':'sets synthetic four-byte mode only when write-enabled','jedec_9f':'wire response bytes are 25 39 c2; the source explicitly assembles numeric JEDEC ID 0x2539c2 from those bytes','fifo_tx':'Each TX event must emit exactly ceil(length/4) 32-bit writes to module FIFO offset 0x10; payload bytes must match descriptor TX bytes. Raw unused upper bytes of a final partial FIFO word are retained in diagnostics but excluded from effective-wire comparison after length and caller control writes are checked.'},table_provenance='Profile bytes at 0x20000244 remain the exact initializer/scatter output from the locked 0x20000000..0x2000055b scatter region; no standalone table fixture was added.')
 r['initializer_execution']=dict(status='PASS' if NATIVE_INITIALIZER_PROFILE else 'not-enabled-missing-source-symbols',case_pairs=[dict(callflow=initv.normalize_initializer_events(left.initializer_events),raw_callflow=left.initializer_events,semantic_native_entries=initv.split_initializer_native_visits(left.initializer_native_visits)[0],comparator_diagnostic_counts=initv.split_initializer_native_visits(left.initializer_native_visits)[1],normalized_callback_records=left.normalized_init_table,state=initializer_state(left)) for left in MACHINES[::2]])
 r['limits'][3]='Actual scatter descriptor200001e8/callbacks430a9c/ac4/aec retained; native platform configuration and storage read/program/erase-validation wrappers, critical/MRAM guard and ROM bridge execute. ROM0200ff20 is a status/write callback; Full native mode1 device-info41d792→41d294 executes and supplies cache word11, including actual volatile reads and ten delay calls; core-debug/peripheral values and delays remain modeled. NOR timing wrapper/scanner, address-mode check/setter, and status-register mode switch execute stock/source instructions; the 24-byte blocking-transfer/FIFO/status-poll bodies execute against a synthetic SPI device at the transaction boundary. No erase operation or physical MRAM/NOR atomicity, timing, or coherence claim. Filesystem mutex/delay and selected logging remain modeled.'
 r['source_sha256'].update({str(x.relative_to(s.ROOT)):v.sha(x) for folder in ['nor_read','nor_write','nor_mspi_power','nor_mspi_queue','clock_manager','platform_control','platform_startup','application_storage'] for x in (s.ROOT/'g2/components/bootloader'/folder).iterdir() if x.suffix in ['.c','.h','.S']});out.write_text(json.dumps(r,indent=2)+'\n')
if __name__=='__main__':main()
