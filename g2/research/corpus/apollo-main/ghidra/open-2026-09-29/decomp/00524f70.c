
void ft_validator_init(int param_1,undefined4 param_2,undefined4 param_3,undefined1 param_4)

{
  *(undefined4 *)(param_1 + 0x80) = param_2;
  *(undefined4 *)(param_1 + 0x84) = param_3;
  *(undefined1 *)(param_1 + 0x88) = param_4;
  *(undefined4 *)(param_1 + 0x8c) = 0;
  return;
}

