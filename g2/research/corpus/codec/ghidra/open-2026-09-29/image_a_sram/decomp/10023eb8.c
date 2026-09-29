
uint gx8002_flash_otp_write(int param_1,int param_2,uint param_3)

{
  short sVar1;
  uint uVar2;
  int iVar3;
  int iVar4;
  int *piVar5;
  uint uVar6;
  uint uVar7;
  uint uVar8;
  int iVar9;
  
  iVar3 = DAT_10023f98;
  piVar5 = *(int **)(*(int *)(DAT_10023f98 + 0xc) + 0x14);
  if ((param_3 != 0) && (param_3 + param_1 <= (uint)piVar5[2])) {
    uVar2 = *piVar5 + param_1 + (piVar5[4] & 7U) * piVar5[1];
    sVar1 = *(short *)(*(int *)(DAT_10023f98 + 0xc) + 6);
    if ((sVar1 == 0x5e) || (sVar1 == 0x85)) {
      gx8002_flash_wait_ready();
      gx8002_flash_write_enable();
      iVar4 = DAT_10023f9c + -8;
      *(undefined1 *)(iVar3 + 0x10) = 0x42;
      sflash_addr2cmd_isra_0(iVar4,uVar2);
      if (param_3 + (uVar2 & 0xff) < 0x101) {
        gx8002_flash_otp_transmit(*(int *)(iVar3 + 8) + 1,param_2,param_3);
        uVar6 = param_3;
      }
      else {
        uVar6 = 0x100 - (uVar2 & 0xff);
        gx8002_flash_otp_transmit(*(int *)(iVar3 + 8) + 1,param_2,uVar6);
        iVar4 = DAT_10023f9c;
        for (uVar7 = uVar6; uVar7 < param_3; uVar7 = uVar7 + iVar9) {
          sflash_addr2cmd_isra_0(DAT_10023fa0,uVar7 + uVar2,iVar4);
          gx8002_flash_wait_ready();
          uVar8 = param_3 - uVar7;
          gx8002_flash_write_enable();
          iVar9 = (uVar8 < 0x100) * uVar8 + (uint)(uVar8 >= 0x100) * 0x100;
          gx8002_flash_otp_transmit(*(int *)(iVar3 + 8) + 1,param_2 + uVar7,iVar9);
          if (uVar6 != 0) {
            uVar6 = uVar6 + iVar9;
          }
        }
      }
      gx8002_flash_wait_ready();
      return uVar6;
    }
  }
  return 0xffffffff;
}

