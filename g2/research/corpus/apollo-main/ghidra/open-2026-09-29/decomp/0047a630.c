
int FUN_0047a630(int param_1)

{
  int iVar1;
  char cVar2;
  
  if (param_1 == 0) {
    iVar1 = DAT_0047ae64;
    for (cVar2 = '\n'; cVar2 != '\0'; cVar2 = cVar2 + -1) {
      if (*(char *)(iVar1 + 0x2f) != '\0') {
        return iVar1;
      }
      iVar1 = iVar1 + 200;
    }
  }
  else {
    for (cVar2 = '\t'; cVar2 != '\0'; cVar2 = cVar2 + -1) {
      if (*(char *)(param_1 + 0xf7) != '\0') {
        return param_1 + 200;
      }
      param_1 = param_1 + 200;
    }
  }
  return 0;
}

