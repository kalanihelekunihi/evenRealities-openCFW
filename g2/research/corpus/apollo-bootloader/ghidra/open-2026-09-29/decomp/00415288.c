
void FUN_00415288(int param_1,undefined4 param_2,undefined4 param_3)

{
  int iVar1;
  
  iVar1 = lfs_mlist_isopen(*(undefined4 *)(param_1 + 0x28),param_2);
  if (iVar1 != 0) {
    FUN_00415734(DAT_00415318,DAT_0041530c,0x18ae);
  }
  FUN_0041315c(param_1,param_2,param_3);
  return;
}

