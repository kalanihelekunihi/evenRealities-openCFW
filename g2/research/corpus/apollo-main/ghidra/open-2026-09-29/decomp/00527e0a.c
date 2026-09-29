
undefined4 FT_Outline_Get_Orientation(short *param_1)

{
  undefined4 uVar1;
  int iVar2;
  uint uVar3;
  int iVar4;
  int iVar5;
  uint uVar6;
  int iVar7;
  int iVar8;
  int iVar9;
  int iVar10;
  int iVar11;
  int iVar12;
  uint local_38;
  int local_34;
  uint local_30;
  int local_2c;
  
  iVar10 = 0;
  if ((param_1 == (short *)0x0) || (param_1[1] < 1)) {
    uVar1 = 0;
  }
  else {
    FT_Outline_Get_CBox(param_1,&local_38);
    if ((local_38 == local_30) || (local_34 == local_2c)) {
      uVar1 = 2;
    }
    else {
      if ((int)local_30 < 0) {
        local_30 = -local_30;
      }
      if ((int)local_38 < 0) {
        local_38 = -local_38;
      }
      iVar2 = FT_MSB(local_30 | local_38);
      uVar3 = iVar2 - 0xe;
      if ((int)uVar3 < 1) {
        uVar3 = 0;
      }
      iVar2 = FT_MSB(local_2c - local_34);
      uVar6 = iVar2 - 0xe;
      if ((int)uVar6 < 1) {
        uVar6 = 0;
      }
      iVar2 = *(int *)(param_1 + 2);
      iVar12 = 0;
      for (iVar7 = 0; iVar7 < *param_1; iVar7 = iVar7 + 1) {
        iVar11 = (int)*(short *)(*(int *)(param_1 + 6) + iVar7 * 2);
        iVar8 = *(int *)(iVar2 + iVar11 * 8) >> (uVar3 & 0xff);
        iVar9 = *(int *)(iVar2 + iVar11 * 8 + 4) >> (uVar6 & 0xff);
        for (; iVar12 <= iVar11; iVar12 = iVar12 + 1) {
          iVar4 = *(int *)(iVar2 + iVar12 * 8) >> (uVar3 & 0xff);
          iVar5 = *(int *)(iVar2 + iVar12 * 8 + 4) >> (uVar6 & 0xff);
          iVar10 = (iVar8 + iVar4) * (iVar5 - iVar9) + iVar10;
          iVar8 = iVar4;
          iVar9 = iVar5;
        }
        iVar12 = iVar11 + 1;
      }
      if (iVar10 < 1) {
        if (iVar10 < 0) {
          uVar1 = 0;
        }
        else {
          uVar1 = 2;
        }
      }
      else {
        uVar1 = 1;
      }
    }
  }
  return uVar1;
}

