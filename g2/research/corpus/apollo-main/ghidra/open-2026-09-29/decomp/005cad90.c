
void FUN_005cad90(int param_1,int param_2,int *param_3,int *param_4)

{
  int iVar1;
  int local_1c;
  int local_18;
  
  FUN_00489546(&local_1c,*(undefined4 *)(param_2 + 0x1c),*(undefined4 *)(param_2 + 0x20),
               *(undefined4 *)(param_2 + 0x2c),*(undefined4 *)(param_2 + 0x28),0x1fffffff,0);
  if ((*(char *)(param_1 + 0x3c) == '\x01') || (*(char *)(param_1 + 0x3c) == '\0')) {
    *param_4 = *param_3 - local_1c / 2;
    param_4[2] = local_1c / 2 + *param_3;
    if (*(char *)(param_1 + 0x3c) == '\x01') {
      iVar1 = FUN_005c9dc0(param_1,0x20000);
      param_4[1] = iVar1 + param_3[1];
      param_4[3] = local_18 + param_4[1];
    }
    else {
      iVar1 = FUN_005c9db6(param_1,0x20000);
      param_4[3] = param_3[1] - iVar1;
      param_4[1] = param_4[3] - local_18;
    }
  }
  else if ((*(char *)(param_1 + 0x3c) == '\x02') || (*(char *)(param_1 + 0x3c) == '\x04')) {
    param_4[1] = param_3[1] - local_18 / 2;
    param_4[3] = local_18 / 2 + param_3[1];
    if (*(char *)(param_1 + 0x3c) == '\x02') {
      iVar1 = FUN_005c9dca(param_1,0x20000);
      *param_4 = (*param_3 - local_1c) - iVar1;
      iVar1 = FUN_005c9dca(param_1,0x20000);
      param_4[2] = *param_3 - iVar1;
    }
    else {
      iVar1 = FUN_005c9dd4(param_1,0x20000);
      *param_4 = iVar1 + *param_3;
      iVar1 = FUN_005c9dd4(param_1,0x20000);
      param_4[2] = iVar1 + local_1c + *param_3;
    }
  }
  else if ((*(char *)(param_1 + 0x3c) == '\x10') || (*(char *)(param_1 + 0x3c) == '\b')) {
    *param_4 = *param_3 - local_1c / 2;
    param_4[1] = param_3[1] - local_18 / 2;
    param_4[2] = local_1c + *param_4;
    param_4[3] = local_18 + param_4[1];
  }
  return;
}

