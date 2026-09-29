
int FUN_005d99c0(int param_1,int param_2,uint param_3)

{
  int iVar1;
  int iVar2;
  uint uVar3;
  uint uVar4;
  
  iVar2 = 0;
  uVar3 = *(uint *)(param_1 + 0xc);
  do {
    if (uVar3 < *(uint *)(param_1 + 0x10)) {
      iVar1 = -uVar3;
    }
    else {
      iVar1 = *(int *)(param_1 + 8) - uVar3;
    }
    uVar4 = (*(uint *)(param_1 + 0x10) + iVar1) - 1;
    if (*(int *)(param_1 + 8) - uVar3 <= uVar4) {
      uVar4 = *(int *)(param_1 + 8) - uVar3;
    }
    if (param_3 <= uVar4) {
      uVar4 = param_3;
    }
    FUN_00439be4(*(int *)(param_1 + 4) + uVar3,param_2,uVar4);
    iVar2 = uVar4 + iVar2;
    param_2 = param_2 + uVar4;
    param_3 = param_3 - uVar4;
    uVar3 = uVar4 + uVar3;
    if (uVar3 == *(uint *)(param_1 + 8)) {
      uVar3 = 0;
    }
    DataMemoryBarrier(0x1f);
    *(uint *)(param_1 + 0xc) = uVar3;
  } while (param_3 != 0);
  return iVar2;
}

