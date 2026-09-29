
undefined8 FUN_005c6cdc(int param_1,int param_2,uint param_3,undefined4 param_4)

{
  uint uVar1;
  int iVar2;
  uint uVar3;
  int *piVar4;
  int iVar5;
  uint uVar6;
  
  uVar1 = FUN_0043fe16(param_1);
  iVar2 = FUN_005c5772(param_1,0);
  param_2 = param_2 - iVar2;
  if (param_2 < 0) {
    uVar3 = 0;
  }
  else if ((int)uVar1 < param_2) {
    uVar3 = *(int *)(param_1 + 0x70) - 1;
  }
  else if ((*(byte *)(param_1 + 0x74) & 7) == 1) {
    uVar3 = (uint)((*(int *)(param_1 + 0x70) + -1) * param_2 + (int)uVar1 / 2) / uVar1;
  }
  else if ((*(byte *)(param_1 + 0x74) & 7) == 2) {
    uVar3 = (uint)(*(int *)(param_1 + 0x70) * param_2) / uVar1;
  }
  else if (((*(byte *)(param_1 + 0x74) & 7) == 3) &&
          (piVar4 = (int *)FUN_005c5a9a(param_1,0), piVar4 != (int *)0x0)) {
    iVar2 = 0x7fffffff;
    uVar3 = 0;
    for (uVar6 = 0; uVar6 < *(uint *)(param_1 + 0x70); uVar6 = uVar6 + 1) {
      iVar5 = FUN_004888b4(*(undefined4 *)(*piVar4 + uVar6 * 4),
                           *(undefined4 *)(param_1 + ((piVar4[4] << 0x1c) >> 0x1f) * -4 + 0x54),
                           *(undefined4 *)(param_1 + ((piVar4[4] << 0x1c) >> 0x1f) * -4 + 0x5c),0,
                           uVar1,param_4);
      param_3 = uVar1;
      if (param_2 - iVar5 < 1) {
        iVar5 = FUN_004888b4(*(undefined4 *)(*piVar4 + uVar6 * 4),
                             *(undefined4 *)(param_1 + ((piVar4[4] << 0x1c) >> 0x1f) * -4 + 0x54),
                             *(undefined4 *)(param_1 + ((piVar4[4] << 0x1c) >> 0x1f) * -4 + 0x5c),0)
        ;
        iVar5 = iVar5 - param_2;
      }
      else {
        iVar5 = FUN_004888b4(*(undefined4 *)(*piVar4 + uVar6 * 4),
                             *(undefined4 *)(param_1 + ((piVar4[4] << 0x1c) >> 0x1f) * -4 + 0x54),
                             *(undefined4 *)(param_1 + ((piVar4[4] << 0x1c) >> 0x1f) * -4 + 0x5c),0)
        ;
        iVar5 = param_2 - iVar5;
      }
      if (iVar5 < iVar2) {
        iVar2 = iVar5;
        uVar3 = uVar6;
      }
    }
  }
  else {
    uVar3 = 0;
  }
  return CONCAT44(param_3,uVar3);
}

