
undefined8 terminal_data_bind_temp_session_response_timer(int param_1,undefined4 param_2)

{
  undefined4 uVar1;
  int iVar2;
  int iVar3;
  
  iVar3 = DAT_00597c08;
  if ((((*(char *)(DAT_00597c08 + 0xa1da) == '\0') || (*(int *)(DAT_00597c08 + 0x956c) != -1)) ||
      (param_1 == 0)) || (param_1 == -1)) {
    uVar1 = 0;
  }
  else {
    iVar2 = td_current_record(param_1);
    if (iVar2 == 0) {
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        param_2 = 0x21a;
        FUN_0043d574(2,DAT_00597c2c,DAT_00597c28,DAT_00597c50,0x21a,DAT_00597c4c,param_1);
      }
      iVar3 = FUN_0043d0ce();
      if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
        compress_log_output(0x8400000,DAT_00597c54,DAT_00597c54,param_1);
      }
      uVar1 = 0;
    }
    else {
      *(undefined4 *)(iVar2 + 0x88) = *(undefined4 *)(iVar3 + 0x95f4);
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        param_2 = 0x21f;
        FUN_0043d574(3,DAT_00597c2c,DAT_00597c28,DAT_00597c50,0x21f,DAT_00597c58,param_1);
      }
      iVar3 = FUN_0043d0ce();
      if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
        compress_log_output(0xc400000,DAT_00597c5c,DAT_00597c5c,param_1);
      }
      uVar1 = 1;
    }
  }
  return CONCAT44(param_2,uVar1);
}

