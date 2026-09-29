
int FUN_00415a08(uint param_1,uint param_2,char *param_3,char param_4)

{
  uint uVar1;
  int iVar2;
  int iVar3;
  char cVar4;
  char cVar5;
  char acStack_21 [21];
  
  iVar2 = 0;
  if ((param_2 == 0) && (param_1 == 0)) {
    acStack_21[1] = 0x30;
    iVar2 = 1;
  }
  for (; (param_2 != 0 || (param_1 != 0)); param_1 = param_1 >> 4 | uVar1) {
    cVar4 = (char)(param_1 & 0xf);
    if (9 < (param_1 & 0xf)) {
      if (param_4 == '\0') {
        cVar5 = '\a';
      }
      else {
        cVar5 = '\'';
      }
      cVar4 = cVar5 + cVar4;
    }
    acStack_21[iVar2 + 1] = cVar4 + '0';
    iVar2 = iVar2 + 1;
    uVar1 = param_2 << 0x1c;
    param_2 = param_2 >> 4;
  }
  iVar3 = iVar2;
  if (param_3 != (char *)0x0) {
    while (iVar3 != 0) {
      *param_3 = acStack_21[iVar3];
      param_3 = param_3 + 1;
      iVar3 = iVar3 + -1;
    }
    *param_3 = '\0';
  }
  return iVar2;
}

