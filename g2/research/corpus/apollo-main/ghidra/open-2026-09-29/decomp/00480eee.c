
undefined4 FUN_00480eee(uint param_1,undefined4 *param_2)

{
  undefined4 uVar1;
  
  if (param_1 < 0xe0) {
    if (param_2 == (undefined4 *)0x0) {
      uVar1 = 6;
    }
    else {
      *param_2 = *(undefined4 *)(DAT_0048173c + param_1 * 4);
      uVar1 = 0;
    }
  }
  else {
    uVar1 = 5;
  }
  return uVar1;
}

