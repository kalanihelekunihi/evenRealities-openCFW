
undefined8
even_ai_stream_init_from_service
          (char param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int *piVar1;
  char *pcVar2;
  char cVar3;
  undefined2 uVar4;
  int iVar5;
  undefined4 uVar6;
  
  pcVar2 = DAT_004e607c;
  piVar1 = DAT_004e5f90;
  if ((*DAT_004e5f90 == 0) || (*DAT_004e60ec == 0)) {
    iVar5 = FUN_0043d0ce();
    if (iVar5 << 0x1e < 0) {
      param_2 = 0x17f;
      param_3 = DAT_004e61a8;
      FUN_0043d574(1,DAT_004e5fa0,DAT_004e5f9c,DAT_004e61ac,0x17f,DAT_004e61a8,param_4);
    }
    iVar5 = FUN_0043d0ce();
    if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_004e61b0,DAT_004e61b0);
    }
  }
  else {
    if (*DAT_004e607c != '\x01') {
      FUN_0043c0e4(DAT_004e607c,0x20,0);
    }
    *pcVar2 = '\x01';
    if (param_1 == '\0') {
      cVar3 = '\x02';
    }
    else {
      cVar3 = '\x01';
    }
    pcVar2[1] = cVar3;
    uVar4 = text_stream_current_length(*piVar1);
    *(undefined2 *)(pcVar2 + 2) = uVar4;
    uVar4 = text_stream_pending_length(*piVar1);
    *(undefined2 *)(pcVar2 + 4) = uVar4;
    pcVar2[8] = '\x06';
    pcVar2[9] = '\0';
    uVar6 = even_ai_stream_interval_get();
    *(undefined4 *)(pcVar2 + 0x10) = uVar6;
  }
  return CONCAT44(param_3,param_2);
}

