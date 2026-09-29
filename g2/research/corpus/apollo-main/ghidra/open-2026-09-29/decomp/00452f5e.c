
void FUN_00452f5e(char *param_1,undefined4 *param_2)

{
  if (param_1 == (char *)0x0) {
    *param_2 = 0;
    param_2[1] = 0;
  }
  else if ((*param_1 == '\x01') || (*param_1 == '\x03')) {
    *param_2 = *(undefined4 *)(param_1 + 0x30);
    param_2[1] = *(undefined4 *)(param_1 + 0x34);
  }
  else {
    *param_2 = 0xffffffff;
    param_2[1] = 0xffffffff;
  }
  return;
}

