
undefined4
ble_state_skip_manual_start(char param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 uVar1;
  
  if (*DAT_00478298 != '\0') {
    *DAT_00478704 = 0xa4;
  }
  uVar1 = DAT_00478724;
  fw_event_loop_remove_delayed(DAT_00478724);
  if (param_1 != '\0') {
    fw_event_loop_push_delayed(uVar1,0xa4,60000);
  }
  fw_event_loop_push_delayed(uVar1,0xa3,0);
  return param_4;
}

