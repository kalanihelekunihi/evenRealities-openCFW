
int compute_glyph_metrics(int *param_1,undefined4 param_2)

{
  short sVar1;
  byte *pbVar2;
  int iVar3;
  int *piVar4;
  int iVar5;
  undefined4 uVar6;
  int iVar7;
  int iVar8;
  uint uVar9;
  int local_40;
  int local_3c;
  int local_38;
  int local_34;
  undefined4 local_30;
  int local_2c;
  uint local_28;
  
  iVar3 = *param_1;
  iVar8 = *(int *)(iVar3 + 0x60);
  iVar5 = param_1[2];
  iVar7 = param_1[1];
  uVar6 = 0x10000;
  if (-1 < (int)((uint)*(byte *)(param_1 + 4) << 0x1f)) {
    uVar6 = *(undefined4 *)(*(int *)(iVar7 + 0x2c) + 8);
  }
  if (*(int *)(iVar5 + 0x48) == DAT_005f1558) {
    FUN_00439c04(&local_40,param_1 + 9,0x10);
  }
  else {
    FT_Outline_Get_CBox(iVar5 + 0x6c,&local_40);
  }
  *(int *)(iVar5 + 0x38) = param_1[0xf];
  *(int *)(iVar5 + 0x20) = local_40;
  *(int *)(iVar5 + 0x24) = local_34;
  *(int *)(iVar5 + 0x28) = param_1[0x13] - param_1[0x11];
  if (((((*(int *)(iVar8 + 0x40) != 0x28) || (param_1[0x27] == 0)) ||
       (*(char *)(param_1[0x27] + 0x267) == '\0')) &&
      ((*(int *)(iVar3 + 0x1e8) == 0 && ((param_1[4] & DAT_005f155c) == 0)))) &&
     (pbVar2 = (byte *)tt_face_get_device_metrics(iVar3,**(undefined2 **)(iVar7 + 0x2c),param_2),
     pbVar2 != (byte *)0x0)) {
    *(uint *)(iVar5 + 0x28) = (uint)*pbVar2 << 6;
  }
  *(int *)(iVar5 + 0x18) = local_38 - local_40;
  *(int *)(iVar5 + 0x1c) = local_34 - local_3c;
  if ((*(char *)(iVar3 + 0x124) == '\0') || (*(short *)(iVar3 + 0x14a) == 0)) {
    sVar1 = FT_DivFix(local_34 - local_3c,uVar6);
    if (*(short *)(iVar3 + 0x174) == -1) {
      uVar9 = (int)*(short *)(iVar3 + 0xdc) - (int)*(short *)(iVar3 + 0xde);
    }
    else {
      uVar9 = (int)*(short *)(iVar3 + 0x1ba) - (int)*(short *)(iVar3 + 0x1bc);
    }
    iVar7 = (int)(uVar9 - (int)sVar1) / 2;
  }
  else {
    sVar1 = FT_DivFix(param_1[0x2e] - local_34,uVar6);
    iVar7 = (int)sVar1;
    if (param_1[0x30] < param_1[0x2e]) {
      uVar9 = FT_DivFix(param_1[0x2e] - param_1[0x30],uVar6);
      uVar9 = uVar9 & 0xffff;
    }
    else {
      uVar9 = 0;
    }
  }
  piVar4 = *(int **)(*(int *)(iVar3 + 0x80) + 0x34);
  if ((piVar4 != (int *)0x0) && (*(int *)(*piVar4 + 8) != 0)) {
    local_30 = 0;
    local_2c = iVar7;
    local_28 = uVar9;
    iVar3 = (**(code **)(*piVar4 + 8))(piVar4[1],param_2,1,&local_30);
    iVar7 = local_2c;
    uVar9 = local_28;
    if (iVar3 != 0) {
      return iVar3;
    }
  }
  *(uint *)(iVar5 + 0x3c) = uVar9;
  if (-1 < (int)((uint)*(byte *)(param_1 + 4) << 0x1f)) {
    iVar7 = FT_MulFix(iVar7,uVar6);
    uVar9 = FT_MulFix(uVar9,uVar6);
  }
  *(int *)(iVar5 + 0x2c) = *(int *)(iVar5 + 0x20) - *(int *)(iVar5 + 0x28) / 2;
  *(int *)(iVar5 + 0x30) = iVar7;
  *(uint *)(iVar5 + 0x34) = uVar9;
  return 0;
}

