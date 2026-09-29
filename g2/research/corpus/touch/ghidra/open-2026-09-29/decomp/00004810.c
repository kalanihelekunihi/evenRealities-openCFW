
undefined4 touch_flash_1510_copy_rows(undefined4 param_1,uint param_2,int param_3,int param_4)

{
  int iVar1;
  int extraout_r1;
  uint uVar2;
  undefined4 uVar3;
  
  iVar1 = touch_leaf_1484_constant_128();
  __aeabi_uidivmod(param_3,iVar1);
  uVar2 = param_2;
  uVar3 = DAT_0000485c;
  if (extraout_r1 == 0) {
    for (; uVar3 = 0, uVar2 < param_2 + param_3; uVar2 = uVar2 + iVar1) {
      Cy_Flash_WriteRow(uVar2,param_4);
      param_4 = param_4 + iVar1;
    }
  }
  return uVar3;
}

