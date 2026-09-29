
void fw_event_loop_push(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  undefined4 local_14;
  undefined4 local_10;
  undefined4 uStack_c;
  
  uStack_c = param_4;
  if (*DAT_00476c2c == 0) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(1,DAT_00476c04,DAT_00476c00,DAT_00476c4c,0x96,DAT_00476c48);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_00476c50,DAT_00476c50);
    }
  }
  else if ((*DAT_00476bf0 != 0) &&
          (local_14 = param_2, local_10 = param_1,
          iVar1 = osMessageQueuePut(*DAT_00476bf0,&local_14,0,param_3), iVar1 != 0)) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(1,DAT_00476c04,DAT_00476c00,DAT_00476c4c,0xa0,DAT_00476c54,iVar1);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x4400000,DAT_00476c58,DAT_00476c58,iVar1);
    }
  }
  return;
}

