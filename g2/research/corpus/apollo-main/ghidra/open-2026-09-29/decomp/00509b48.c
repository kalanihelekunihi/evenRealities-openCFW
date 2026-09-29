
void APP_errorFaultHandler(char *param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  byte bVar1;
  int iVar2;
  undefined1 auStack_210 [512];
  undefined4 uStack_10;
  
  uStack_10 = param_4;
  FUN_0043c0e4(auStack_210,0x200,0);
  if (*param_1 == '\0') {
    bVar1 = 0;
    while (*(short *)(param_1 + 4) != *(short *)(DAT_00509bfc + (uint)bVar1 * 8)) {
      bVar1 = bVar1 + 1;
    }
    FUN_004b4728(auStack_210,DAT_00509c00,*(undefined2 *)(param_1 + 4),
                 *(undefined4 *)(DAT_00509bfc + (uint)bVar1 * 8 + 4));
  }
  else if (*param_1 == '\x01') {
    FUN_004b4728(auStack_210,DAT_00509c04,*(undefined4 *)(param_1 + 4));
  }
  iVar2 = FUN_0043d0ce();
  if (iVar2 << 0x1e < 0) {
    FUN_0043d574(1,DAT_00509c14,DAT_00509c10,DAT_00509c0c,0x71,DAT_00509c08,
                 *(undefined4 *)(param_1 + 8),*(undefined4 *)(param_1 + 0xc),
                 *(undefined4 *)(param_1 + 0x10),auStack_210);
  }
  iVar2 = FUN_0043d0ce();
  if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
    compress_log_output(0x5000000,DAT_00509c18,DAT_00509c18,*(undefined4 *)(param_1 + 8),
                        *(undefined4 *)(param_1 + 0xc),*(undefined4 *)(param_1 + 0x10),auStack_210);
  }
  return;
}

