
void touch_clock_1434_calibrate(void)

{
  char cVar1;
  int iVar2;
  
  iVar2 = touch_platform_13f8_rounded_measurement();
  if (iVar2 != 0) {
    *DAT_0000476c = iVar2;
    cVar1 = __aeabi_uidiv(iVar2 + -1,DAT_00004770);
    *DAT_00004774 = cVar1 + '\x01';
    iVar2 = __aeabi_uidiv(iVar2 + -1,1000);
    *DAT_00004778 = iVar2 + 1;
    *DAT_0000477c = (iVar2 + 1) * 0x8000;
  }
  return;
}

