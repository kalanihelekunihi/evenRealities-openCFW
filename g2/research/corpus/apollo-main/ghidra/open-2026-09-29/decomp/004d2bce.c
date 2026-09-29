
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

longlong FUN_004d2bce(undefined4 param_1,byte *param_2,undefined *param_3,undefined *param_4)

{
  int iVar1;
  byte *pbVar2;
  undefined *puVar3;
  
  pbVar2 = param_2;
  puVar3 = param_3;
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    pbVar2 = (byte *)0x3b;
    puVar3 = PTR_s_MessageNotify_recv_data_len____d_004d341c;
    param_4 = param_3;
    FUN_0043d574(4,PTR_s_system_alert_004d3428,PTR_s_D__01_workspace_s200_ap510b_iar__004d3424,
                 PTR_s_system_alert_common_data_handler_004d3420,0x3b,
                 PTR_s_MessageNotify_recv_data_len____d_004d341c,param_3);
  }
  iVar1 = FUN_0043d0ce();
  if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
    compress_log_output(0x10400000,PTR_s__system_alert_MessageNotify_recv_004d342c,
                        PTR_s__system_alert_MessageNotify_recv_004d342c,param_3,pbVar2,puVar3,
                        param_4);
  }
  *_DAT_004d3430 = (uint)*param_2;
  iVar1 = FUN_0045a568();
  if ((iVar1 == 1) && (iVar1 = FUN_00443484(), iVar1 == 1)) {
    FUN_0045a8ee(0x21,0,0,200);
  }
  return ZEXT48(pbVar2) << 0x20;
}

