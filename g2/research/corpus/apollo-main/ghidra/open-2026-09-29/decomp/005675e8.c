
undefined4 FUN_005675e8(undefined4 *param_1,undefined4 param_2)

{
  char cVar1;
  undefined4 uVar2;
  undefined4 *puVar3;
  undefined4 local_1c;
  undefined4 local_18;
  undefined4 uStack_14;
  undefined4 uStack_10;
  
  if (param_1 == (undefined4 *)0x0) {
    uVar2 = 0x28;
  }
  else {
    param_1[3] = 0;
    param_1[4] = param_2;
    *param_1 = 0;
    param_1[2] = 0;
    param_1[5] = 0;
    param_1[6] = 0;
    cVar1 = FUN_004c6d9a(&local_18,param_2,2);
    if (cVar1 == '\0') {
      FUN_004c6fba(&local_18,0,2);
      cVar1 = FUN_004c7018(&local_18,&local_1c);
      if (cVar1 == '\0') {
        param_1[1] = local_1c;
        FUN_004c6fba(&local_18,0,0);
        puVar3 = (undefined4 *)FUN_00484180(DAT_0056771c,0xc);
        if (puVar3 == (undefined4 *)0x0) {
          FUN_0044d25c(3,DAT_00567730,0x81,DAT_0056772c,DAT_00567728,DAT_00567724,DAT_00567720);
          do {
                    /* WARNING: Do nothing block with infinite loop */
          } while( true );
        }
        if (puVar3 == (undefined4 *)0x0) {
          FUN_004c6ee0(&local_18);
          uVar2 = 0x51;
        }
        else {
          *puVar3 = local_18;
          puVar3[1] = uStack_14;
          puVar3[2] = uStack_10;
          param_1[3] = puVar3;
          param_1[5] = &LAB_00567734_1;
          param_1[6] = &LAB_005676f8_1;
          uVar2 = 0;
        }
      }
      else {
        FUN_004c6ee0(&local_18);
        uVar2 = 0x51;
      }
    }
    else {
      uVar2 = 1;
    }
  }
  return uVar2;
}

