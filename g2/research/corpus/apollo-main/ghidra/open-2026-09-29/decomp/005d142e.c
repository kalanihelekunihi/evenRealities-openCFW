
int FUN_005d142e(int param_1,undefined4 param_2,undefined4 param_3)

{
  int iVar1;
  
  if (*(char *)(param_1 + 0x40) == '\x03') {
    iVar1 = 0;
  }
  else {
    *(undefined1 *)(param_1 + 0x40) = 3;
    iVar1 = FUN_005d13c4(param_1);
    if (iVar1 == 0) {
      iVar1 = FUN_005d139e(param_1,param_2,param_3);
    }
  }
  return iVar1;
}

