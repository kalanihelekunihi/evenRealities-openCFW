
undefined4 gx8002_flash_otp_configuration(undefined4 *param_1)

{
  uint uVar1;
  int iVar2;
  undefined4 uVar3;
  undefined4 uStack_14;
  undefined1 uStack_10;
  
  *param_1 = 0x8002;
  uVar1 = gx8002_clock_frequency(0xd);
  iVar2 = (*(code *)(*puRam10025d80 & 0xfffffffe))(0,0,uVar1 >> 1,0x800);
  if (iVar2 != 0) {
    uStack_14 = 0;
    uStack_10 = 0;
    iVar2 = gx_spi_flash_otp_read(iVar2,0,&uStack_14,5);
    if (-1 < iVar2) {
      uVar3 = func_0x10206ca0(PTR_s_8003A_10025d88);
      iVar2 = func_0x10206c7c(&uStack_14,PTR_s_8003A_10025d88,uVar3);
      if (iVar2 != 0) {
        return 0;
      }
      *param_1 = 0x3a;
      return 0;
    }
    func_0x10206c24(PTR_s_read_flash_otp_error_10025d84);
  }
  return 0xffffffff;
}

