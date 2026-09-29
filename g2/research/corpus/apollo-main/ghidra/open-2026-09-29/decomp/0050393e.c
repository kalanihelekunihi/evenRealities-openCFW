
undefined8
FUN_0050393e(undefined2 *param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  byte bVar1;
  int iVar2;
  int iVar3;
  undefined2 *puVar4;
  
  iVar2 = DAT_005040bc;
  if (*(char *)(DAT_005040bc + 0x9c) == '\0') {
    iVar2 = FUN_0043d0ce();
    puVar4 = param_1;
    if (iVar2 << 0x1e < 0) {
      puVar4 = (undefined2 *)0x24a;
      param_2 = DAT_005040d8;
      FUN_0043d574(2,DAT_005040e0,DAT_005040d0,DAT_005040dc,0x24a,DAT_005040d8,param_3,param_4);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x8000000,DAT_005040e4,DAT_005040e4);
    }
  }
  else {
    puVar4 = param_1;
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      puVar4 = (undefined2 *)0x24e;
      param_2 = DAT_005040e8;
      FUN_0043d574(4,DAT_005040e0,DAT_005040d0,DAT_005040dc,0x24e,DAT_005040e8,
                   *(undefined1 *)((int)param_1 + 3));
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0x10400000,DAT_005040ec,DAT_005040ec,*(undefined1 *)((int)param_1 + 3));
    }
    bVar1 = *(byte *)(iVar2 + 0x97);
    if (*(char *)((int)param_1 + 3) == '\0') {
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        puVar4 = (undefined2 *)0x256;
        param_2 = DAT_005040f0;
        FUN_0043d574(4,DAT_005040e0,DAT_005040d0,DAT_005040dc,0x256,DAT_005040f0,*param_1);
      }
      iVar3 = FUN_0043d0ce();
      if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
        compress_log_output(0x10400000,DAT_005040f4,DAT_005040f4,*param_1);
      }
      iVar3 = FUN_0047ab6c(iVar2 + (uint)bVar1 * 0xf,*param_1);
      if (iVar3 == 0) {
        iVar3 = FUN_0043d0ce();
        if (iVar3 << 0x1e < 0) {
          puVar4 = (undefined2 *)0x25f;
          param_2 = DAT_00504100;
          FUN_0043d574(2,DAT_005040e0,DAT_005040d0,DAT_005040dc);
        }
        iVar3 = FUN_0043d0ce();
        if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
          compress_log_output(0x8000000,DAT_00504104,DAT_00504104);
        }
      }
      else {
        iVar3 = FUN_0043d0ce();
        if (iVar3 << 0x1e < 0) {
          puVar4 = (undefined2 *)0x25b;
          param_2 = DAT_005040f8;
          FUN_0043d574(4,DAT_005040e0,DAT_005040d0,DAT_005040dc);
        }
        iVar3 = FUN_0043d0ce();
        if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
          compress_log_output(0x10000000,DAT_005040fc,DAT_005040fc);
        }
      }
    }
    else {
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        puVar4 = (undefined2 *)0x264;
        param_2 = DAT_00504108;
        FUN_0043d574(2,DAT_005040e0,DAT_005040d0,DAT_005040dc,0x264,DAT_00504108,
                     *(undefined1 *)((int)param_1 + 3));
      }
      iVar3 = FUN_0043d0ce();
      if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
        compress_log_output(0x8400000,DAT_0050410c,DAT_0050410c,*(undefined1 *)((int)param_1 + 3));
      }
    }
    *(undefined1 *)(iVar2 + 0x9c) = 0;
  }
  return CONCAT44(param_2,puVar4);
}

