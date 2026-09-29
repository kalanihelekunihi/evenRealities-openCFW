
undefined4 TT_Process_Composite_Component(int *param_1,int param_2,int param_3,uint param_4)

{
  undefined4 uVar1;
  undefined4 uVar2;
  int *piVar3;
  uint uVar4;
  int *piVar5;
  int iVar6;
  byte bVar7;
  uint uVar8;
  undefined1 auStack_30 [2];
  short local_2e;
  int local_2c;
  
  iVar6 = param_1[3];
  local_2c = *(int *)(iVar6 + 0x18) + param_4 * 8;
  local_2e = *(short *)(iVar6 + 0x16) - (short)param_4;
  bVar7 = *(byte *)(param_2 + 4) & 200;
  if (bVar7 != 0) {
    FT_Outline_Transform(auStack_30,param_2 + 0x10);
  }
  if ((int)((uint)*(byte *)(param_2 + 4) << 0x1e) < 0) {
    uVar4 = *(uint *)(param_2 + 8);
    uVar8 = *(uint *)(param_2 + 0xc);
    if (uVar8 == 0 && uVar4 == 0) {
      return 0;
    }
    if ((bVar7 != 0) && ((int)((uint)*(ushort *)(param_2 + 4) << 0x14) < 0)) {
      uVar1 = FT_Hypot(*(undefined4 *)(param_2 + 0x10),*(undefined4 *)(param_2 + 0x14));
      uVar2 = FT_Hypot(*(undefined4 *)(param_2 + 0x1c),*(undefined4 *)(param_2 + 0x18));
      uVar4 = FT_MulFix(uVar4,uVar1);
      uVar8 = FT_MulFix(uVar8,uVar2);
    }
    if (-1 < (int)((uint)*(byte *)(param_1 + 4) << 0x1f)) {
      uVar1 = *(undefined4 *)(*(int *)(param_1[1] + 0x2c) + 8);
      uVar4 = FT_MulFix(uVar4,*(undefined4 *)(*(int *)(param_1[1] + 0x2c) + 4));
      uVar8 = FT_MulFix(uVar8,uVar1);
      if (((int)((uint)*(byte *)(param_2 + 4) << 0x1d) < 0) &&
         (-1 < (int)((uint)*(byte *)(param_1 + 4) << 0x1e))) {
        if (*(int *)(*(int *)(*param_1 + 0x60) + 0x40) == 0x23) {
          uVar4 = uVar4 + 0x20 & 0xffffffc0;
        }
        uVar8 = uVar8 + 0x20 & 0xffffffc0;
      }
    }
  }
  else {
    uVar8 = param_3 + *(int *)(param_2 + 8);
    uVar4 = param_4 + *(int *)(param_2 + 0xc);
    if ((param_4 <= uVar8) || ((uint)(int)*(short *)(iVar6 + 0x16) <= uVar4)) {
      return 0x15;
    }
    piVar3 = (int *)(*(int *)(iVar6 + 0x18) + uVar8 * 8);
    piVar5 = (int *)(*(int *)(iVar6 + 0x18) + uVar4 * 8);
    uVar4 = *piVar3 - *piVar5;
    uVar8 = piVar3[1] - piVar5[1];
  }
  if (uVar8 != 0 || uVar4 != 0) {
    FT_Outline_Translate(auStack_30,uVar4,uVar8);
  }
  return 0;
}

