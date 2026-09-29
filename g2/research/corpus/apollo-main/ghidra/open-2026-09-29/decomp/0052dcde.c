
uint FUN_0052dcde(void)

{
  uint uVar1;
  byte bVar2;
  
  uVar1 = 0;
  for (bVar2 = 0; bVar2 < 8; bVar2 = bVar2 + 1) {
    if (*DAT_0052e7bc << 1 < 0) {
      uVar1 = uVar1 << 1 | 1;
    }
    else {
      uVar1 = uVar1 << 1 & 0xfe;
    }
    *DAT_0052e784 = 0x20000000;
    *DAT_0052e850 = 0x20000000;
  }
  return uVar1 & 0xff;
}

