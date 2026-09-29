
undefined4 tt_driver_init(int param_1)

{
  *(undefined4 *)(param_1 + 0x40) = 0x23;
  *(undefined4 *)(param_1 + 0x40) = 0x28;
  return 0;
}

