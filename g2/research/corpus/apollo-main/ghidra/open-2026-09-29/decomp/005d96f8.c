
void FUN_005d96f8(int param_1,int param_2)

{
  uint uVar1;
  
  uVar1 = 0;
  while( true ) {
    if (9 < uVar1) {
      return;
    }
    if (param_1 == *(int *)(DAT_005d9938 + uVar1 * 4)) break;
    uVar1 = uVar1 + 1;
  }
  *(undefined4 *)(param_2 + uVar1 * 4) = 2;
  return;
}

