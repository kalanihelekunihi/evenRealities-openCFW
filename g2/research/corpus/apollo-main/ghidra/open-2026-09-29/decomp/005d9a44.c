
void FUN_005d9a44(int param_1,int param_2,uint param_3)

{
  uint uVar1;
  int iVar2;
  
  iVar2 = *(int *)(param_1 + 0xc);
  uVar1 = *(int *)(param_1 + 8) - iVar2;
  if (param_3 < uVar1) {
    FUN_00439be4(*(int *)(param_1 + 4) + iVar2,param_2,param_3);
    DataMemoryBarrier(0x1f);
    *(uint *)(param_1 + 0xc) = param_3 + iVar2;
  }
  else {
    FUN_00439be4(iVar2 + *(int *)(param_1 + 4),param_2,uVar1);
    FUN_00439be4(*(undefined4 *)(param_1 + 4),param_2 + uVar1,param_3 - uVar1);
    DataMemoryBarrier(0x1f);
    *(uint *)(param_1 + 0xc) = param_3 - uVar1;
  }
  return;
}

