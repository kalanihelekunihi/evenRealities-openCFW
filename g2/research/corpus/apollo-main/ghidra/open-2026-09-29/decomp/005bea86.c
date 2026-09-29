
undefined4 FUN_005bea86(int param_1)

{
  undefined4 uVar1;
  
  if (((param_1 == 0) || (*(int *)(param_1 + 0x1c) == 0)) || (*(int *)(param_1 + 0x24) == 0)) {
    uVar1 = 0xfffffffe;
  }
  else {
    if (*(int *)(*(int *)(param_1 + 0x1c) + 0x14) != 0) {
      FUN_005bea1a(*(undefined4 *)(*(int *)(param_1 + 0x1c) + 0x14),param_1);
    }
    (**(code **)(param_1 + 0x24))(*(undefined4 *)(param_1 + 0x28),*(undefined4 *)(param_1 + 0x1c));
    *(undefined4 *)(param_1 + 0x1c) = 0;
    uVar1 = 0;
  }
  return uVar1;
}

