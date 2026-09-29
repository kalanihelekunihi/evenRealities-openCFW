
undefined4 gx8002_aout_free(int param_1)

{
  uRam00000008 = uRam00000008 & 0xfffffffe;
  uRam00000014 = 0;
  uRam00000018 = 0;
  gx8002_memset(param_1 + 0x10,0,0x24);
  if ((param_1 != 0) && (*(char *)(param_1 + 4) != '\0')) {
    *(undefined1 *)(param_1 + 4) = 0;
  }
  return 0;
}

