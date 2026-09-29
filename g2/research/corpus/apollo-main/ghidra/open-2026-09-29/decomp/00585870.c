
uint FUN_00585870(int param_1,int param_2,uint param_3)

{
  uint uVar1;
  
  uVar1 = 0xffffffff;
  FUN_0043c0e4(param_1,param_2 + 7U >> 3,0xff);
  if (param_3 != 0) {
    uVar1 = param_3 - 1 >> 3;
    *(byte *)(param_1 + uVar1) = 0xffU >> (param_3 & 7) & *(byte *)(param_1 + uVar1);
  }
  return uVar1;
}

