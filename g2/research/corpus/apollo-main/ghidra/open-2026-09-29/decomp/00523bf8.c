
undefined4 FUN_00523bf8(int *param_1,int param_2)

{
  int *piVar1;
  int iVar2;
  undefined4 *puVar3;
  int iVar4;
  int iVar5;
  int iVar6;
  int iVar7;
  
  piVar1 = DAT_0052404c;
  iVar4 = *param_1;
  DAT_0052404c[4] = iVar4;
  if (iVar4 < 1) {
    FUN_004b127c(4);
    return 0xffffffff;
  }
  *piVar1 = (int)param_1;
  iVar5 = param_1[2];
  piVar1[1] = iVar5;
  iVar6 = param_1[3];
  piVar1[2] = iVar6;
  iVar7 = ((int)(iVar4 + ((uint)(iVar4 >> 1) >> 0x1e)) >> 2) + -4;
  piVar1[3] = iVar7;
  if (param_2 != 0) {
    iVar2 = *piVar1;
    *(undefined4 *)(iVar2 + 0x10) = 0;
    *(undefined4 *)(iVar2 + 0x14) = 0;
    puVar3 = (undefined4 *)(iVar5 + iVar7 * 4);
    *puVar3 = DAT_00524050;
    puVar3[1] = iVar6;
    *(undefined4 *)(iVar5 + 8 + iVar7 * 4) = DAT_00524054;
    *(int *)(iVar5 + 0xc + iVar7 * 4) = iVar4;
    FUN_005140ea();
    FUN_00514046(0x148,0);
    FUN_00514046(0xec,piVar1[2] | 6);
    FUN_00514046(0xf0,piVar1[2]);
    FUN_00514046(0xf4,piVar1[4]);
  }
  return 0;
}

