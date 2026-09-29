
int FUN_005de970(int param_1,byte *param_2)

{
  int iVar1;
  uint uVar2;
  uint uVar3;
  byte *pbVar4;
  
  pbVar4 = param_2 + 4;
  uVar3 = (uint)param_2[3] |
          (uint)param_2[1] << 0x10 | (uint)*param_2 << 0x18 | (uint)param_2[2] << 8;
  iVar1 = FUN_005de270(param_1,uVar3 + 1);
  if (iVar1 == 0) {
    iVar1 = *(int *)(param_1 + 0x20);
    for (uVar2 = 0; uVar2 < uVar3; uVar2 = uVar2 + 1) {
      *(uint *)(iVar1 + uVar2 * 4) = (uint)pbVar4[1] << 8 | (uint)*pbVar4 << 0x10 | (uint)pbVar4[2];
      pbVar4 = pbVar4 + 5;
    }
    *(undefined4 *)(iVar1 + uVar2 * 4) = 0;
  }
  else {
    iVar1 = 0;
  }
  return iVar1;
}

