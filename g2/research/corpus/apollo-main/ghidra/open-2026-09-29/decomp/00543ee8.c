
int FUN_00543ee8(int param_1,uint param_2,uint param_3,undefined4 param_4)

{
  int iVar1;
  uint uVar2;
  uint uVar3;
  byte local_38 [32];
  undefined4 uStack_18;
  
  uStack_18 = param_4;
  iVar1 = FUN_00543cc0(param_1,*(int *)(param_1 + 0xc) * (param_2 / *(uint *)(param_1 + 0xc)));
  uVar3 = param_2;
  if ((iVar1 == 0) || (param_2 != *(uint *)(iVar1 + 0x14))) {
    for (; (uVar3 < param_3 && (uVar3 + 0x20 < param_3)); uVar3 = uVar3 + 0x1c) {
      iVar1 = FUN_00585a12(param_1,uVar3,local_38,0x20);
      if (iVar1 != 0) {
        return -1;
      }
      for (uVar2 = 0; (uVar2 < 0x1c && (uVar2 + uVar3 < param_3)); uVar2 = uVar2 + 1) {
        if (((uint)local_38[uVar2 + 1] * 0x100 + (uint)local_38[uVar2] +
             (uint)local_38[uVar2 + 2] * 0x10000 + (uint)local_38[uVar2 + 3] * 0x1000000 ==
             DAT_005448b0) && (param_2 <= (uVar2 + uVar3) - 4)) {
          return uVar2 + uVar3 + -4;
        }
      }
    }
  }
  return -1;
}

