
undefined8 FUN_0055f4b8(int param_1,int param_2,undefined2 param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 uVar2;
  
  uVar2 = DAT_0055f748;
  iVar1 = DAT_0055f744;
  if (*(char *)(param_1 + 4) != '\0') {
    *(undefined4 *)(DAT_0055f744 + 0x10) = DAT_0055f748;
    *(undefined4 *)(iVar1 + 0x14) = uVar2;
    *(undefined4 *)(iVar1 + 0x18) = uVar2;
    *(undefined4 *)(iVar1 + 0x1c) = uVar2;
  }
  uVar2 = DAT_0055f734;
  if (*(int *)(DAT_0055f744 + param_2 * 4) != 0) {
    uVar2 = (**(code **)(DAT_0055f744 + param_2 * 4))(param_1,param_3,param_4);
  }
  return CONCAT44(param_4,uVar2);
}

