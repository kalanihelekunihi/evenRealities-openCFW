
void FUN_00416bf8(uint param_1,int *param_2,uint *param_3)

{
  int iVar1;
  
  if (param_1 < 0x80) {
    iVar1 = 0;
    param_1 = (int)param_1 / 4;
  }
  else {
    iVar1 = FUN_004169f2(param_1);
    param_1 = param_1 >> (iVar1 + 0xfbU & 0xff) ^ 0x20;
    iVar1 = iVar1 + -6;
  }
  *param_2 = iVar1;
  *param_3 = param_1;
  return;
}

