
bool FUN_00568020(int *param_1,undefined4 *param_2,undefined4 *param_3)

{
  bool bVar1;
  bool bVar2;
  undefined4 uVar3;
  int iVar4;
  int iVar5;
  int iVar6;
  int iVar7;
  
  iVar5 = param_1[2] - param_1[4];
  iVar6 = param_1[3] - param_1[5];
  iVar7 = *param_1 - param_1[2];
  iVar4 = param_1[1] - param_1[3];
  if ((iVar5 + 1U < 3) && (iVar6 + 1U < 3)) {
    bVar1 = true;
  }
  else {
    bVar1 = false;
  }
  if ((iVar7 + 1U < 3) && (iVar4 + 1U < 3)) {
    bVar2 = true;
  }
  else {
    bVar2 = false;
  }
  if (bVar1) {
    if (!bVar2) {
      uVar3 = FT_Atan2(iVar7,iVar4);
      *param_3 = uVar3;
      *param_2 = uVar3;
    }
  }
  else if (bVar2) {
    uVar3 = FT_Atan2(iVar5,iVar6);
    *param_3 = uVar3;
    *param_2 = uVar3;
  }
  else {
    uVar3 = FT_Atan2(iVar5,iVar6);
    *param_2 = uVar3;
    uVar3 = FT_Atan2(iVar7,iVar4);
    *param_3 = uVar3;
  }
  FT_Angle_Diff(*param_2,*param_3);
  iVar4 = FUN_00567fc6();
  return iVar4 < 0x1e0000;
}

