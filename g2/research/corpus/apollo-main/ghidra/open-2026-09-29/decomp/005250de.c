
undefined8 ft_glyphslot_preset_bitmap(uint param_1,uint param_2,int *param_3,uint param_4)

{
  uint uVar1;
  uint uVar2;
  uint uVar3;
  uint uVar4;
  int iVar5;
  uint uVar6;
  int iVar7;
  char cVar8;
  uint local_28;
  uint local_24;
  int *local_20;
  uint local_1c;
  
  iVar5 = 0;
  iVar7 = 0;
  local_28 = param_1;
  local_24 = param_2;
  if ((*(int *)(param_1 + 0x9c) != 0) &&
     ((int)((uint)*(byte *)(*(int *)(param_1 + 0x9c) + 4) << 0x1f) < 0)) goto LAB_00525258;
  if (param_3 != (int *)0x0) {
    iVar5 = *param_3;
    iVar7 = param_3[1];
  }
  local_20 = param_3;
  local_1c = param_4;
  FT_Outline_Get_CBox(param_1 + 0x6c,&local_28);
  local_28 = iVar5 + local_28;
  local_24 = iVar7 + local_24;
  local_20 = (int *)(iVar5 + (int)local_20);
  local_1c = iVar7 + local_1c;
  param_2 = param_2 & 0xff;
  if (param_2 == 2) {
    cVar8 = '\x01';
    if ((int)((int)local_20 - local_28) < 0x40) {
      local_20 = (int *)((int)local_20 + 0x3f);
    }
    else {
      local_28 = local_28 + 0x20;
      local_20 = local_20 + 8;
    }
    uVar1 = local_28;
    if ((int)(local_1c - local_24) < 0x40) {
      uVar2 = local_1c + 0x3f;
    }
    else {
      local_24 = local_24 + 0x20;
      uVar2 = local_1c + 0x20;
    }
  }
  else {
    if (param_2 < 2) {
LAB_005251ce:
      cVar8 = '\x02';
    }
    else if (param_2 == 4) {
      cVar8 = '\x06';
      ft_lcd_padding(&local_24,&local_1c,param_1);
    }
    else {
      if (3 < param_2) goto LAB_005251ce;
      cVar8 = '\x05';
      ft_lcd_padding(&local_28,&local_20,param_1);
    }
    local_20 = (int *)((int)local_20 + 0x3f);
    uVar2 = local_1c + 0x3f;
    uVar1 = local_28;
  }
  local_1c = uVar2 & 0xffffffc0;
  local_20 = (int *)((uint)local_20 & 0xffffffc0);
  local_24 = local_24 & 0xffffffc0;
  local_28 = uVar1 & 0xffffffc0;
  uVar4 = (int)local_20 - local_28 >> 6;
  uVar6 = local_1c - local_24 >> 6;
  if (cVar8 == '\x01') {
    uVar3 = ((int)(uVar4 + 0xf) >> 4) << 1;
  }
  else if (cVar8 == '\x05') {
    uVar4 = uVar4 * 3;
    uVar3 = uVar4 + 3 & 0xfffffffc;
  }
  else {
    uVar3 = uVar4;
    if (cVar8 == '\x06') {
      uVar6 = uVar6 * 3;
    }
  }
  *(int *)(param_1 + 100) = (int)uVar1 >> 6;
  *(int *)(param_1 + 0x68) = (int)uVar2 >> 6;
  *(char *)(param_1 + 0x5e) = cVar8;
  *(undefined2 *)(param_1 + 0x5c) = 0x100;
  *(uint *)(param_1 + 0x50) = uVar4;
  *(uint *)(param_1 + 0x4c) = uVar6;
  *(uint *)(param_1 + 0x54) = uVar3;
LAB_00525258:
  return CONCAT44(local_24,local_28);
}

