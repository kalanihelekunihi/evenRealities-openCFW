
uint FUN_00428240(int param_1,int param_2,undefined4 param_3)

{
  byte bVar1;
  uint *puVar2;
  uint *puVar3;
  uint uVar4;
  uint uVar5;
  int iVar6;
  uint uVar7;
  undefined4 local_28;
  
  iVar6 = DAT_00428a78;
  puVar3 = (uint *)(DAT_00428a78 + param_1 * 4 + 4);
  puVar2 = (uint *)(DAT_00428a78 + 100);
  local_28 = CONCAT13((char)(*puVar2 >> 0x15),
                      CONCAT12((char)(*puVar2 >> 0xe),
                               CONCAT11((char)(*puVar2 >> 7),*(undefined1 *)puVar2))) & 0x7f7f7f7f;
  uVar4 = (*(uint *)(DAT_00428a78 + param_2 * 4 + 4) & 0xfffffff) >> 0x15;
  uVar5 = (*puVar3 & 0xfffffff) >> 0x15;
  bVar1 = *(byte *)puVar3;
  if (*DAT_00428a7c << 0x1f < 0) {
    uVar7 = 0;
    while ((uVar7 < 0x3c && (-1 < *DAT_00428a84 << 1))) {
      delay_us(1);
      uVar7 = uVar7 + 1;
    }
    spotmgr_timer_irq_service_42a04a();
  }
  *DAT_00428a88 = param_3;
  *DAT_00428a8c = param_1;
  *DAT_00428c90 = (*puVar3 & 0x1ffff) >> 7;
  *DAT_00428c94 = (*puVar3 & 0x1fffff) >> 0x11;
  *DAT_00428c98 = uVar5;
  *DAT_00428a90 = bVar1 & 0x7f;
  spotmgr_power_ton_adjust_42a1bc(param_3,param_1);
  *DAT_00428ba8 = *DAT_00428ba8 & 0xffffff80 | *(uint *)(iVar6 + 0x50) & 0x7f;
  iVar6 = uVar5 - uVar4;
  if (iVar6 < 1) {
    iVar6 = 0;
  }
  else {
    iVar6 = iVar6 * 2;
  }
  if (iVar6 + uVar4 < 0x80) {
    *DAT_00428c84 = *DAT_00428c84 & 0xffffff80 | iVar6 + uVar4 & 0x7f;
  }
  else {
    *DAT_00428c84 = *DAT_00428c84 | 0x7f;
  }
  *DAT_00428a80 = param_1;
  FUN_0041cc48(0x32);
  *DAT_00428c88 = 2;
  return local_28;
}

