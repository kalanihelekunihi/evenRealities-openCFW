
undefined4 FUN_0052e0a2(int param_1)

{
  undefined4 uVar1;
  
  if (*(char *)(param_1 + 8) == '\x01') {
    if (*(char *)(param_1 + 9) == '\0') {
      uVar1 = 0;
    }
    else {
      FUN_0055c430(*(undefined4 *)(param_1 + 4));
      FUN_0055c7e8(*(undefined4 *)(param_1 + 4),2,1);
      *(undefined1 *)(param_1 + 9) = 0;
      uVar1 = 0;
    }
  }
  else {
    uVar1 = 0xc;
  }
  return uVar1;
}

