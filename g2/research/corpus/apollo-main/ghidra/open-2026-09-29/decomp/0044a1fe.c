
void SVC_SystemTimeSync(undefined4 param_1,char param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined1 auStack_38 [4];
  int local_34;
  int local_2c;
  undefined4 local_28;
  undefined4 local_24;
  undefined4 local_20;
  undefined4 local_1c;
  undefined4 local_18;
  undefined4 uStack_10;
  
  uStack_10 = param_4;
  service_time_epoch_to_calendar24(param_1,auStack_38);
  DRV_RtcSetTime(auStack_38);
  FUN_0043c0e4(auStack_38,0x28,0);
  service_time_current_calendar_get(auStack_38);
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    FUN_0043d574(4,DAT_0044a420,DAT_0044a41c,DAT_0044a418,0xbd,DAT_0044a414,local_2c + 2000,local_28
                 ,local_24,local_20,local_1c,local_18,*(undefined4 *)(DAT_0044a410 + local_34 * 4),
                 (int)param_2);
  }
  iVar1 = FUN_0043d0ce();
  if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
    compress_log_output(0x12000000,DAT_0044a424,DAT_0044a424,local_2c + 2000,local_28,local_24,
                        local_20,local_1c,local_18,*(undefined4 *)(DAT_0044a410 + local_34 * 4),
                        (int)param_2);
  }
  return;
}

