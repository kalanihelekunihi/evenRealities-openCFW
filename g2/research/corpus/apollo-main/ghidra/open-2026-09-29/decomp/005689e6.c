
void FUN_005689e6(int *param_1,int param_2,int param_3,int param_4)

{
  bool bVar1;
  int iVar2;
  undefined4 uVar3;
  int iVar4;
  int local_20;
  int local_1c;
  
  local_20 = param_3;
  local_1c = param_4;
  iVar2 = FT_Angle_Diff(*param_1,param_1[1]);
  iVar2 = iVar2 / 2;
  if ((((char)param_1[param_2 * 8 + 0x11] == '\0') || (param_3 == 0)) ||
     (DAT_005694dc <= iVar2 + 0x59c000U)) {
    bVar1 = false;
  }
  else {
    uVar3 = FT_Tan(iVar2);
    FT_MulFix(param_1[0xc],uVar3);
    iVar4 = FUN_00567fc6();
    if (((iVar4 == 0) || (param_1[4] < iVar4)) || (param_3 < iVar4)) {
      bVar1 = false;
    }
    else {
      bVar1 = true;
    }
  }
  if (bVar1) {
    iVar4 = *param_1;
    uVar3 = FT_Cos(iVar2);
    uVar3 = FT_DivFix(param_1[0xc],uVar3);
    FT_Vector_From_Polar(&local_20,uVar3,(int)&DAT_005a0000 + iVar2 + iVar4 + param_2 * -0xb40000);
    local_20 = param_1[2] + local_20;
    local_1c = param_1[3] + local_1c;
  }
  else {
    FT_Vector_From_Polar
              (&local_20,param_1[0xc],(int)&DAT_005a0000 + param_1[1] + param_2 * -0xb40000);
    local_20 = param_1[2] + local_20;
    local_1c = param_1[3] + local_1c;
    *(undefined1 *)(param_1 + param_2 * 8 + 0x11) = 0;
  }
  FUN_005683f2(param_1 + param_2 * 8 + 0xd,&local_20,0);
  return;
}

