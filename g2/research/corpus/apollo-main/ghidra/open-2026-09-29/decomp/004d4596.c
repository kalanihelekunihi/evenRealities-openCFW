
undefined4 FUN_004d4596(int *param_1,uint param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 uVar1;
  int iVar2;
  uint uVar3;
  uint local_90 [32];
  undefined4 uStack_10;
  
  iVar2 = *param_1;
  if (*DAT_004d4604 << 0x1f < 0) {
    uVar1 = 3;
  }
  else if (param_2 + iVar2 < 0x11) {
    uStack_10 = param_4;
    for (uVar3 = 0; uVar3 < param_2; uVar3 = uVar3 + 1) {
      local_90[uVar3 * 2] =
           param_1[1] & 0xffffffe0U | (uint)*(byte *)(param_1 + 2) << 3 |
           (uint)*(byte *)((int)param_1 + 9) << 1 | (uint)*(byte *)((int)param_1 + 10);
      local_90[uVar3 * 2 + 1] =
           param_1[3] & 0xffffffe0U | param_1[4] << 1 | (uint)*(byte *)(param_1 + 5);
      param_1 = param_1 + 6;
    }
    FUN_004d44d2(iVar2,local_90,param_2);
    uVar1 = 0;
  }
  else {
    uVar1 = 5;
  }
  return uVar1;
}

