
undefined8 FUN_00584a7c(void)

{
  int *piVar1;
  undefined4 in_r3;
  int local_10;
  undefined4 uStack_c;
  
  piVar1 = DAT_00584e48;
  local_10 = 0;
  uStack_c = in_r3;
  if ((*DAT_00584e48 != 0) && (*DAT_00584e4c == '\x01')) {
    FUN_0058e80e(*DAT_00584e48,&local_10,1);
    FUN_0058e7e4(*piVar1,local_10);
    if (local_10 << 0x1b < 0) {
      FUN_00584b3c(0x20,1);
    }
    if (local_10 << 0x19 < 0) {
      FUN_00584b3c(0x20,1);
    }
    if ((local_10 << 0x14 < 0) && (*DAT_00584e50 = *DAT_00584e50 & 0xffffffef, *DAT_00584e54 != 0))
    {
      osSemaphoreRelease(*DAT_00584e54);
    }
    if (local_10 << 0x13 < 0) {
      FUN_00584a64();
      *DAT_00584e58 = 1;
      if (*DAT_00584e54 != 0) {
        osSemaphoreRelease(*DAT_00584e54);
      }
    }
    if (local_10 << 0x16 < 0) {
      *DAT_00584e5c = *DAT_00584e5c + 1;
    }
    if (local_10 << 0x17 < 0) {
      *DAT_00584e60 = *DAT_00584e60 + 1;
    }
    if (local_10 << 0x18 < 0) {
      *DAT_00584e64 = *DAT_00584e64 + 1;
    }
  }
  return CONCAT44(uStack_c,local_10);
}

