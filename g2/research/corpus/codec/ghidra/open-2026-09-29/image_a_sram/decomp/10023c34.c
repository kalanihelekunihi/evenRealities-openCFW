
undefined4 gx8002_flash_page_program(uint param_1,int param_2,uint param_3)

{
  int iVar1;
  uint uVar2;
  uint uVar3;
  int iVar4;
  
  iVar1 = DAT_10023ca8;
  if (param_3 != 0) {
    if (*(uint *)(DAT_10023ca8 + 4) < param_3 + param_1) {
      return 0xffffffea;
    }
    gx8002_flash_wait_ready();
    gx8002_flash_write_enable();
    uVar2 = *(uint *)(iVar1 + 0x18);
    if (param_3 + (param_1 & 0xff) < 0x101) {
      (*(code *)(uVar2 & 0xfffffffe))(param_1,param_2,param_3);
    }
    else {
      uVar3 = 0x100 - (param_1 & 0xff);
      (*(code *)(uVar2 & 0xfffffffe))(param_1,param_2,uVar3);
      for (; uVar3 < param_3; uVar3 = uVar3 + iVar4) {
        uVar2 = param_3 - uVar3;
        iVar4 = (uVar2 < 0x100) * uVar2 + (uint)(uVar2 >= 0x100) * 0x100;
        gx8002_flash_write_enable();
        (*(code *)(*(uint *)(iVar1 + 0x18) & 0xfffffffe))(param_1 + uVar3,param_2 + uVar3,iVar4);
      }
    }
  }
  return 0;
}

