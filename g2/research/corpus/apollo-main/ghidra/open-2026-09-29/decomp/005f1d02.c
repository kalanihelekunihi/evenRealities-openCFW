
undefined8 tt_hvadvance_adjust(int param_1,uint param_2,int *param_3,uint param_4)

{
  undefined4 uVar1;
  int iVar2;
  undefined4 uVar3;
  
  uVar3 = 0;
  if ((*(char *)(param_1 + 0x2b9) != '\0') && (*(int *)(param_1 + 700) != 0)) {
    if ((param_4 & 0xff) == 0) {
      if (*(char *)(*(int *)(param_1 + 700) + 0x20) == '\0') {
        uVar1 = ft_var_load_hvvar(param_1,0);
        *(undefined4 *)(*(int *)(param_1 + 700) + 0x24) = uVar1;
      }
      if (*(char *)(*(int *)(param_1 + 700) + 0x21) == '\0') {
        uVar3 = *(undefined4 *)(*(int *)(param_1 + 700) + 0x24);
        goto LAB_005f1db6;
      }
      iVar2 = *(int *)(*(int *)(param_1 + 700) + 0x28);
    }
    else {
      if (*(char *)(*(int *)(param_1 + 700) + 0x2c) == '\0') {
        uVar1 = ft_var_load_hvvar(param_1,1);
        *(undefined4 *)(*(int *)(param_1 + 700) + 0x30) = uVar1;
      }
      if (*(char *)(*(int *)(param_1 + 700) + 0x2d) == '\0') {
        uVar3 = *(undefined4 *)(*(int *)(param_1 + 700) + 0x30);
        goto LAB_005f1db6;
      }
      iVar2 = *(int *)(*(int *)(param_1 + 700) + 0x34);
    }
    if (*(int *)(iVar2 + 0x1c) == 0) {
      uVar1 = 0;
      if (**(uint **)(iVar2 + 4) <= param_2) {
        uVar3 = 6;
        goto LAB_005f1db6;
      }
    }
    else {
      if (*(uint *)(iVar2 + 0x14) <= param_2) {
        param_2 = *(int *)(iVar2 + 0x14) - 1;
      }
      uVar1 = *(undefined4 *)(*(int *)(iVar2 + 0x18) + param_2 * 4);
      param_2 = *(uint *)(*(int *)(iVar2 + 0x1c) + param_2 * 4);
    }
    iVar2 = ft_var_get_item_delta(param_1,iVar2,uVar1,param_2);
    *param_3 = iVar2 + *param_3;
  }
LAB_005f1db6:
  return CONCAT44(param_4,uVar3);
}

