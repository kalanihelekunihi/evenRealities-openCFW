
void gx8002_rtc_init(void)

{
  int iVar1;
  uint uVar2;
  
  iVar1 = iRam102066f8;
  func_0x10025080(0,1);
  *(uint *)(iVar1 + 0xc) = *(uint *)(iVar1 + 0xc) | 0x10;
  uVar2 = func_0x10025210(0);
  if (uVar2 < 0x10000) {
    *(uint *)(iVar1 + 0x20) = uVar2;
    func_0x1002553c(4,PTR_gx8002_rtc_isr_10206700,0);
    gx_rtc_start_tick();
  }
  else {
    gx8002_printf(PTR_s_RTC_prescaler_error__102066fc);
  }
  return;
}

