
undefined4 gx8002_flash_otp_status(byte *param_1)

{
  short sVar1;
  int iVar2;
  undefined4 uVar3;
  uint uVar4;
  
  iVar2 = DAT_10023b20;
  uVar4 = *(uint *)(*(int *)(*(int *)(DAT_10023b20 + 0xc) + 0x14) + 0x10);
  gx8002_flash_wait_ready();
  sVar1 = *(short *)(*(int *)(iVar2 + 0xc) + 6);
  if ((sVar1 == 0x5e) || (sVar1 == 0x85)) {
    iVar2 = gx8002_flash_read_status2();
    *param_1 = (byte)(iVar2 >> (uVar4 & 7) + 3) & 1;
    uVar3 = 0;
  }
  else {
    uVar3 = 0xffffffff;
  }
  return uVar3;
}

