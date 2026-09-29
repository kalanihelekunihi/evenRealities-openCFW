
undefined8 FUN_00480f0c(uint param_1,uint param_2,uint param_3)

{
  bool bVar1;
  int iVar2;
  undefined4 *puVar3;
  undefined4 uVar4;
  uint uVar5;
  undefined4 local_18;
  
  iVar2 = DAT_0048173c;
  local_18 = param_3;
  if (param_1 < 0xe0) {
    uVar5 = 1 << (param_1 & 0x1f);
    if ((*(uint *)(DAT_00481740 + (param_1 >> 5) * 4) & uVar5) == 0) {
      if ((1 < (param_2 & 0xfff) >> 10) &&
         ((*(uint *)(DAT_00481744 + (param_1 >> 5) * 4) & uVar5) == 0)) {
        uVar4 = 7;
        goto LAB_00480f88;
      }
    }
    else if ((((param_2 & 0xffff) >> 0xd != 0) && ((param_2 & 0xffff) >> 0xd != 6)) &&
            ((param_2 & 0xffff) >> 0xd != 1)) {
      uVar4 = 7;
      goto LAB_00480f88;
    }
    local_18 = FUN_00473940();
    puVar3 = DAT_00481748;
    *DAT_00481748 = 0x73;
    *(uint *)(iVar2 + param_1 * 4) = param_2;
    *puVar3 = 0;
    bVar1 = (bool)isCurrentModePrivileged();
    if (bVar1) {
      enableIRQinterrupts((local_18 & 1) == 1);
    }
    uVar4 = 0;
  }
  else {
    uVar4 = 5;
  }
LAB_00480f88:
  return CONCAT44(local_18,uVar4);
}

