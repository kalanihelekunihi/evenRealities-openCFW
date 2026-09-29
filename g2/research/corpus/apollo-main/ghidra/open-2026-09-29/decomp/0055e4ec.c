
undefined8 FUN_0055e4ec(int param_1,undefined4 param_2,char param_3,undefined4 param_4)

{
  int iVar1;
  int local_18;
  undefined4 uStack_14;
  
  iVar1 = DAT_0055e98c;
  local_18 = 0;
  uStack_14 = param_4;
  if (param_3 == '\0') {
    FUN_0058e2d8(*(undefined4 *)(param_1 * 0x1c + DAT_0055e98c + 4),
                 *(int *)(*(int *)(param_1 * 0x1c + DAT_0055e98c + 0x10) + 8) +
                 *(int *)(*(int *)(param_1 * 0x1c + DAT_0055e98c + 0x10) + 0xc),param_2,&local_18);
    *(int *)(*(int *)(param_1 * 0x1c + iVar1 + 0x10) + 8) =
         local_18 + *(int *)(*(int *)(iVar1 + param_1 * 0x1c + 0x10) + 8);
  }
  else {
    FUN_0058e2d8(*(undefined4 *)(param_1 * 0x1c + DAT_0055e98c + 4),
                 *(int *)(*(int *)(param_1 * 0x1c + DAT_0055e98c + 0x10) + 8) +
                 *(int *)(*(int *)(param_1 * 0x1c + DAT_0055e98c + 0x10) + 0xc),param_2,&local_18);
    *(int *)(*(int *)(param_1 * 0x1c + iVar1 + 0x10) + 8) =
         local_18 + *(int *)(*(int *)(param_1 * 0x1c + iVar1 + 0x10) + 8);
    if (*(int *)(param_1 * 0x1c + iVar1 + 0x14) != 0) {
      (**(code **)(param_1 * 0x1c + iVar1 + 0x14))
                (*(undefined4 *)(*(int *)(param_1 * 0x1c + iVar1 + 0x10) + 0xc),
                 *(undefined4 *)(*(int *)(param_1 * 0x1c + iVar1 + 0x10) + 8));
    }
    *(undefined4 *)(*(int *)(iVar1 + param_1 * 0x1c + 0x10) + 8) = 0;
  }
  return CONCAT44(uStack_14,local_18);
}

