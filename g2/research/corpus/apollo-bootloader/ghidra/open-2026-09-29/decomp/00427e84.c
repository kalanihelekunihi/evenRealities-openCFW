
uint FUN_00427e84(int param_1,int param_2,undefined4 param_3)

{
  int iVar1;
  uint *puVar2;
  uint *puVar3;
  uint uVar4;
  uint uVar5;
  uint uVar6;
  uint uVar7;
  bool bVar8;
  uint local_28;
  
  puVar3 = (uint *)(DAT_00428a78 + param_1 * 4 + 4);
  puVar2 = (uint *)(DAT_00428a78 + 100);
  local_28 = CONCAT13((char)(*puVar2 >> 0x15),
                      CONCAT12((char)(*puVar2 >> 0xe),
                               CONCAT11((char)(*puVar2 >> 7),*(undefined1 *)puVar2))) & 0x7f7f7f7f;
  uVar4 = *(byte *)(DAT_00428a78 + param_2 * 4 + 4) & 0x7f;
  uVar5 = (*puVar3 & 0xfffffff) >> 0x15;
  uVar6 = *(byte *)puVar3 & 0x7f;
  if (*DAT_00428a7c << 0x1f < 0) {
    if (param_1 == *DAT_00428a80) {
      spotmgr_power_ton_adjust_42a1bc(param_3,param_1);
      *DAT_00428c84 = uVar5 | *DAT_00428c84 & 0xffffff80;
      FUN_0041ccd6();
      *DAT_00428c88 = 0x1a;
      return local_28;
    }
    if (*DAT_00428a7c << 0x1f < 0) {
      uVar7 = 0;
      while ((uVar7 < 0x3c && (-1 < *DAT_00428a84 << 1))) {
        delay_us(1);
        uVar7 = uVar7 + 1;
      }
      spotmgr_timer_irq_service_42a04a();
    }
  }
  *DAT_00428a88 = param_3;
  *DAT_00428a8c = param_1;
  *DAT_00428c90 = (*puVar3 & 0x1ffff) >> 7;
  *DAT_00428c94 = (*puVar3 & 0x1fffff) >> 0x11;
  *DAT_00428c98 = uVar5;
  *DAT_00428a90 = uVar6;
  spotmgr_power_ton_adjust_42a1bc(param_3,param_1);
  if ((int)(uVar6 - uVar4) < 1) {
    iVar1 = 0;
  }
  else {
    iVar1 = (uVar6 - uVar4) * 2;
  }
  if (iVar1 + uVar4 < 0x80) {
    *DAT_00428ba8 = *DAT_00428ba8 & 0xffffff80 | iVar1 + uVar4 & 0x7f;
  }
  else {
    *DAT_00428ba8 = *DAT_00428ba8 | 0x7f;
  }
  delay_us(0x32);
  *DAT_00428ba8 = uVar6 | *DAT_00428ba8 & 0xffffff80;
  bVar8 = *DAT_00428bac << 0xe < 0;
  if (bVar8) {
    FUN_0041e22e();
  }
  puVar2 = DAT_00428c9c;
  *DAT_00428c9c = *DAT_00428c9c | 0x10000;
  *puVar2 = *puVar2 | 0x2000000;
  delay_us(0x14);
  if (bVar8) {
    FUN_0041e1e8();
  }
  puVar2 = DAT_00428ca0;
  *DAT_00428ca0 = *DAT_00428ca0 & 0xffffc3ff | ((*puVar3 & 0x1fffff) >> 0x11) << 10;
  *puVar2 = (*puVar3 & 0x1ffff) >> 7 | *puVar2 & 0xfffffc00;
  *DAT_00428c84 = uVar5 | *DAT_00428c84 & 0xffffff80;
  return local_28;
}

