
void case_register_write_channel(int param_1,undefined4 param_2,int param_3)

{
  if (param_3 != 0) {
    *(undefined4 *)(param_1 + 0x18) = param_2;
    return;
  }
  *(undefined4 *)(param_1 + 0x28) = param_2;
  return;
}

