
int _rxSyncEventCallback(int param_1,undefined4 param_2,int param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  
  iVar2 = param_1;
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    iVar2 = 0x13c;
    param_2 = DAT_004b99d8;
    param_3 = param_1;
    FUN_0043d574(4,PTR_s_prot_tran_004b9100,DAT_004b90fc,DAT_004b99dc,0x13c,DAT_004b99d8,param_1,
                 param_4);
  }
  iVar1 = FUN_0043d0ce();
  if (-1 < iVar1 << 0x1f) {
    iVar1 = FUN_0043d0ce();
    if (-1 < iVar1 << 0x1d) goto LAB_004b8fc4;
  }
  compress_log_output(0x10400000,DAT_004b99e0,DAT_004b99e0,param_1,iVar2,param_2,param_3);
LAB_004b8fc4:
  if (param_1 != 0) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(1,PTR_s_prot_tran_004b9100,DAT_004b90fc,DAT_004b99dc,0x13e,DAT_004b99e4,param_1);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x4400000,DAT_004b99e8,DAT_004b99e8,param_1);
    }
  }
  return param_1;
}

