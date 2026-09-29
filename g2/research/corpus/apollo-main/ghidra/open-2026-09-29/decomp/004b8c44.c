
undefined4
tpl_schedule_rx_timeout_004b8c44
          (undefined1 param_1,undefined1 param_2,undefined1 param_3,undefined4 param_4)

{
  undefined1 *puVar1;
  
  fw_event_loop_remove_delayed(0x4b8c6d);
  puVar1 = DAT_004b9618;
  DAT_004b9618[2] = param_1;
  *puVar1 = param_2;
  puVar1[1] = param_3;
  fw_event_loop_push_delayed(0x4b8c6d,puVar1,0x5dc);
  return param_4;
}

