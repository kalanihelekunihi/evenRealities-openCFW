
void FUN_0052dc98(int param_1)

{
  byte bVar1;
  
  for (bVar1 = 0; bVar1 < 8; bVar1 = bVar1 + 1) {
    if (param_1 << 0x18 < 0) {
      *DAT_0052e784 = 0x80000000;
    }
    else {
      *DAT_0052e850 = 0x80000000;
    }
    *DAT_0052e784 = 0x20000000;
    *DAT_0052e850 = 0x20000000;
    param_1 = param_1 << 1;
  }
  *DAT_0052e850 = 0x80000000;
  return;
}

