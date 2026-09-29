
int FUN_00415a7c(char *param_1)

{
  int iVar1;
  
  iVar1 = 0;
  if (param_1 != (char *)0x0) {
    while (*param_1 != '\0') {
      iVar1 = iVar1 + 1;
      param_1 = param_1 + 1;
    }
  }
  return iVar1;
}

