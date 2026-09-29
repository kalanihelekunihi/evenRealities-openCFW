
void nusProcCccState(undefined2 *param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined1 *puVar1;
  int iVar2;
  
  if (*(char *)(param_1 + 4) == '\x05') {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(4,DAT_004be9c4,DAT_004be9c0,DAT_004be9bc,0x43,DAT_004be9b8,param_1[3],param_1[2],
                   *(undefined1 *)(param_1 + 4),param_4);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x10c00000,DAT_004be9c8,DAT_004be9c8,param_1[3],param_1[2],
                          *(undefined1 *)(param_1 + 4));
    }
    puVar1 = DAT_004be9cc;
    if (param_1[3] == 1) {
      *DAT_004be9cc = (char)*param_1;
      puVar1[2] = 1;
    }
    else {
      *DAT_004be9cc = 0;
      puVar1[2] = 0;
    }
  }
  return;
}

