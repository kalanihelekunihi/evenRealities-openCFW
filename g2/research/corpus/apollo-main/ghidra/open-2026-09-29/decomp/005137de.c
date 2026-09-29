
undefined4 FUN_005137de(void)

{
  byte bVar1;
  undefined4 uVar2;
  
  if ((*DAT_00513890 << 10 < 0) && (*DAT_00513890 << 4 < 0)) {
    bVar1 = (byte)*DAT_00513894 & 1 ^ 1;
  }
  else {
    bVar1 = 1;
  }
  if (bVar1 == 0) {
    do {
    } while (*DAT_00513898 << 0x1f < 0);
    uVar2 = 0;
  }
  else {
    uVar2 = 7;
  }
  return uVar2;
}

