
void setting_notify_recalibration_status_to_app
               (undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined1 auStack_74 [8];
  undefined2 uStack_6c;
  undefined2 uStack_68;
  undefined4 uStack_64;
  undefined4 uStack_c;
  
  uStack_c = param_4;
  FUN_0048949c(auStack_74,0x68);
  auStack_74[0] = 3;
  uStack_6c = 5;
  uStack_68 = 1;
  uStack_64 = param_1;
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    FUN_0043d574(3,DAT_0049c02c,DAT_0049c028,PTR_s_setting_notify_recalibration_sta_0049c05c,0x1b0,
                 PTR_s__Notify_Recalibration_Status__st_0049c058,param_1);
  }
  iVar1 = FUN_0043d0ce();
  if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
    compress_log_output(0xc400000,PTR_s__pb_service_setting__Notify_Reca_0049c060,
                        PTR_s__pb_service_setting__Notify_Reca_0049c060,param_1);
  }
  setting_notify_common(auStack_74);
  return;
}

