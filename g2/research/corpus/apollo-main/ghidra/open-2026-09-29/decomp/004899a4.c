
int FUN_004899a4(char *param_1,uint param_2,int param_3,int param_4,int param_5)

{
  int iVar1;
  int iVar2;
  undefined1 local_30 [4];
  uint local_2c;
  undefined4 local_28;
  undefined4 local_24;
  int iStack_20;
  
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
    local_2c = 0;
    iVar1 = 0;
    local_30[0] = 0;
    iStack_20 = param_4;
    if (param_2 != 0) {
      while ((param_1[local_2c] != '\0' && (local_2c < param_2))) {
        FUN_00489b3c(param_1,&local_28,&local_24,&local_2c);
        if (((-1 < param_5 << 0x1c) || (iVar2 = FUN_00489652(local_30,local_28), iVar2 == 0)) &&
           (iVar2 = FUN_004d57f4(param_3,local_28,local_24), 0 < iVar2)) {
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

