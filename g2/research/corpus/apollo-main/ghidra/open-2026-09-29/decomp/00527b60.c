
undefined4
FT_Vector_Transform(int *param_1,undefined4 *param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  
  if ((param_1 != (int *)0x0) && (param_2 != (undefined4 *)0x0)) {
    iVar1 = FT_MulFix(*param_1,*param_2);
    iVar2 = FT_MulFix(param_1[1],param_2[1]);
    iVar3 = FT_MulFix(*param_1,param_2[2]);
    iVar4 = FT_MulFix(param_1[1],param_2[3]);
    *param_1 = iVar2 + iVar1;
    param_1[1] = iVar4 + iVar3;
  }
  return param_4;
}

