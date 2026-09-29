
undefined4
tt_get_var_blend(int param_1,undefined4 *param_2,undefined4 *param_3,undefined4 *param_4,
                undefined4 *param_5)

{
  if (*(int *)(param_1 + 700) == 0) {
    if (param_2 != (undefined4 *)0x0) {
      *param_2 = 0;
    }
    if (param_3 != (undefined4 *)0x0) {
      *param_3 = 0;
    }
    if (param_5 != (undefined4 *)0x0) {
      *param_5 = 0;
    }
  }
  else {
    if (param_2 != (undefined4 *)0x0) {
      *param_2 = **(undefined4 **)(param_1 + 700);
    }
    if (param_3 != (undefined4 *)0x0) {
      *param_3 = *(undefined4 *)(*(int *)(param_1 + 700) + 4);
    }
    if (param_4 != (undefined4 *)0x0) {
      *param_4 = *(undefined4 *)(*(int *)(param_1 + 700) + 8);
    }
    if (param_5 != (undefined4 *)0x0) {
      *param_5 = *(undefined4 *)(*(int *)(param_1 + 700) + 0xc);
    }
  }
  return 0;
}

