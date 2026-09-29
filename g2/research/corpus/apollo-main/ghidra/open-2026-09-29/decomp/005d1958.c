
int FUN_005d1958(int param_1,undefined4 param_2,undefined4 param_3)

{
  int iVar1;
  
  iVar1 = 0;
  if (*(char *)(param_1 + 0x2c) == '\0') {
    *(undefined1 *)(param_1 + 0x2c) = 1;
    iVar1 = FUN_005d18ee(param_1);
    if (iVar1 == 0) {
      iVar1 = FUN_005d18c8(param_1,param_2,param_3);
    }
  }
  return iVar1;
}

