
undefined4
FUN_0800cd80(int param_1,int param_2,undefined4 param_3,undefined4 param_4,undefined4 param_5)

{
  int *piVar1;
  int iVar2;
  undefined4 uVar3;
  int local_28;
  undefined4 local_24;
  int local_20;
  
  piVar1 = DAT_0800cde0;
  uVar3 = 0;
  if (param_1 != 0) {
    if (*DAT_0800cde0 != 0) {
      local_28 = param_2;
      local_24 = param_3;
      local_20 = param_1;
      if (param_2 < 6) {
        iVar2 = xTaskGetSchedulerState();
        if (iVar2 == 2) {
          uVar3 = FUN_0800c686(*piVar1,&local_28,param_5,0);
        }
        else {
          uVar3 = FUN_0800c686(*piVar1,&local_28,0);
        }
      }
      else {
        uVar3 = FUN_0800c7a8(*DAT_0800cde0,&local_28,param_4,0);
      }
    }
    return uVar3;
  }
  disableIRQinterrupts();
  do {
                    /* WARNING: Do nothing block with infinite loop */
  } while( true );
}

