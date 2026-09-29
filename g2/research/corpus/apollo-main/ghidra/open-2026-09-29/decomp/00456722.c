
void _evenEfsReplyToAPP(undefined1 param_1,undefined1 param_2,undefined1 param_3,undefined4 param_4)

{
  int iVar1;
  undefined1 local_1c;
  undefined1 local_1b;
  undefined4 uStack_18;
  
  uStack_18 = param_4;
  FUN_0043c0e4(&local_1c,2,0);
  local_1c = param_2;
  local_1b = param_3;
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    FUN_0043d574(4,PTR_s_efs_service_00456bc8,PTR_s_D__01_workspace_s200_ap510b_iar__00456bc4,
                 PTR_s__evenEfsReplyToAPP_00456bc0,0x106,PTR_s_status____d_00456bbc,param_3);
  }
  iVar1 = FUN_0043d0ce();
  if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
    compress_log_output(0x10400000,PTR_s__efs_service_status____d_00456bcc,
                        PTR_s__efs_service_status____d_00456bcc,param_3);
  }
  Thread_MsgEfsTxByBle(1,param_1,&local_1c,2);
  return;
}

