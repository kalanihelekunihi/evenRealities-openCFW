
int case_insensitive_strcmp(char *param_1,char *param_2)

{
  int iVar1;
  int iVar2;
  
  if ((param_1 == (char *)0x0) || (param_2 == (char *)0x0)) {
    iVar1 = 1;
  }
  else if (param_1 == param_2) {
    iVar1 = 0;
  }
  else {
    while( true ) {
      iVar1 = FUN_004d58c2(*param_1);
      iVar2 = FUN_004d58c2(*param_2);
      if (iVar1 != iVar2) break;
      if (*param_1 == '\0') {
        return 0;
      }
      param_1 = param_1 + 1;
      param_2 = param_2 + 1;
    }
    iVar1 = FUN_004d58c2(*param_1);
    iVar2 = FUN_004d58c2(*param_2);
    iVar1 = iVar1 - iVar2;
  }
  return iVar1;
}

