
undefined8 cff_cmap_unicode_init(int *param_1,undefined4 param_2,undefined4 param_3)

{
  undefined4 uVar1;
  int iVar2;
  int iVar3;
  
  iVar2 = *param_1;
  iVar3 = *(int *)(iVar2 + 0x2a4);
  if (*(int *)(iVar3 + 0x4a4) == 0) {
    uVar1 = 0xa3;
  }
  else {
    param_3 = 0;
    uVar1 = (**(code **)(*(int *)(iVar3 + 0xc0c) + 4))
                      (*(undefined4 *)(iVar2 + 100),param_1,*(undefined4 *)(iVar3 + 0x14),
                       DAT_005ac5ec,0,iVar2);
  }
  return CONCAT44(param_3,uVar1);
}

