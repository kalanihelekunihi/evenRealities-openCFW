
undefined8 FUN_004e7802(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int *piVar1;
  int iVar2;
  undefined1 uStack_18;
  undefined2 uStack_17;
  undefined1 uStack_15;
  undefined4 uStack_14;
  undefined4 uStack_10;
  
  uStack_18 = (undefined1)param_2;
  uStack_17 = (undefined2)((uint)param_2 >> 8);
  uStack_15 = (undefined1)((uint)param_2 >> 0x18);
  uStack_14 = param_3;
  uStack_10 = param_4;
  iVar2 = FUN_0043d0ce();
  if (iVar2 << 0x1e < 0) {
    uStack_14 = DAT_004e8140;
    uStack_18 = 0x7f;
    uStack_17 = 1;
    uStack_15 = 0;
    FUN_0043d574(4,DAT_004e7fe8,DAT_004e7fe4,DAT_004e8144);
  }
  iVar2 = FUN_0043d0ce();
  if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
    compress_log_output(0x10000000,DAT_004e8148,DAT_004e8148);
  }
  *DAT_004e83bc = 0;
  piVar1 = DAT_004e8430;
  if ((*DAT_004e8430 != 0) && (iVar2 = ui_common_api_fn_00509dfa(*DAT_004e8430), iVar2 == 0)) {
    FUN_0043c0e4(&uStack_18,10,0);
    ui_common_api_fn_00509e14(*piVar1,&uStack_18,5);
    FUN_004e8bcc(uStack_18,CONCAT13((undefined1)uStack_14,CONCAT12(uStack_15,uStack_17)));
  }
  return CONCAT44(uStack_14,CONCAT13(uStack_15,CONCAT21(uStack_17,uStack_18)));
}

