
int FUN_005d16a2(int param_1,undefined4 param_2,undefined4 param_3)

{
  int iVar1;
  
  iVar1 = 0;
  if (*(char *)(param_1 + 0x40) == '\0') {
    *(undefined1 *)(param_1 + 0x40) = 1;
    iVar1 = FUN_005d1640(param_1);
    if (iVar1 == 0) {
      iVar1 = FUN_005d161a(param_1,param_2,param_3);
    }
  }
  return iVar1;
}

