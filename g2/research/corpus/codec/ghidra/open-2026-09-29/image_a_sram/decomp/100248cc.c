
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void gx8002_otp_lowpower_enter(void)

{
  int iStack_14;
  
  iStack_14 = 0;
  gx8002_flash_otp_configuration(&iStack_14);
  if (iStack_14 == 0x8002) {
    _DAT_a0000024 = _DAT_a0000024 & 0xfffc16ff | 0x6800;
    _DAT_a0000028 = _DAT_a0000028 & 0xfffc1eff | 0x6000;
    _DAT_a0000038 = _DAT_a0000038 & 0xffffffef;
    _DAT_a0000034 = 0xf;
    gx8002_clock_switch_1m();
    stub();
    stub();
    *(undefined4 *)(iRam1002493c + 4) = 5;
    stub();
    stub();
    uRama0000000 = 1;
    stub();
  }
  return;
}

