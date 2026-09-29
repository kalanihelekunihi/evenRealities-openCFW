
uint FUN_00428840(int param_1,undefined4 param_2,undefined4 param_3)

{
  byte bVar1;
  uint uVar2;
  uint *puVar3;
  uint *puVar4;
  uint uVar5;
  undefined4 local_20;
  
  puVar4 = (uint *)(DAT_00428a78 + param_1 * 4 + 4);
  puVar3 = (uint *)(DAT_00428a78 + 100);
  local_20 = CONCAT13((char)(*puVar3 >> 0x15),
                      CONCAT12((char)(*puVar3 >> 0xe),
                               CONCAT11((char)(*puVar3 >> 7),*(undefined1 *)puVar3))) & 0x7f7f7f7f;
  uVar2 = *puVar4;
  bVar1 = *(byte *)puVar4;
  if (*DAT_00428a7c << 0x1f < 0) {
    uVar5 = 0;
    while ((uVar5 < 0x3c && (-1 < *DAT_00428a84 << 1))) {
      delay_us(1);
      uVar5 = uVar5 + 1;
    }
    spotmgr_timer_irq_service_42a04a();
  }
  *DAT_00428a88 = param_3;
  *DAT_00428a8c = param_1;
  *DAT_00428c90 = (*puVar4 & 0x1ffff) >> 7;
  *DAT_00428c94 = (*puVar4 & 0x1fffff) >> 0x11;
  *DAT_00428c98 = (uVar2 & 0xfffffff) >> 0x15;
  *DAT_00428a90 = bVar1 & 0x7f;
  *DAT_00428ba8 = bVar1 & 0x7f | *DAT_00428ba8 & 0xffffff80;
  spotmgr_power_ton_adjust_42a1bc(param_3,param_1);
  return local_20;
}

