
undefined4 FUN_0800c7a8(int param_1,int param_2,undefined4 *param_3,int param_4)

{
  char cVar1;
  undefined4 uVar2;
  int iVar3;
  undefined4 uVar4;
  
  if (param_1 == 0) {
    disableIRQinterrupts();
    do {
                    /* WARNING: Do nothing block with infinite loop */
    } while( true );
  }
  if ((param_2 == 0) && (*(int *)(param_1 + 0x40) != 0)) {
    disableIRQinterrupts();
    do {
                    /* WARNING: Do nothing block with infinite loop */
    } while( true );
  }
  if ((param_4 == 2) && (*(int *)(param_1 + 0x3c) != 1)) {
    disableIRQinterrupts();
    do {
                    /* WARNING: Do nothing block with infinite loop */
    } while( true );
  }
  uVar2 = ulSetInterruptMaskFromISR();
  if ((*(uint *)(param_1 + 0x38) < *(uint *)(param_1 + 0x3c)) || (param_4 == 2)) {
    cVar1 = *(char *)(param_1 + 0x45);
    FUN_0800ad48(param_1,param_2,param_4);
    if (cVar1 == -1) {
      if (((*(int *)(param_1 + 0x24) != 0) && (iVar3 = FUN_0800cba0(param_1 + 0x24), iVar3 != 0)) &&
         (param_3 != (undefined4 *)0x0)) {
        *param_3 = 1;
      }
    }
    else {
      *(char *)(param_1 + 0x45) = cVar1 + '\x01';
    }
    uVar4 = 1;
  }
  else {
    uVar4 = 0;
  }
  vClearInterruptMaskFromISR(uVar2);
  return uVar4;
}

