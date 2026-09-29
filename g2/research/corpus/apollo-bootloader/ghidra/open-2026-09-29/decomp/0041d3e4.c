
undefined8 FUN_0041d3e4(byte param_1,uint *param_2,undefined4 param_3,uint param_4)

{
  uint *puVar1;
  int iVar2;
  uint local_10;
  
  if (param_1 == 0) {
    if ((param_2 == (uint *)0x0) || ((char)*param_2 != '\x01')) {
      local_10 = *DAT_0041d8d0 & 0xffffffe0 | 0x19;
    }
    else {
      local_10 = *DAT_0041d8d0 & 0xffffffe0 | 5;
    }
    *DAT_0041d8d0 = local_10;
  }
  else if (param_1 == 2) {
    *DAT_0041d8d4 =
         *DAT_0041d8d4 & DAT_0041d8d8 | *DAT_0041d8dc & 0x3f | (*DAT_0041d8e0 & 0xf) << 6 |
         DAT_0041d8e4;
    puVar1 = DAT_0041d8e8;
    local_10 = *DAT_0041d8e8 & 0xffffffdd | 2;
    *DAT_0041d8e8 = local_10;
    *puVar1 = *puVar1 | 1;
    *puVar1 = *puVar1 | 0x10;
    *puVar1 = *puVar1 | 8;
    delay_us(5);
    *puVar1 = *puVar1 & 0xffffffef;
    if ((param_2 != (uint *)0x0) && ((char)*param_2 == '\x01')) {
      local_10 = *puVar1 & DAT_0041d8ec | 0x100;
      *puVar1 = local_10;
    }
  }
  else if (param_1 < 2) {
    local_10 = *DAT_0041d8d0 & 0xfffffffc;
    *DAT_0041d8d0 = local_10;
  }
  else if (param_1 == 4) {
    *DAT_0041d8d4 =
         *DAT_0041d8d4 & DAT_0041d8d8 | *DAT_0041d8dc & 0x3f | (*DAT_0041d8e0 & 0xf) << 6 |
         0x3118000;
    local_10 = *DAT_0041d8e8 & DAT_0041d8f4 | 2;
    *DAT_0041d8e8 = local_10;
  }
  else if (param_1 < 4) {
    *DAT_0041d8d4 = *DAT_0041d8dc & 0x3f | (*DAT_0041d8e0 & 0xf) << 6 | DAT_0041d8e4;
    puVar1 = DAT_0041d8e8;
    *DAT_0041d8e8 = *DAT_0041d8e8 & 0xffffffdd | 0x22;
    *puVar1 = *puVar1 | 1;
    if ((param_2 == (uint *)0x0) || ((char)*param_2 != '\x01')) {
      local_10 = *puVar1 & 0xffffffd7 | 8;
    }
    else {
      local_10 = *puVar1 & DAT_0041d8f0 | 0x100;
    }
    *puVar1 = local_10;
  }
  else {
    local_10 = param_4;
    if (param_1 == 6) {
      *DAT_0041d8d4 = *DAT_0041d8d4 | 0x7000;
      *DAT_0041d8e8 = *DAT_0041d8e8 & 0xffffff7f;
      iVar2 = clock_release(2,0x34);
      if (iVar2 != 0) goto LAB_0041d43a;
    }
    else {
      if (5 < param_1) {
        iVar2 = 6;
        goto LAB_0041d43a;
      }
      iVar2 = clock_request(2,0x34);
      if (iVar2 != 0) goto LAB_0041d43a;
      if (param_2 == (uint *)0x0) {
        local_10 = *DAT_0041d8d4 & 0xffff8fff | 0x4000;
        *DAT_0041d8d4 = local_10;
      }
      else {
        if ((*param_2 != 0) && (4 < *param_2 - 3)) {
          iVar2 = 6;
          goto LAB_0041d43a;
        }
        local_10 = *DAT_0041d8d4 & 0xffff8fff | (*param_2 & 7) << 0xc;
        *DAT_0041d8d4 = local_10;
      }
      *DAT_0041d8e8 = *DAT_0041d8e8 | 0x80;
    }
  }
  iVar2 = 0;
LAB_0041d43a:
  return CONCAT44(local_10,iVar2);
}

