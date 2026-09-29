
undefined4 gx8002_aout_resume(int param_1)

{
  func_0x10025080(0xb,1);
  func_0x10025080(0xf,1);
  if (*(char *)(param_1 + 0x1b) != '\0') {
    uRam00000008 = uRam00000008 | 1;
  }
  if (*(char *)(param_1 + 0x1a) != '\0') {
    *(undefined1 *)(param_1 + 0x1a) = 0;
  }
  return 0;
}

