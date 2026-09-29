
uint case_event_group_set_bits(uint *param_1,uint param_2)

{
  bool bVar1;
  uint *puVar2;
  uint *puVar3;
  uint uVar4;
  uint uVar5;
  uint uVar6;
  
  uVar6 = 0;
  if (param_1 == (uint *)0x0) {
    disableIRQinterrupts();
    do {
                    /* WARNING: Do nothing block with infinite loop */
    } while( true );
  }
  if (param_2 >> 0x18 != 0) {
    disableIRQinterrupts();
    do {
                    /* WARNING: Do nothing block with infinite loop */
    } while( true );
  }
  FUN_0800c380();
  *param_1 = *param_1 | param_2;
  puVar3 = (uint *)param_1[4];
  while (puVar2 = puVar3, puVar2 != param_1 + 3) {
    puVar3 = (uint *)puVar2[1];
    bVar1 = false;
    uVar5 = *puVar2 & 0xff000000;
    uVar4 = *puVar2 & 0xffffff;
    if ((int)(uVar5 << 5) < 0) {
      if ((uVar4 & ~*param_1) == 0) {
        bVar1 = true;
      }
    }
    else if ((*param_1 & uVar4) != 0) {
      bVar1 = true;
    }
    if (bVar1) {
      if ((int)(uVar5 << 7) < 0) {
        uVar6 = uVar6 | uVar4;
      }
      FUN_0800c1cc(puVar2,*param_1 | 0x2000000);
    }
  }
  *param_1 = *param_1 & ~uVar6;
  FUN_0800cc0c();
  return *param_1;
}

