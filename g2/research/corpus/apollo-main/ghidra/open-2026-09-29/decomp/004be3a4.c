
void efsProcCccState(undefined2 *param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined1 *puVar1;
  int iVar2;
  
  if (*(char *)(param_1 + 4) == '\x04') {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(4,DAT_004be6a4,DAT_004be6a0,DAT_004be69c,0x41,DAT_004be698,param_1[3],param_1[2],
                   *(undefined1 *)(param_1 + 4),param_4);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x10c00000,DAT_004be6a8,DAT_004be6a8,param_1[3],param_1[2],
                          *(undefined1 *)(param_1 + 4));
    }
    puVar1 = DAT_004be6ac;
    if (param_1[3] == 1) {
      *DAT_004be6ac = (char)*param_1;
      puVar1[2] = 1;
    }
    else {
      *DAT_004be6ac = 0;
      puVar1[2] = 0;
    }
  }
  return;
}

