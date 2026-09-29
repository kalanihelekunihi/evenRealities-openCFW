
undefined8 FUN_0055d5e2(undefined4 *param_1,undefined1 param_2,undefined4 param_3,uint param_4)

{
  undefined4 uVar1;
  int iVar2;
  
  if (param_1 == (undefined4 *)0x0) {
    uVar1 = 0xffffffff;
  }
  else if ((uint)param_1[4] < param_4) {
    uVar1 = 0xfffffffb;
  }
  else {
    iVar2 = (*(code *)param_1[2])(*param_1,param_2,param_3,param_4);
    if ((*(char *)(param_1 + 5) != '\0') && (*(undefined1 *)(param_1 + 5) = 0, iVar2 != 0)) {
      iVar2 = (*(code *)param_1[2])(*param_1,param_2,param_3,param_4);
    }
    if (iVar2 == 0) {
      uVar1 = 0;
    }
    else {
      uVar1 = 0xfffffffd;
    }
  }
  return CONCAT44(param_4,uVar1);
}

