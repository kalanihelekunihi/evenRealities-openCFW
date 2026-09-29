
undefined4
ble_param_reset_delayed_event
          (undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 uVar1;
  
  uVar1 = DAT_00478724;
  fw_event_loop_remove_delayed(DAT_00478724);
  fw_event_loop_push_delayed(uVar1,0xa4,param_1);
  return param_4;
}

