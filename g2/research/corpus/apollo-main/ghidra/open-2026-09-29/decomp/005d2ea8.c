
undefined4 FUN_005d2ea8(int *param_1,int param_2)

{
  undefined4 uVar1;
  int iVar2;
  
  if ((*param_1 < 1) || (param_1[3] < 1)) {
    uVar1 = 0x24;
  }
  else if (param_2 < 0x8000) {
    iVar2 = FT_DivFix(0x7d00000,param_2 << 0x10);
    if ((iVar2 < *param_1) || (iVar2 < param_1[3])) {
      uVar1 = 0xa4;
    }
    else {
      uVar1 = 0;
    }
  }
  else {
    uVar1 = 0xa4;
  }
  return uVar1;
}

