
undefined8 FUN_00484656(int param_1,undefined4 *param_2,char param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  int iVar3;
  
  if (*(int *)(param_1 + 0x44) != 0) {
    FUN_00453604();
    iVar1 = FUN_0044fa7e();
    FUN_00453604();
    iVar2 = FUN_0044faa8();
    iVar3 = *(int *)(param_1 + 0x44);
    if ((((*(int *)(iVar3 + 0x50) != 1) && (*(int *)(iVar3 + 8) < 1)) &&
        (iVar1 + -1 <= *(int *)(iVar3 + 0x10))) &&
       ((*(int *)(iVar3 + 0xc) < 1 && (iVar2 + -1 <= *(int *)(iVar3 + 0x14))))) {
      param_2 = (undefined4 *)0x0;
      goto LAB_004846dc;
    }
  }
  if (param_2 == (undefined4 *)0x0) {
    param_2 = *(undefined4 **)(param_1 + 0x44);
  }
  else {
    param_2 = (undefined4 *)*param_2;
  }
  for (; param_2 != (undefined4 *)0x0; param_2 = (undefined4 *)*param_2) {
    if (((param_2[0x14] == 1) &&
        ((*(char *)(param_2 + 0x16) == '\0' || (*(char *)(param_2 + 0x16) == param_3)))) &&
       (iVar1 = FUN_004848b2(param_1,param_2), iVar1 != 0)) goto LAB_004846dc;
  }
  param_2 = (undefined4 *)0x0;
LAB_004846dc:
  return CONCAT44(param_4,param_2);
}

