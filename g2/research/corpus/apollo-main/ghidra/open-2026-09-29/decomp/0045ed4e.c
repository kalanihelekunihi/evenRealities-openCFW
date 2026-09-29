
undefined4 FUN_0045ed4e(int *param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  
  iVar2 = *param_1;
  iVar1 = *(int *)(iVar2 + 0x10);
  *(undefined1 *)(iVar1 + 0x1c) = 1;
  iVar2 = FUN_0045fcd2(iVar2);
  if (*(int *)(iVar1 + 0x18) != 0) {
    (**(code **)(iVar1 + 0x18))(iVar1,iVar2,0x4d,0);
  }
  FUN_0045bbd2();
  if (iVar2 != 0) {
    *(undefined1 *)(iVar2 + 0xe8) = 0;
    FUN_0045fd06(iVar2);
  }
  return param_4;
}

