
undefined4 FUN_004408b0(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  FUN_0043ee94(param_2,param_1 + 0x14);
  if (*(int *)(param_1 + 8) != 0) {
    FUN_00450b98(param_2,*(undefined4 *)(*(int *)(param_1 + 8) + 0x28),
                 *(undefined4 *)(*(int *)(param_1 + 8) + 0x28));
  }
  return param_4;
}

