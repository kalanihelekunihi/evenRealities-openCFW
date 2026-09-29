
undefined4 gx8002_aout_exit(void)

{
  uRam00000020 = uRam00000020 & 0xfffffff1;
  func_0x10025080(0xb,0);
  func_0x10025080(0xf,0);
  return 0;
}

