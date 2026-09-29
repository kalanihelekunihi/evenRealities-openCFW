
undefined4 gx8002_flash_otp_erase(void)

{
  short sVar1;
  int iVar2;
  int *piVar3;
  uint uVar4;
  int iVar5;
  int iVar6;
  
  iVar2 = DAT_10023c28;
  sVar1 = *(short *)(*(int *)(DAT_10023c28 + 0xc) + 6);
  if ((sVar1 == 0x5e) || (sVar1 == 0x85)) {
    piVar3 = *(int **)(*(int *)(DAT_10023c28 + 0xc) + 0x14);
    uVar4 = piVar3[4];
    iVar5 = *piVar3;
    iVar6 = piVar3[1];
    *(undefined1 *)(DAT_10023c28 + 0x10) = 0x44;
    gx8002_flash_wait_ready();
    gx8002_flash_write_enable();
    sflash_addr2cmd_isra_0(DAT_10023c2c + -8,iVar5 + (uVar4 & 7) * iVar6);
    gx8002_flash_command_write(*(undefined1 *)(iVar2 + 0x10),DAT_10023c30,3);
    gx8002_flash_wait_ready();
  }
  return 0;
}

