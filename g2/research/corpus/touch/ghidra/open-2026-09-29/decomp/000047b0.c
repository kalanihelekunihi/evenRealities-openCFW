
undefined4 touch_flash_14b0_zero_rows(undefined4 param_1,uint param_2,int param_3)

{
  int iVar1;
  int extraout_r1;
  uint uVar2;
  undefined4 uVar3;
  undefined1 *puVar4;
  undefined1 *puVar5;
  
  puVar4 = &stack0xffffffe8 + DAT_00004808;
  puVar5 = &stack0xffffffe8 + DAT_00004808;
  iVar1 = touch_leaf_1488_constant_128();
  memset(puVar4,0,0x200);
  __aeabi_uidivmod(param_3,iVar1);
  uVar2 = param_2;
  uVar3 = DAT_0000480c;
  if (extraout_r1 == 0) {
    for (; uVar3 = 0, uVar2 < param_2 + param_3; uVar2 = uVar2 + iVar1) {
      Cy_Flash_WriteRow(uVar2,puVar5);
    }
  }
  return uVar3;
}

