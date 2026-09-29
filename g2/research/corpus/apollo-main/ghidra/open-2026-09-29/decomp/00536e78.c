
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void L2cSlaveInit(void)

{
  byte bVar1;
  
  *(undefined4 *)(DAT_00536fa0 + 0x1c) = _DAT_00536f9c;
  for (bVar1 = 0; bVar1 < 3; bVar1 = bVar1 + 1) {
    *(undefined1 *)(DAT_00536f90 + (uint)bVar1 + 0x14) = 0;
  }
  return;
}

