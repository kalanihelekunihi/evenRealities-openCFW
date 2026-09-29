
undefined8
service_even_ai_fn_00498528(char param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined2 local_c;
  char cStack_a;
  undefined1 uStack_9;
  
  local_c = (undefined2)param_4;
  cStack_a = (char)((uint)param_4 >> 0x10);
  uStack_9 = (undefined1)((uint)param_4 >> 0x18);
  if (*DAT_004985a8 != '\0') {
    if ((param_1 != '\x01') && (param_1 != '\x02')) {
      if (param_1 != '\x03') goto LAB_004985a2;
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        local_c = (undefined2)DAT_00498624;
        cStack_a = (char)((uint)DAT_00498624 >> 0x10);
        uStack_9 = (undefined1)((uint)DAT_00498624 >> 0x18);
        FUN_0043d574(2,DAT_004985bc,DAT_004985b8,DAT_00498628,0x1a8);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0x8000000,DAT_0049862c,DAT_0049862c);
      }
    }
    local_c = (undefined2)*DAT_00498630;
    uStack_9 = (undefined1)((uint)*DAT_00498630 >> 0x18);
    param_3 = 5;
    cStack_a = param_1;
    FUN_00464f76(7,&local_c,3,DAT_0049861c);
  }
LAB_004985a2:
  return CONCAT17(uStack_9,CONCAT16(cStack_a,CONCAT24(local_c,param_3)));
}

