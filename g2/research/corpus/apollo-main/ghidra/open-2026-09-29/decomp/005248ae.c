
void FT_Vector_Transform_Scaled(int *param_1,undefined4 *param_2,int param_3)

{
  int iVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  
  param_3 = param_3 << 0x10;
  if ((param_1 != (int *)0x0) && (param_2 != (undefined4 *)0x0)) {
    iVar1 = FT_MulDiv(*param_1,*param_2,param_3);
    iVar2 = FT_MulDiv(param_1[1],param_2[1],param_3);
    iVar3 = FT_MulDiv(*param_1,param_2[2],param_3);
    iVar4 = FT_MulDiv(param_1[1],param_2[3],param_3);
    *param_1 = iVar2 + iVar1;
    param_1[1] = iVar4 + iVar3;
  }
  return;
}

