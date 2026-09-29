
undefined4 FUN_0052e072(int param_1)

{
  undefined4 uVar1;
  
  if (*(char *)(param_1 + 8) == '\x01') {
    if (*(char *)(param_1 + 9) == '\0') {
      *(undefined1 *)(param_1 + 9) = 1;
      FUN_0055c7e8(*(undefined4 *)(param_1 + 4),0,1);
      FUN_0055c32e(*(undefined4 *)(param_1 + 4));
      uVar1 = 0;
    }
    else {
      uVar1 = 2;
    }
  }
  else {
    uVar1 = 0xc;
  }
  return uVar1;
}

