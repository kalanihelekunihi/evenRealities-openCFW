
void FUN_004503d6(int param_1)

{
  FUN_00450398(param_1,0x60);
  *(undefined4 *)(param_1 + 0x30) = 500;
  *(undefined4 *)(param_1 + 0x24) = 0;
  *(undefined4 *)(param_1 + 0x2c) = 100;
  *(undefined4 *)(param_1 + 0x44) = 1;
  *(undefined4 *)(param_1 + 0x20) = 0x450635;
  *(byte *)(param_1 + 0x5c) = *(byte *)(param_1 + 0x5c) | 0x10;
  return;
}

