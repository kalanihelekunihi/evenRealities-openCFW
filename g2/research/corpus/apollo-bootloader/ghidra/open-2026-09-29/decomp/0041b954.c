
undefined8 FUN_0041b954(uint param_1,uint param_2,undefined4 param_3,undefined4 param_4)

{
  uint *puVar1;
  uint *puVar2;
  int iVar3;
  uint uVar4;
  bool bVar5;
  undefined4 local_28;
  uint local_24;
  undefined4 uStack_20;
  
  local_28 = param_2;
  local_24 = param_3;
  uStack_20 = param_4;
  local_24 = critical_save();
  puVar1 = DAT_0041c480;
  if ((param_1 & 0xff) == 2) {
    local_28._0_3_ = CONCAT12(1,(ushort)local_28);
    FUN_0041cd1a(0,0,(int)&local_28 + 2);
    puVar1 = DAT_0041c318;
    bVar5 = -1 < (int)(*DAT_0041c318 << 0x1a);
    if (bVar5) {
      *DAT_0041c318 = *DAT_0041c318 | 0x20;
      delay_us(1);
      delay_status_change(0xf,DAT_0041c31c,0x1000000,0x1000000);
    }
    puVar2 = DAT_0041c480;
    if (*DAT_0041c31c << 7 < 0) {
      *DAT_0041c480 = *DAT_0041c480 & 0xfffffffc | param_1 & 3;
      iVar3 = 4;
      for (uVar4 = 0; uVar4 < 0x14; uVar4 = uVar4 + 1) {
        if ((*puVar2 & 7) >> 2 != 0) {
          iVar3 = 0;
          break;
        }
        delay_us(1);
      }
    }
    else {
      iVar3 = 1;
    }
    if (bVar5) {
      *puVar1 = *puVar1 & 0xffffffdf;
    }
    FUN_0041cdfa();
  }
  else {
    *DAT_0041c480 = *DAT_0041c480 & 0xfffffffc | param_1 & 3;
    iVar3 = 4;
    for (uVar4 = 0; uVar4 < 0x14; uVar4 = uVar4 + 1) {
      if ((*puVar1 & 7) >> 2 != 0) {
        iVar3 = 0;
        break;
      }
      delay_us(1);
    }
  }
  if (iVar3 == 0) {
    *DAT_0041c484 = (char)param_1;
    if ((param_1 & 0xff) != 2) {
      local_28._0_2_ = (ushort)(byte)local_28;
      FUN_0041cd1a(0,0,(int)&local_28 + 1);
    }
  }
  else if ((param_1 & 0xff) == 2) {
    local_28 = local_28 & 0xffffff00;
    FUN_0041cd1a(0,0,&local_28);
  }
  bVar5 = (bool)isCurrentModePrivileged();
  if (bVar5) {
    enableIRQinterrupts((local_24 & 1) == 1);
  }
  return CONCAT44(local_28,iVar3);
}

