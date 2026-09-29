
uint mspi_clkgen_ctrl(int param_1,char param_2,char param_3,uint param_4)

{
  bool bVar1;
  uint uVar2;
  
  uVar2 = critical_save();
  if (param_2 == '\0') {
    *DAT_004251a8 = *DAT_004251a8 & ~(1 << (param_1 * 5 & 0xffU));
  }
  else {
    if (param_3 != '\0') {
      *DAT_004251a8 =
           ((param_4 & 0xff) << 1) << (param_1 * 5 & 0xffU) |
           *DAT_004251a8 & ~(0x1e << (param_1 * 5 & 0xffU));
    }
    *DAT_004251a8 = 1 << (param_1 * 5 & 0xffU) | *DAT_004251a8;
    delay_us(10);
  }
  bVar1 = (bool)isCurrentModePrivileged();
  if (bVar1) {
    enableIRQinterrupts((uVar2 & 1) == 1);
  }
  return uVar2;
}

