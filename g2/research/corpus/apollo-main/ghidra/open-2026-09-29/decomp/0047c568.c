
void FUN_0047c568(undefined1 param_1,char param_2)

{
  int iVar1;
  undefined1 *puVar2;
  
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    FUN_0043d574(4,DAT_0047cb4c,DAT_0047cb48,DAT_0047cb44,0x872,DAT_0047cb40,param_1,param_2);
  }
  iVar1 = FUN_0043d0ce();
  if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
    compress_log_output(0x10800000,DAT_0047cb50,DAT_0047cb50,param_1,param_2);
  }
  FUN_0047c2bc();
  puVar2 = (undefined1 *)FUN_004bb07c(param_1);
  if (puVar2 == (undefined1 *)0x0) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(4,DAT_0047cb4c,DAT_0047cb48,DAT_0047cb44,0x8a6,DAT_0047cb8c,param_1);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x10400000,DAT_0047cb90,DAT_0047cb90,param_1);
    }
  }
  else if ((puVar2[0x30] == '\0') || ((puVar2[0x2e] & 5) == 0)) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(4,DAT_0047cb4c,DAT_0047cb48,DAT_0047cb44,0x89f,DAT_0047cb84,param_1,puVar2[0x30],
                   puVar2[0x2e]);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x10c00000,DAT_0047cb88,DAT_0047cb88,param_1,puVar2[0x30],puVar2[0x2e]);
    }
    puVar2[0x30] = 0;
    puVar2[0x2f] = 0;
  }
  else {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(2,DAT_0047cb4c,DAT_0047cb48,DAT_0047cb44,0x880,DAT_0047cb54,puVar2[5],puVar2[4],
                   puVar2[3],puVar2[2],puVar2[1],*puVar2);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x9800000,DAT_0047cb58,DAT_0047cb58,puVar2[5],puVar2[4],puVar2[3],
                          puVar2[2],puVar2[1],*puVar2);
    }
    if (param_2 == '\x01') {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        FUN_0043d574(2,DAT_0047cb4c,DAT_0047cb48,DAT_0047cb44,0x88e,DAT_0047cb6c);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0x8000000,DAT_0047cb70,DAT_0047cb70);
      }
    }
    else if (param_2 == '\x03') {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        FUN_0043d574(2,DAT_0047cb4c,DAT_0047cb48,DAT_0047cb44,0x892,DAT_0047cb74);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0x8000000,DAT_0047cb78,DAT_0047cb78);
      }
    }
    else if (param_2 == '\x04') {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        FUN_0043d574(2,DAT_0047cb4c,DAT_0047cb48,DAT_0047cb44,0x88a,DAT_0047cb64);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0x8000000,DAT_0047cb68,DAT_0047cb68);
      }
    }
    else if (param_2 == '\v') {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        FUN_0043d574(1,DAT_0047cb4c,DAT_0047cb48,DAT_0047cb44,0x885,DAT_0047cb5c);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0x4000000,DAT_0047cb60,DAT_0047cb60);
      }
    }
    else {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        FUN_0043d574(2,DAT_0047cb4c,DAT_0047cb48,DAT_0047cb44,0x896,DAT_0047cb7c,param_2);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0x8400000,DAT_0047cb80,DAT_0047cb80,param_2);
      }
    }
    FUN_0047c8cc(param_1);
  }
  return;
}

