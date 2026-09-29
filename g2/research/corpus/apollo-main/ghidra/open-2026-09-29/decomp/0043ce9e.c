
longlong compress_log_output(uint param_1,uint param_2,undefined4 param_3,uint param_4)

{
  bool bVar1;
  int *piVar2;
  int iVar3;
  uint uVar4;
  uint uStack_4;
  
  uStack_4 = param_4;
  iVar3 = compress_log_export_active();
  piVar2 = DAT_0043d0e0;
  if (iVar3 == 0) {
    uVar4 = 0;
    bVar1 = (bool)isCurrentModePrivileged();
    if (bVar1) {
      uVar4 = getCurrentExceptionNumber();
      uVar4 = uVar4 & 0x1ff;
    }
    if ((uVar4 == 0) && (*DAT_0043d0e0 != 0)) {
      iVar3 = FUN_00441750(*DAT_0043d0e0,500);
      if (iVar3 == 1) {
        compress_log_encode_record(param_1 & 0xffc00000 | param_2 & 0x3fffff,param_3,&uStack_4);
        FUN_00441710(*piVar2);
      }
    }
  }
  return (ulonglong)param_4 << 0x20;
}

