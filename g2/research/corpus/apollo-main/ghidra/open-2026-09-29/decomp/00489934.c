
int FUN_00489934(char *param_1,uint param_2,int param_3,int param_4)

{
  int iVar1;
  int iVar2;
  uint local_28;
  uint local_24;
  int local_20;
  int iStack_1c;
  
  if (param_1 == (char *)0x0) {
    iVar1 = 0;
  }
  else if (param_3 == 0) {
    iVar1 = 0;
  }
  else if (*param_1 == '\0') {
    iVar1 = 0;
  }
  else {
    local_28 = 0;
    iVar1 = 0;
    local_24 = param_2;
    local_20 = param_3;
    iStack_1c = param_4;
    if (param_2 != 0) {
      while (local_28 < param_2) {
        FUN_00489b3c(param_1,&local_20,&local_24,&local_28);
        iVar2 = FUN_004d57f4(param_3,local_20,local_24);
        if (0 < iVar2) {
          iVar1 = param_4 + iVar2 + iVar1;
        }
      }
      if (0 < iVar1) {
        iVar1 = iVar1 - param_4;
      }
    }
  }
  return iVar1;
}

