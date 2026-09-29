
undefined8 FUN_005de8f6(int param_1,byte *param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 uVar2;
  uint *puVar3;
  uint uVar4;
  uint uVar5;
  
  iVar1 = FUN_005de8c2(param_2);
  uVar5 = (uint)param_2[3] |
          (uint)param_2[1] << 0x10 | (uint)*param_2 << 0x18 | (uint)param_2[2] << 8;
  iVar1 = FUN_005de270(param_1,iVar1 + 1,param_3);
  if (iVar1 == 0) {
    puVar3 = *(uint **)(param_1 + 0x20);
    for (; uVar5 != 0; uVar5 = uVar5 - 1) {
      uVar4 = (uint)param_2[6] | (uint)param_2[5] << 8 | (uint)param_2[4] << 0x10;
      iVar1 = param_2[7] + 1;
      do {
        *puVar3 = uVar4;
        uVar4 = uVar4 + 1;
        puVar3 = puVar3 + 1;
        iVar1 = iVar1 + -1;
      } while (iVar1 != 0);
      param_2 = param_2 + 4;
    }
    *puVar3 = 0;
    uVar2 = *(undefined4 *)(param_1 + 0x20);
  }
  else {
    uVar2 = 0;
  }
  return CONCAT44(param_4,uVar2);
}

