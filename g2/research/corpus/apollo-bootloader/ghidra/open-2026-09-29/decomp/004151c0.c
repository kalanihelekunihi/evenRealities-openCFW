
void FUN_004151c0(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  
  iVar1 = lfs_mlist_isopen(*(undefined4 *)(param_1 + 0x28),param_2,param_3,param_4,param_4);
  if (iVar1 == 0) {
    FUN_00415734(DAT_00415314,DAT_0041530c,0x182d);
  }
  FUN_00413ca8(param_1,param_2,param_3,param_4);
  return;
}

