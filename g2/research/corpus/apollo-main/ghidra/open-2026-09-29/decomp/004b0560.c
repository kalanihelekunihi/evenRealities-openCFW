
undefined4 FUN_004b0560(int param_1,uint param_2,int param_3)

{
  uint uVar1;
  
  uVar1 = 0;
  while( true ) {
    if (param_2 <= uVar1) {
      return DAT_004b1038;
    }
    if (*(int *)(param_1 + uVar1 * 8) == param_3) break;
    uVar1 = uVar1 + 1;
  }
  return *(undefined4 *)(param_1 + uVar1 * 8 + 4);
}

