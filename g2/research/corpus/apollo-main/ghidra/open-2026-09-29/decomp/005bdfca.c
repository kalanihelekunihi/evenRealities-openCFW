
undefined4 FUN_005bdfca(char *param_1,int param_2,undefined4 *param_3,undefined4 param_4)

{
  undefined4 uVar1;
  
  if (param_3 != (undefined4 *)0x0) {
    *param_3 = *(undefined4 *)(param_1 + 0x3c);
  }
  if ((*param_1 == '\x04') || (*param_1 == '\x05')) {
    (**(code **)(param_2 + 0x24))(*(undefined4 *)(param_2 + 0x28),*(undefined4 *)(param_1 + 0xc));
  }
  if (*param_1 == '\x06') {
    FUN_005bdfbc(*(undefined4 *)(param_1 + 4),param_2);
  }
  *param_1 = '\0';
  param_1[0x1c] = '\0';
  param_1[0x1d] = '\0';
  param_1[0x1e] = '\0';
  param_1[0x1f] = '\0';
  param_1[0x20] = '\0';
  param_1[0x21] = '\0';
  param_1[0x22] = '\0';
  param_1[0x23] = '\0';
  *(undefined4 *)(param_1 + 0x34) = *(undefined4 *)(param_1 + 0x28);
  *(undefined4 *)(param_1 + 0x30) = *(undefined4 *)(param_1 + 0x34);
  if (*(int *)(param_1 + 0x38) != 0) {
    uVar1 = (**(code **)(param_1 + 0x38))(0,0,0);
    *(undefined4 *)(param_1 + 0x3c) = uVar1;
    *(undefined4 *)(param_2 + 0x30) = uVar1;
  }
  return param_4;
}

