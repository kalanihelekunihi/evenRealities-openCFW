
undefined4 gx8002_flash_otp_lock(void)

{
  short sVar1;
  int iVar2;
  undefined4 uVar3;
  uint uVar4;
  undefined1 uStack_10;
  byte bStack_f;
  
  iVar2 = DAT_100242b0;
  uVar4 = *(uint *)(*(int *)(*(int *)(DAT_100242b0 + 0xc) + 0x14) + 0x10);
  gx8002_flash_wait_ready();
  sVar1 = *(short *)(*(int *)(iVar2 + 0xc) + 6);
  if ((sVar1 == 0x5e) || (sVar1 == 0x85)) {
    uStack_10 = gx8002_flash_read_status();
    bStack_f = gx8002_flash_read_status2();
    bStack_f = (byte)(1 << (uVar4 & 7) + 3) | bStack_f;
    gx8002_flash_wait_ready();
    gx8002_flash_write_enable();
    gx8002_flash_command_write(1,&uStack_10,2);
    uVar3 = 0;
  }
  else {
    uVar3 = 0xffffffff;
  }
  return uVar3;
}

