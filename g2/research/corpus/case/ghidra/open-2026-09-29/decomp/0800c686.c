
undefined4 FUN_0800c686(int param_1,int param_2,int param_3,int param_4)

{
  bool bVar1;
  int iVar2;
  undefined1 auStack_30 [8];
  int local_28;
  int iStack_24;
  int local_20;
  int local_1c;
  int iStack_18;
  
  bVar1 = false;
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
  iStack_24 = param_1;
  local_20 = param_2;
  local_1c = param_3;
  iStack_18 = param_4;
  iVar2 = xTaskGetSchedulerState();
  if ((iVar2 == 0) && (local_1c != 0)) {
    disableIRQinterrupts();
    do {
                    /* WARNING: Do nothing block with infinite loop */
    } while( true );
  }
  local_28 = param_1 + 0x10;
  while( true ) {
    FUN_0800bffc();
    if ((*(uint *)(param_1 + 0x38) < *(uint *)(param_1 + 0x3c)) || (param_4 == 2)) {
      iVar2 = FUN_0800ad48(param_1,local_20,param_4);
      if (*(int *)(param_1 + 0x24) == 0) {
        if (iVar2 != 0) {
          FUN_0800c0a0();
        }
      }
      else {
        iVar2 = FUN_0800cba0(param_1 + 0x24);
        if (iVar2 != 0) {
          FUN_0800c0a0();
        }
      }
      FUN_0800c014();
      return 1;
    }
    if (local_1c == 0) {
      FUN_0800c014();
      return 0;
    }
    if (!bVar1) {
      FUN_0800c15c(auStack_30);
      bVar1 = true;
    }
    FUN_0800c014();
    FUN_0800c380();
    FUN_0800bffc();
    if (*(char *)(param_1 + 0x44) == -1) {
      *(undefined1 *)(param_1 + 0x44) = 0;
    }
    if (*(char *)(param_1 + 0x45) == -1) {
      *(undefined1 *)(param_1 + 0x45) = 0;
    }
    FUN_0800c014();
    iVar2 = FUN_0800c948(auStack_30,&local_1c);
    if (iVar2 != 0) break;
    iVar2 = FUN_0800b080(param_1);
    if (iVar2 == 0) {
      FUN_0800b374(param_1);
      FUN_0800cc0c();
    }
    else {
      FUN_0800c178(local_28,local_1c);
      FUN_0800b374(param_1);
      iVar2 = FUN_0800cc0c();
      if (iVar2 == 0) {
        FUN_0800c0a0();
      }
    }
  }
  FUN_0800b374(param_1);
  FUN_0800cc0c();
  return 0;
}

