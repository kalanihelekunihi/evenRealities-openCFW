
undefined4 gx8002_flash_erase(uint param_1,int param_2)

{
  undefined4 uVar1;
  uint uVar2;
  uint uVar3;
  uint uVar4;
  int iVar5;
  int iVar6;
  
  uVar3 = *(uint *)(DAT_10023df8 + 4);
  if (param_1 < uVar3) {
    uVar2 = param_2 + param_1;
    uVar4 = param_1 & 0xfffff000;
    uVar3 = ((uVar3 < uVar2) * param_1 + (uVar3 >= uVar2) * uVar2) - uVar4;
    iVar6 = DAT_10023df8 + 0x10;
    iVar5 = DAT_10023df8 + 0x11;
    while (uVar1 = 0, uVar3 != 0) {
      uVar3 = (uint)(uVar3 < 0x1000) * 0x1000 + (uVar3 >= 0x1000) * uVar3;
      if (((uVar4 & 0x7fff) == 0) && (0xffff < uVar3)) {
        gx8002_flash_wait_ready();
        gx8002_flash_write_enable();
        sflash_addr2cmd_isra_0(DAT_10023dfc,uVar4,iVar6);
        gx8002_flash_command_write(0xd8,iVar5,3);
        gx8002_flash_wait_ready();
        uVar4 = uVar4 + 0x10000;
      }
      else {
        gx8002_flash_wait_ready();
        gx8002_flash_write_enable();
        sflash_addr2cmd_isra_0(DAT_10023dfc,uVar4,iVar6);
        gx8002_flash_command_write(0x20,iVar5,3);
        gx8002_flash_wait_ready();
        uVar4 = uVar4 + 0x1000;
        uVar3 = uVar3 - 0x1000;
      }
    }
  }
  else {
    uVar1 = 0xffffffea;
  }
  return uVar1;
}

