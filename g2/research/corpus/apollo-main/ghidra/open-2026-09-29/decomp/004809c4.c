
undefined8 FUN_004809c4(byte param_1,uint *param_2,undefined4 param_3,uint param_4)

{
  uint *puVar1;
  int iVar2;
  uint local_10;
  
  if (param_1 == 0) {
    if ((param_2 == (uint *)0x0) || ((char)*param_2 != '\x01')) {
      local_10 = *DAT_00480eb0 & 0xffffffe0 | 0x19;
    }
    else {
      local_10 = *DAT_00480eb0 & 0xffffffe0 | 5;
    }
    *DAT_00480eb0 = local_10;
  }
  else if (param_1 == 2) {
    *DAT_00480eb4 =
         *DAT_00480eb4 & DAT_00480eb8 | *DAT_00480ebc & 0x3f | (*DAT_00480ec0 & 0xf) << 6 |
         DAT_00480ec4;
    puVar1 = DAT_00480ec8;
    local_10 = *DAT_00480ec8 & 0xffffffdd | 2;
    *DAT_00480ec8 = local_10;
    *puVar1 = *puVar1 | 1;
    *puVar1 = *puVar1 | 0x10;
    *puVar1 = *puVar1 | 8;
    FUN_004807a0(5);
    *puVar1 = *puVar1 & 0xffffffef;
    if ((param_2 != (uint *)0x0) && ((char)*param_2 == '\x01')) {
      local_10 = *puVar1 & DAT_00480ecc | 0x100;
      *puVar1 = local_10;
    }
  }
  else if (param_1 < 2) {
    local_10 = *DAT_00480eb0 & 0xfffffffc;
    *DAT_00480eb0 = local_10;
  }
  else if (param_1 == 4) {
    *DAT_00480eb4 =
         *DAT_00480eb4 & DAT_00480eb8 | *DAT_00480ebc & 0x3f | (*DAT_00480ec0 & 0xf) << 6 |
         0x3118000;
    local_10 = *DAT_00480ec8 & DAT_00480ed4 | 2;
    *DAT_00480ec8 = local_10;
  }
  else if (param_1 < 4) {
    *DAT_00480eb4 = *DAT_00480ebc & 0x3f | (*DAT_00480ec0 & 0xf) << 6 | DAT_00480ec4;
    puVar1 = DAT_00480ec8;
    *DAT_00480ec8 = *DAT_00480ec8 & 0xffffffdd | 0x22;
    *puVar1 = *puVar1 | 1;
    if ((param_2 == (uint *)0x0) || ((char)*param_2 != '\x01')) {
      local_10 = *puVar1 & 0xffffffd7 | 8;
    }
    else {
      local_10 = *puVar1 & DAT_00480ed0 | 0x100;
    }
    *puVar1 = local_10;
  }
  else {
    local_10 = param_4;
    if (param_1 == 6) {
      *DAT_00480eb4 = *DAT_00480eb4 | 0x7000;
      *DAT_00480ec8 = *DAT_00480ec8 & 0xffffff7f;
      iVar2 = FUN_004c4530(2,0x34);
      if (iVar2 != 0) goto LAB_00480a1a;
    }
    else {
      if (5 < param_1) {
        iVar2 = 6;
        goto LAB_00480a1a;
      }
      iVar2 = FUN_004c44bc(2,0x34);
      if (iVar2 != 0) goto LAB_00480a1a;
      if (param_2 == (uint *)0x0) {
        local_10 = *DAT_00480eb4 & 0xffff8fff | 0x4000;
        *DAT_00480eb4 = local_10;
      }
      else {
        if ((*param_2 != 0) && (4 < *param_2 - 3)) {
          iVar2 = 6;
          goto LAB_00480a1a;
        }
        local_10 = *DAT_00480eb4 & 0xffff8fff | (*param_2 & 7) << 0xc;
        *DAT_00480eb4 = local_10;
      }
      *DAT_00480ec8 = *DAT_00480ec8 | 0x80;
    }
  }
  iVar2 = 0;
LAB_00480a1a:
  return CONCAT44(local_10,iVar2);
}

