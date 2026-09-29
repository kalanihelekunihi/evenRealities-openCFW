
undefined8 ft_var_load_hvvar(int param_1,uint param_2,undefined4 param_3,undefined4 param_4)

{
  bool bVar1;
  short sVar2;
  int iVar3;
  int iVar4;
  int unaff_r4;
  int iVar5;
  int iVar6;
  undefined4 uVar7;
  uint local_30;
  undefined4 uStack_2c;
  undefined4 uStack_28;
  
  iVar6 = *(int *)(param_1 + 0x68);
  uVar7 = *(undefined4 *)(iVar6 + 0x1c);
  iVar5 = *(int *)(param_1 + 700);
  local_30 = param_2;
  uStack_2c = param_3;
  uStack_28 = param_4;
  if ((param_2 & 0xff) == 0) {
    *(undefined1 *)(iVar5 + 0x20) = 1;
    local_30 = (**(code **)(param_1 + 0x204))(param_1,DAT_005f2528,iVar6,&uStack_2c);
  }
  else {
    *(undefined1 *)(iVar5 + 0x2c) = 1;
    local_30 = (**(code **)(param_1 + 0x204))(param_1,DAT_005f2524,iVar6,&uStack_2c);
  }
  if (local_30 == 0) {
    iVar3 = *(int *)(iVar6 + 8);
    sVar2 = FT_Stream_ReadUShort(iVar6,&local_30);
    if ((local_30 == 0) && (local_30 = FT_Stream_Skip(iVar6,2), local_30 == 0)) {
      bVar1 = false;
    }
    else {
      bVar1 = true;
    }
    if (!bVar1) {
      if (sVar2 == 1) {
        iVar4 = FT_Stream_ReadULong(iVar6,&local_30);
        if ((local_30 == 0) && (unaff_r4 = FT_Stream_ReadULong(iVar6,&local_30), local_30 == 0)) {
          bVar1 = false;
        }
        else {
          bVar1 = true;
        }
        if (!bVar1) {
          if ((param_2 & 0xff) == 0) {
            uVar7 = ft_mem_alloc(uVar7,0x20,&local_30);
            *(undefined4 *)(iVar5 + 0x28) = uVar7;
            if (local_30 != 0) goto LAB_005f1b68;
            iVar6 = *(int *)(iVar5 + 0x28);
          }
          else {
            uVar7 = ft_mem_alloc(uVar7,0x20,&local_30);
            *(undefined4 *)(iVar5 + 0x34) = uVar7;
            if (local_30 != 0) goto LAB_005f1b68;
            iVar6 = *(int *)(iVar5 + 0x34);
          }
          local_30 = ft_var_load_item_variation_store(param_1,iVar4 + iVar3,iVar6);
          if ((local_30 == 0) &&
             ((unaff_r4 == 0 ||
              (local_30 = ft_var_load_delta_set_index_mapping
                                    (param_1,unaff_r4 + iVar3,iVar6 + 0x14,iVar6), local_30 == 0))))
          {
            local_30 = 0;
          }
        }
      }
      else {
        local_30 = 8;
      }
    }
  }
LAB_005f1b68:
  if (local_30 == 0) {
    if ((param_2 & 0xff) == 0) {
      *(undefined1 *)(iVar5 + 0x21) = 1;
      *(uint *)(param_1 + 0x2c0) = *(uint *)(param_1 + 0x2c0) | 2;
    }
    else {
      *(undefined1 *)(iVar5 + 0x2d) = 1;
      *(uint *)(param_1 + 0x2c0) = *(uint *)(param_1 + 0x2c0) | 0x10;
    }
  }
  return CONCAT44(local_30,local_30);
}

