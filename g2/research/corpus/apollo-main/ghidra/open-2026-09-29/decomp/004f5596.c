
void FUN_004f5596(void)

{
  byte bVar1;
  
  bVar1 = (byte)DAT_004f5c3c[0x1727];
  if (bVar1 == 1) {
    *DAT_004f5c3c = DAT_004f5c3c[0x1724];
  }
  else if ((bVar1 != 0) && ((bVar1 == 3 || (bVar1 < 3)))) {
    if ((uint)DAT_004f5c3c[0x1724] + (uint)*DAT_004f5c3c < 0x29) {
      *DAT_004f5c3c = DAT_004f5c3c[0x1724] + *DAT_004f5c3c;
    }
    else {
      *DAT_004f5c3c = 0x28;
    }
  }
  return;
}

