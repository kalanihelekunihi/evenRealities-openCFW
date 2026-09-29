
undefined4 af_autofitter_init(int param_1)

{
  *(undefined4 *)(param_1 + 0xc) = 0x53;
  *(undefined4 *)(param_1 + 0x10) = 0x1e;
  *(undefined1 *)(param_1 + 0x14) = 0;
  *(undefined1 *)(param_1 + 0x15) = 1;
  *(undefined4 *)(param_1 + 0x18) = 500;
  *(undefined4 *)(param_1 + 0x1c) = 400;
  *(undefined4 *)(param_1 + 0x20) = 1000;
  *(undefined4 *)(param_1 + 0x24) = 0x113;
  *(undefined4 *)(param_1 + 0x28) = 0x683;
  *(undefined4 *)(param_1 + 0x2c) = 0x113;
  *(undefined4 *)(param_1 + 0x30) = 0x91d;
  *(undefined4 *)(param_1 + 0x34) = 0;
  return 0;
}

