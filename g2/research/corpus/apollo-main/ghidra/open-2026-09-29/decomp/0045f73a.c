
undefined8 FUN_0045f73a(int *param_1,undefined4 *param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 uVar1;
  int iVar2;
  
  if (((param_1 == (int *)0x0) || (param_2 == (undefined4 *)0x0)) ||
     (*(char *)((int)param_2 + 0xb) != '\x01')) {
    uVar1 = 0;
  }
  else {
    iVar2 = FUN_0045f706(param_1,param_2);
    if (iVar2 == 0) {
      uVar1 = 0;
    }
    else if ((char)param_1[5] == '\0') {
      if (*param_1 == 0) {
        FUN_0045f58c(param_1,*param_2);
        uVar1 = 1;
      }
      else if ((undefined4 *)*param_1 == param_2) {
        uVar1 = 1;
      }
      else {
        *(undefined1 *)(param_1 + 5) = 1;
        param_1[4] = (int)param_2;
        FUN_0045f60e(param_1,*(undefined4 *)*param_1);
        uVar1 = 1;
      }
    }
    else {
      if ((param_1[4] == 0) || (*(byte *)(param_1[4] + 0x16) < *(byte *)((int)param_2 + 0x16))) {
        param_1[4] = (int)param_2;
      }
      uVar1 = 1;
    }
  }
  return CONCAT44(param_4,uVar1);
}

