
undefined4 tt_size_init(int param_1)

{
  *(undefined4 *)(param_1 + 0x130) = 0xffffffff;
  *(undefined4 *)(param_1 + 0x134) = 0xffffffff;
  *(undefined1 *)(param_1 + 0x70) = 0;
  *(undefined4 *)(param_1 + 0x74) = 0xffffffff;
  return 0;
}

