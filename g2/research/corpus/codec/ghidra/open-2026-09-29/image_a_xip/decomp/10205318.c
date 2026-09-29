
undefined4 aout_config_cb(int param_1,int *param_2)

{
  if (*param_2 != 0) {
    uRam00000008 = uRam00000008 | 1;
    *(int *)(param_1 + 0x28) = *param_2;
    *(undefined1 *)(param_1 + 0x1b) = 1;
  }
  if (param_2[1] != 0) {
    *(int *)(param_1 + 0x2c) = param_2[1];
    *(undefined1 *)(param_1 + 0x1a) = 0;
  }
  return 0;
}

