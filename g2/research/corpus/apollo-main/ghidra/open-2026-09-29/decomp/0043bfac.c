
undefined4 FUN_0043bfac(int param_1,int param_2)

{
  char *pcVar1;
  int iVar2;
  
  iVar2 = param_2 + 1;
  if (param_2 < 0) {
    iVar2 = 1;
  }
  pcVar1 = (char *)(param_1 + -1);
  do {
    iVar2 = iVar2 + -1;
    if (iVar2 == 0) {
      return 1;
    }
    pcVar1 = pcVar1 + 1;
  } while (*pcVar1 != '\0');
  return 0;
}

