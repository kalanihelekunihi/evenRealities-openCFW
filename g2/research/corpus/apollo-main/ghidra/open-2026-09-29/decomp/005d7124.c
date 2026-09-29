
void FUN_005d7124(uint *param_1,uint param_2)

{
  int iVar1;
  uint uVar2;
  int iVar3;
  undefined4 *puVar4;
  undefined4 uVar5;
  
  iVar3 = param_1[2] + param_2 * 0x1c;
  if ((param_2 < *param_1) && (-1 < (int)((uint)*(byte *)(iVar3 + 0x10) << 0x1d))) {
    *(uint *)(iVar3 + 0x10) = *(uint *)(iVar3 + 0x10) | 4;
    puVar4 = (undefined4 *)param_1[4];
    uVar2 = param_1[1];
    *(undefined4 *)(iVar3 + 0x14) = 0;
    for (; uVar2 != 0; uVar2 = uVar2 - 1) {
      uVar5 = *puVar4;
      iVar1 = FUN_005d70a4(iVar3,uVar5);
      if (iVar1 != 0) {
        *(undefined4 *)(iVar3 + 0x14) = uVar5;
        break;
      }
      puVar4 = puVar4 + 1;
    }
    if (param_1[1] < *param_1) {
      uVar2 = param_1[1];
      param_1[1] = uVar2 + 1;
      *(int *)(param_1[4] + uVar2 * 4) = iVar3;
    }
  }
  return;
}

