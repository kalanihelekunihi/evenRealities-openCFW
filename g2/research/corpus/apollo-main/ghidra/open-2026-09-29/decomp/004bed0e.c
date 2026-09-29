
int _rxSyncEventCallback(int param_1,undefined4 param_2,int param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  
  iVar2 = param_1;
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    iVar2 = 0x174;
    param_2 = DAT_004bf81c;
    param_3 = param_1;
    FUN_0043d574(4,DAT_004bf220,DAT_004bf21c,DAT_004bf820,0x174,DAT_004bf81c,param_1,param_4);
  }
  iVar1 = FUN_0043d0ce();
  if (-1 < iVar1 << 0x1f) {
    iVar1 = FUN_0043d0ce();
    if (-1 < iVar1 << 0x1d) goto LAB_004bed5a;
  }
  compress_log_output(0x10400000,DAT_004bf824,DAT_004bf824,param_1,iVar2,param_2,param_3);
LAB_004bed5a:
  if (param_1 != 0) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(1,DAT_004bf220,DAT_004bf21c,DAT_004bf820,0x176,DAT_004bf828,param_1);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x4400000,DAT_004bf8b0,DAT_004bf8b0,param_1);
    }
  }
  return param_1;
}

