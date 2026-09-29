
undefined4 FUN_0800b330(int param_1)

{
  undefined4 uVar1;
  
  uVar1 = 0;
  if (param_1 == 0) {
    disableIRQinterrupts();
    do {
                    /* WARNING: Do nothing block with infinite loop */
    } while( true );
  }
  if (((*(int *)(param_1 + 0x14) == DAT_0800b358) && (*(int *)(param_1 + 0x28) != DAT_0800b35c)) &&
     (*(int *)(param_1 + 0x28) == 0)) {
    uVar1 = 1;
  }
  return uVar1;
}

