
undefined4
central_schedule_master_connect_004a2618
          (undefined4 param_1,char param_2,undefined4 param_3,undefined4 param_4)

{
  undefined2 uVar1;
  
  central_cancel_connect_retry_work_004a17f4();
  *DAT_004a2fcc = 2;
  uVar1 = 1;
  if (param_2 != '\0') {
    uVar1 = 0x81;
  }
  fw_event_loop_push_delayed(DAT_004a311c,uVar1,param_1);
  return param_4;
}

