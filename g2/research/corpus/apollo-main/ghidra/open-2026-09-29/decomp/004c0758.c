
uint FUN_004c0758(int param_1,char param_2,char param_3,uint param_4)

{
  bool bVar1;
  uint uVar2;
  
  uVar2 = FUN_00473940();
  if (param_2 == '\0') {
    *DAT_004c0f60 = *DAT_004c0f60 & ~(1 << (param_1 * 5 & 0xffU));
  }
  else {
    if (param_3 != '\0') {
      *DAT_004c0f60 =
           ((param_4 & 0xff) << 1) << (param_1 * 5 & 0xffU) |
           *DAT_004c0f60 & ~(0x1e << (param_1 * 5 & 0xffU));
    }
    *DAT_004c0f60 = 1 << (param_1 * 5 & 0xffU) | *DAT_004c0f60;
    FUN_004807a0(10);
  }
  bVar1 = (bool)isCurrentModePrivileged();
  if (bVar1) {
    enableIRQinterrupts((uVar2 & 1) == 1);
  }
  return uVar2;
}

