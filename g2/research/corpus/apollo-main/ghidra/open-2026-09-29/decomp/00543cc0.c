
int FUN_00543cc0(int param_1,int param_2)

{
  uint uVar1;
  
  uVar1 = 0;
  while( true ) {
    if (0x3f < uVar1) {
      return 0;
    }
    if (*(int *)(uVar1 * 0x18 + param_1 + 0x2ac) == param_2) break;
    uVar1 = uVar1 + 1;
  }
  return param_1 + uVar1 * 0x18 + 0x2a8;
}

