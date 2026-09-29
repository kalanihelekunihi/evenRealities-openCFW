
void FUN_0047c8cc(undefined1 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  char cVar1;
  undefined1 *puVar2;
  int iVar3;
  
  puVar2 = (undefined1 *)FUN_004bb07c(param_1);
  if (puVar2 == (undefined1 *)0x0) {
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      FUN_0043d574(4,DAT_0047cb4c,DAT_0047cb48,DAT_0047cb98,0x8d0,DAT_0047cbb8,param_1);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0x10400000,DAT_0047cbbc,DAT_0047cbbc,param_1);
    }
  }
  else if ((puVar2[0x30] == '\0') || ((puVar2[0x2e] & 5) == 0)) {
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      FUN_0043d574(4,DAT_0047cb4c,DAT_0047cb48,DAT_0047cb98,0x8c9,DAT_0047cbb0,param_1,puVar2[0x30],
                   puVar2[0x2e]);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0x10c00000,DAT_0047cbb4,DAT_0047cbb4,param_1,puVar2[0x30],puVar2[0x2e]);
    }
    puVar2[0x30] = 0;
    puVar2[0x2f] = 0;
  }
  else {
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      FUN_0043d574(2,DAT_0047cb4c,DAT_0047cb48,DAT_0047cb98,0x8bb,DAT_0047cb94,puVar2[5],puVar2[4],
                   puVar2[3],puVar2[2],puVar2[1],*puVar2,param_4);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0x9800000,DAT_0047cb9c,DAT_0047cb9c,puVar2[5],puVar2[4],puVar2[3],
                          puVar2[2],puVar2[1],*puVar2);
    }
    cVar1 = FUN_0047b59c(puVar2[6],puVar2);
    if (cVar1 == '\0') {
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        FUN_0043d574(1,DAT_0047cb4c,DAT_0047cb48,DAT_0047cb98,0x8c2,DAT_0047cba8);
      }
      iVar3 = FUN_0043d0ce();
      if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
        compress_log_output(0x4000000,DAT_0047cbac,DAT_0047cbac);
      }
    }
    else {
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        FUN_0043d574(4,DAT_0047cb4c,DAT_0047cb48,DAT_0047cb98,0x8c0,DAT_0047cba0);
      }
      iVar3 = FUN_0043d0ce();
      if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
        compress_log_output(0x10000000,DAT_0047cba4);
      }
    }
    FUN_004b4720();
  }
  return;
}

