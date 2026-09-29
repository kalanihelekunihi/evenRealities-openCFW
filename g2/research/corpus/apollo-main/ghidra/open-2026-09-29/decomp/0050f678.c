
void FUN_0050f678(int param_1)

{
  uint uVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  undefined4 uVar5;
  
  if ((*(byte *)(param_1 + 0x3c) & 3) == 1) {
    uVar1 = *(uint *)(param_1 + 0x2c) / *(uint *)(param_1 + 0x38);
    *(uint *)(param_1 + 0x30) =
         *(uint *)(param_1 + 0x30) - uVar1 * (*(uint *)(param_1 + 0x30) / uVar1);
    *(uint *)(param_1 + 0x30) = uVar1 * (*(uint *)(param_1 + 0x38) >> 1) + *(int *)(param_1 + 0x30);
    *(uint *)(param_1 + 0x34) =
         *(uint *)(param_1 + 0x30) - uVar1 * (*(uint *)(param_1 + 0x30) / uVar1);
    *(uint *)(param_1 + 0x34) = uVar1 * (*(uint *)(param_1 + 0x38) >> 1) + *(int *)(param_1 + 0x34);
    iVar2 = FUN_0050e9cc(param_1,0);
    iVar3 = FUN_0050e9e0(param_1,0);
    iVar2 = *(int *)(iVar2 + 0xc);
    iVar4 = FUN_0043fe70(param_1);
    uVar5 = FUN_0050f710(param_1);
    FUN_0043f142(uVar5,(iVar4 / 2 - iVar2 / 2) - (iVar3 + iVar2) * *(int *)(param_1 + 0x30));
  }
  return;
}

