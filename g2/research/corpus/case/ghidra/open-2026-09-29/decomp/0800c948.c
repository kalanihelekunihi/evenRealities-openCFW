
undefined4 FUN_0800c948(int *param_1,uint *param_2)

{
  uint uVar1;
  uint uVar2;
  undefined4 uVar3;
  
  if (param_1 == (int *)0x0) {
    disableIRQinterrupts();
    do {
                    /* WARNING: Do nothing block with infinite loop */
    } while( true );
  }
  if (param_2 != (uint *)0x0) {
    FUN_0800bffc();
    uVar1 = *(uint *)(DAT_0800c9a4 + 0xc) - param_1[1];
    uVar2 = *param_2;
    if (uVar2 == 0xffffffff) {
      uVar3 = 0;
    }
    else if ((*param_1 == *(int *)(DAT_0800c9a4 + 0x20)) ||
            (*(uint *)(DAT_0800c9a4 + 0xc) < (uint)param_1[1])) {
      if (uVar1 < uVar2) {
        *param_2 = uVar2 - uVar1;
        FUN_0800c15c(param_1);
        uVar3 = 0;
      }
      else {
        *param_2 = 0;
        uVar3 = 1;
      }
    }
    else {
      uVar3 = 1;
    }
    FUN_0800c014();
    return uVar3;
  }
  disableIRQinterrupts();
  do {
                    /* WARNING: Do nothing block with infinite loop */
  } while( true );
}

