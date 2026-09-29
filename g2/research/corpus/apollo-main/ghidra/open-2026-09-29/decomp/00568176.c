
undefined1 FUN_00568176(int *param_1,undefined4 *param_2,undefined4 *param_3,undefined4 *param_4)

{
  bool bVar1;
  bool bVar2;
  undefined1 uVar3;
  undefined4 uVar4;
  int iVar5;
  bool bVar6;
  int iVar7;
  int iVar8;
  int iVar9;
  int iVar10;
  int iVar11;
  
  iVar7 = param_1[4] - param_1[6];
  iVar8 = param_1[5] - param_1[7];
  iVar9 = param_1[2] - param_1[4];
  iVar10 = param_1[3] - param_1[5];
  iVar11 = *param_1 - param_1[2];
  iVar5 = param_1[1] - param_1[3];
  if ((iVar7 + 1U < 3) && (iVar8 + 1U < 3)) {
    bVar6 = true;
  }
  else {
    bVar6 = false;
  }
  if ((iVar9 + 1U < 3) && (iVar10 + 1U < 3)) {
    bVar1 = true;
  }
  else {
    bVar1 = false;
  }
  if ((iVar11 + 1U < 3) && (iVar5 + 1U < 3)) {
    bVar2 = true;
  }
  else {
    bVar2 = false;
  }
  if (bVar6) {
    if (bVar1) {
      if (!bVar2) {
        uVar4 = FT_Atan2(iVar11,iVar5);
        *param_4 = uVar4;
        *param_3 = uVar4;
        *param_2 = uVar4;
      }
    }
    else if (bVar2) {
      uVar4 = FT_Atan2(iVar9,iVar10);
      *param_4 = uVar4;
      *param_3 = uVar4;
      *param_2 = uVar4;
    }
    else {
      uVar4 = FT_Atan2(iVar9,iVar10);
      *param_3 = uVar4;
      *param_2 = uVar4;
      uVar4 = FT_Atan2(iVar11,iVar5);
      *param_4 = uVar4;
    }
  }
  else if (bVar1) {
    if (bVar2) {
      uVar4 = FT_Atan2(iVar7,iVar8);
      *param_4 = uVar4;
      *param_3 = uVar4;
      *param_2 = uVar4;
    }
    else {
      uVar4 = FT_Atan2(iVar7,iVar8);
      *param_2 = uVar4;
      uVar4 = FT_Atan2(iVar11,iVar5);
      *param_4 = uVar4;
      uVar4 = FUN_00568160(*param_2,*param_4);
      *param_3 = uVar4;
    }
  }
  else if (bVar2) {
    uVar4 = FT_Atan2(iVar7,iVar8);
    *param_2 = uVar4;
    uVar4 = FT_Atan2(iVar9,iVar10);
    *param_4 = uVar4;
    *param_3 = uVar4;
  }
  else {
    uVar4 = FT_Atan2(iVar7,iVar8);
    *param_2 = uVar4;
    uVar4 = FT_Atan2(iVar9,iVar10);
    *param_3 = uVar4;
    uVar4 = FT_Atan2(iVar11,iVar5);
    *param_4 = uVar4;
  }
  FT_Angle_Diff(*param_2,*param_3);
  iVar5 = FUN_00567fc6();
  FT_Angle_Diff(*param_3,*param_4);
  iVar7 = FUN_00567fc6();
  if ((iVar5 < 0x168000) && (iVar7 < 0x168000)) {
    uVar3 = 1;
  }
  else {
    uVar3 = 0;
  }
  return uVar3;
}

