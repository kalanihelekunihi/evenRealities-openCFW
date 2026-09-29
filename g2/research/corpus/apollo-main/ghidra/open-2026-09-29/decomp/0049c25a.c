
undefined8 FUN_0049c25a(undefined4 param_1,undefined *param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 uVar1;
  int iVar2;
  
  uVar1 = service_ancc_message_count_get();
  iVar2 = FUN_0043d0ce();
  if (iVar2 << 0x1e < 0) {
    param_1 = 0xa7;
    param_2 = PTR_s_dashboard_send_initial_notificat_0049cd18;
    FUN_0043d574(4,PTR_s_dashboard_0049cb30,DAT_0049cb2c,
                 PTR_s_dashboard_send_initial_notificat_0049cd1c,0xa7,
                 PTR_s_dashboard_send_initial_notificat_0049cd18,uVar1,param_4);
  }
  iVar2 = FUN_0043d0ce();
  if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
    compress_log_output(0x10400000,PTR_s__dashboard_dashboard_send_initia_0049cd20,
                        PTR_s__dashboard_dashboard_send_initia_0049cd20,uVar1);
  }
  FUN_0049c146(uVar1);
  return CONCAT44(param_2,param_1);
}

