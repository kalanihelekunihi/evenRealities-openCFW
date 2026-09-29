
void FUN_004f81f0(void)

{
  int *piVar1;
  int iVar2;
  undefined4 local_30;
  undefined4 local_2c;
  undefined1 auStack_28 [24];
  undefined1 auStack_10 [4];
  undefined1 auStack_c [4];
  
  FUN_004f8298();
  FUN_00439c04(auStack_28,DAT_004f8904,0x20);
  local_30 = FUN_00441094();
  FUN_00439be4(auStack_10,&local_30,3);
  local_30 = FUN_004410a6();
  FUN_00439be4(auStack_c,&local_30,3);
  piVar1 = DAT_004f8fbc;
  iVar2 = FUN_00463c68(*DAT_004f8908,auStack_28);
  *piVar1 = iVar2;
  if (*piVar1 == 0) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      local_2c = DAT_004f890c;
      local_30 = 0xbca;
      FUN_0043d574(1,DAT_004f8918,DAT_004f8914,DAT_004f8910);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_004f8fc0,DAT_004f8fc0);
    }
  }
  else {
    FUN_0043f09a(*(undefined4 *)*piVar1,0,2);
  }
  return;
}

