
undefined8 FUN_005c3838(int *param_1,int param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  int iVar3;
  
  iVar2 = *param_1;
  iVar3 = *param_1;
  while (iVar2 != 0) {
    iVar1 = (*(code *)param_1[1])(*(undefined4 *)(param_2 + 0x10),*(undefined4 *)(iVar2 + 0x10));
    iVar3 = iVar2;
    if (iVar1 < 0) {
      iVar2 = *(int *)(iVar2 + 4);
    }
    else {
      iVar2 = *(int *)(iVar2 + 8);
    }
  }
  return CONCAT44(param_4,iVar3);
}

