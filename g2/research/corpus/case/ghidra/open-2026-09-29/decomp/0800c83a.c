
undefined4 FUN_0800c83a(int param_1,int param_2,int param_3)

{
  bool bVar1;
  int iVar2;
  undefined1 auStack_30 [8];
  int local_28;
  int iStack_20;
  int local_1c;
  int local_18;
  
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
  iStack_20 = param_1;
  local_1c = param_2;
  local_18 = param_3;
  iVar2 = xTaskGetSchedulerState();
  if ((iVar2 == 0) && (local_18 != 0)) {
    disableIRQinterrupts();
    do {
                    /* WARNING: Do nothing block with infinite loop */
    } while( true );
  }
  local_28 = param_1 + 0x24;
  while( true ) {
    FUN_0800bffc();
    iVar2 = *(int *)(param_1 + 0x38);
    if (iVar2 != 0) {
      case_advance_cursor(param_1,local_1c);
      *(int *)(param_1 + 0x38) = iVar2 + -1;
      if ((*(int *)(param_1 + 0x10) != 0) && (iVar2 = FUN_0800cba0(param_1 + 0x10), iVar2 != 0)) {
        FUN_0800c0a0();
      }
      FUN_0800c014();
      return 1;
    }
    if (local_18 == 0) break;
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
    iVar2 = FUN_0800c948(auStack_30,&local_18);
    if (iVar2 == 0) {
      iVar2 = case_context_word38_is_zero(param_1);
      if (iVar2 == 0) {
        FUN_0800b374(param_1);
        FUN_0800cc0c();
      }
      else {
        FUN_0800c178(local_28,local_18);
        FUN_0800b374(param_1);
        iVar2 = FUN_0800cc0c();
        if (iVar2 == 0) {
          FUN_0800c0a0();
        }
      }
    }
    else {
      FUN_0800b374(param_1);
      FUN_0800cc0c();
      iVar2 = case_context_word38_is_zero(param_1);
      if (iVar2 != 0) {
        return 0;
      }
    }
  }
  FUN_0800c014();
  return 0;
}

