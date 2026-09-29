
undefined8 _anccNotiRemoveCback(int param_1,undefined4 param_2,uint param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  
  iVar2 = param_1;
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    param_3 = (uint)*(byte *)(param_1 + 2);
    iVar2 = 0x185;
    param_2 = DAT_004bf8c4;
    FUN_0043d574(4,DAT_004bf220,DAT_004bf21c,DAT_004bf8c8,0x185,DAT_004bf8c4,param_3,param_4);
  }
  iVar1 = FUN_0043d0ce();
  if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
    compress_log_output(0x10400000,DAT_004bf8cc,DAT_004bf8cc,*(undefined1 *)(param_1 + 2),iVar2,
                        param_2,param_3);
  }
  return CONCAT44(param_2,iVar2);
}

