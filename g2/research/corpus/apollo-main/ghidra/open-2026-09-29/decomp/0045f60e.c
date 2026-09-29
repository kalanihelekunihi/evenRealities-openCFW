
undefined4 FUN_0045f60e(int *param_1,int param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  
  if ((((param_1 != (int *)0x0) && (param_2 != 0)) && (iVar1 = FUN_0045f840(param_1), iVar1 != 0))
     && (*(char *)(iVar1 + 0x1c) == '\x01')) {
    if (*(char *)(iVar1 + 0xb) == '\0') {
      FUN_0045f8ba(iVar1);
      if (param_1[1] == iVar1) {
        param_1[1] = 0;
      }
    }
    else {
      *(undefined1 *)(iVar1 + 0x1c) = 2;
      FUN_0045ef24(iVar1,0);
      if ((*param_1 == iVar1) && ((char)param_1[5] == '\0')) {
        *param_1 = 0;
        param_1[1] = param_1[3];
      }
    }
  }
  return param_4;
}

