
undefined4 FUN_0045fcb2(int param_1)

{
  int iVar1;
  
  if (param_1 != 0) {
    for (iVar1 = *(int *)(param_1 + 8); iVar1 != 0; iVar1 = *(int *)(iVar1 + 0x20)) {
      if (*(char *)(iVar1 + 0x1c) == '\x02') {
        return 1;
      }
    }
  }
  return 0;
}

