
void FT_Matrix_Multiply_Scaled(undefined4 *param_1,int *param_2,int param_3)

{
  int iVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  int iVar6;
  int iVar7;
  int iVar8;
  
  param_3 = param_3 << 0x10;
  if ((param_1 != (undefined4 *)0x0) && (param_2 != (int *)0x0)) {
    iVar1 = FT_MulDiv(*param_1,*param_2,param_3);
    iVar2 = FT_MulDiv(param_1[1],param_2[2],param_3);
    iVar3 = FT_MulDiv(*param_1,param_2[1],param_3);
    iVar4 = FT_MulDiv(param_1[1],param_2[3],param_3);
    iVar5 = FT_MulDiv(param_1[2],*param_2,param_3);
    iVar6 = FT_MulDiv(param_1[3],param_2[2],param_3);
    iVar7 = FT_MulDiv(param_1[2],param_2[1],param_3);
    iVar8 = FT_MulDiv(param_1[3],param_2[3],param_3);
    *param_2 = iVar2 + iVar1;
    param_2[1] = iVar4 + iVar3;
    param_2[2] = iVar6 + iVar5;
    param_2[3] = iVar8 + iVar7;
  }
  return;
}

