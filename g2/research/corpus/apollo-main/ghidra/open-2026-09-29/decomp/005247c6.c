
undefined4 FT_Matrix_Invert(undefined4 *param_1)

{
  undefined4 uVar1;
  int iVar2;
  int iVar3;
  undefined4 uVar4;
  
  if (param_1 == (undefined4 *)0x0) {
    uVar1 = 6;
  }
  else {
    iVar2 = FT_MulFix(*param_1,param_1[3]);
    iVar3 = FT_MulFix(param_1[1],param_1[2]);
    iVar2 = iVar2 - iVar3;
    if (iVar2 == 0) {
      uVar1 = 6;
    }
    else {
      iVar3 = FT_DivFix(param_1[1],iVar2);
      param_1[1] = -iVar3;
      iVar3 = FT_DivFix(param_1[2],iVar2);
      param_1[2] = -iVar3;
      uVar4 = *param_1;
      uVar1 = FT_DivFix(param_1[3],iVar2);
      *param_1 = uVar1;
      uVar1 = FT_DivFix(uVar4,iVar2);
      param_1[3] = uVar1;
      uVar1 = 0;
    }
  }
  return uVar1;
}

