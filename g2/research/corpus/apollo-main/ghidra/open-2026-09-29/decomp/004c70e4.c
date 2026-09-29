
undefined * FUN_004c70e4(int param_1)

{
  int iVar1;
  
  iVar1 = FUN_00454768(param_1);
  while( true ) {
    if (iVar1 == 0) {
      return &DAT_004c7328;
    }
    if (*(char *)(param_1 + iVar1) == '.') break;
    if ((*(char *)(param_1 + iVar1) == '/') || (*(char *)(param_1 + iVar1) == '\\')) {
      return &DAT_004c7328;
    }
    iVar1 = iVar1 + -1;
  }
  return (undefined *)(iVar1 + param_1 + 1);
}

