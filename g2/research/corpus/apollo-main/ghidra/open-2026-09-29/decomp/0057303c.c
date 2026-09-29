
undefined4 pt_cmd_31_handler(int param_1,byte param_2,undefined1 *param_3,byte *param_4)

{
  char *pcVar1;
  undefined4 uVar2;
  int iVar3;
  byte bVar4;
  char *pcVar5;
  char cVar6;
  
  if ((((param_3 == (undefined1 *)0x0) || (param_4 == (byte *)0x0)) || (param_1 == 0)) ||
     (param_2 < 4)) {
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      FUN_0043d574(1,DAT_005735f4,DAT_005735f0,DAT_005738cc,0x8a4,DAT_00573200,DAT_005738cc);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0x4400000,DAT_00573300,DAT_00573300,DAT_005738cc);
    }
    return 0xffffffff;
  }
  *param_3 = 0x43;
  param_3[1] = 1;
  param_3[2] = 3;
  param_3[3] = 1;
  pcVar1 = DAT_00573c04;
  bVar4 = 4;
  *DAT_00573c04 = '\x01';
  pcVar5 = pcVar1 + 1;
  FUN_0043c0e4(pcVar5,7,0);
  uVar2 = DAT_00573c08;
  uart_sync_write(DAT_00573c08,7,0);
  cVar6 = '(';
  do {
    if (cVar6 == '\0') {
LAB_00573196:
      if (cVar6 == '\0') {
        iVar3 = FUN_0043d0ce();
        if (iVar3 << 0x1e < 0) {
          FUN_0043d574(1,DAT_005735f4,DAT_005735f0,DAT_005738cc,0x8cd,DAT_00573c14);
        }
        iVar3 = FUN_0043d0ce();
        if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
          compress_log_output(0x4000000,DAT_00573c54,DAT_00573c54);
        }
        param_3[bVar4] = 1;
        bVar4 = bVar4 + 1;
      }
      *param_4 = bVar4;
      return 0;
    }
    osDelay(1);
    if (*pcVar1 == '\0') {
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        FUN_0043d574(1,DAT_005735f4,DAT_005735f0,DAT_005738cc,0x8be,DAT_00573c0c,pcVar5);
      }
      iVar3 = FUN_0043d0ce();
      if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
        compress_log_output(0x4400000,DAT_00573c10,DAT_00573c10,pcVar5);
      }
      iVar3 = FUN_004751c8(pcVar1 + 1,uVar2,7);
      if (iVar3 == 0) {
        param_3[4] = 0;
        bVar4 = 5;
      }
      else {
        param_3[4] = 1;
        bVar4 = 5;
      }
      goto LAB_00573196;
    }
    cVar6 = cVar6 + -1;
  } while( true );
}

