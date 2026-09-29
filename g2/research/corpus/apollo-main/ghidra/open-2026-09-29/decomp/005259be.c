
undefined8
open_face(int param_1,undefined4 *param_2,uint param_3,undefined4 param_4,int param_5,
         undefined4 *param_6,int *param_7)

{
  int iVar1;
  uint uVar2;
  int iVar3;
  undefined4 uVar4;
  int iVar5;
  undefined4 *local_30;
  uint local_2c;
  undefined4 local_28;
  
  uVar4 = 0;
  iVar5 = *(int *)(param_1 + 0xc);
  local_28 = *(undefined4 *)(param_1 + 8);
  local_2c = param_3;
  iVar1 = ft_mem_alloc(local_28,*(undefined4 *)(iVar5 + 0x24),&local_2c);
  local_30 = param_2;
  uVar2 = local_2c;
  if (local_2c == 0) {
    *(int *)(iVar1 + 0x60) = param_1;
    *(undefined4 *)(iVar1 + 100) = local_28;
    *(undefined4 *)(iVar1 + 0x68) = *param_2;
    if ((param_3 & 0xff) != 0) {
      *(uint *)(iVar1 + 8) = *(uint *)(iVar1 + 8) | 0x400;
    }
    uVar4 = ft_mem_alloc(local_28,0x44,&local_2c);
    uVar2 = local_2c;
    if (local_2c == 0) {
      *(undefined4 *)(iVar1 + 0x80) = uVar4;
      *(undefined4 *)(*(int *)(iVar1 + 0x80) + 0x34) = 0;
      iVar3 = 0;
      while ((iVar3 < param_5 && (*(int *)(*(int *)(iVar1 + 0x80) + 0x34) == 0))) {
        if (param_6[iVar3 * 2] == DAT_005262a8) {
          *(undefined4 *)(*(int *)(iVar1 + 0x80) + 0x34) = param_6[iVar3 * 2 + 1];
        }
        iVar3 = iVar3 + 1;
      }
      *(undefined4 *)(*(int *)(iVar1 + 0x80) + 0x3c) = 0xffffffff;
      if (*(int *)(iVar5 + 0x30) != 0) {
        local_30 = param_6;
        local_2c = (**(code **)(iVar5 + 0x30))(*param_2,iVar1,param_4);
      }
      *param_2 = *(undefined4 *)(iVar1 + 0x68);
      uVar2 = local_2c;
      if ((local_2c == 0) &&
         ((uVar2 = find_unicode_charmap(iVar1), uVar2 == 0 || ((uVar2 & 0xff) == 0x26)))) {
        *param_7 = iVar1;
        uVar2 = local_2c;
      }
    }
  }
  local_2c = uVar2;
  if (local_2c != 0) {
    destroy_charmaps(iVar1,local_28);
    if (*(int *)(iVar5 + 0x34) != 0) {
      (**(code **)(iVar5 + 0x34))(iVar1);
    }
    ft_mem_free(local_28,uVar4);
    ft_mem_free(local_28,iVar1);
    *param_7 = 0;
  }
  return CONCAT44(local_30,local_2c);
}

