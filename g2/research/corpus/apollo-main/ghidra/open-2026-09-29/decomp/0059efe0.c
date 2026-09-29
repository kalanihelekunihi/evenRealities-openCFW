
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined8
FUN_0059efe0(undefined4 param_1,undefined4 param_2,undefined1 *param_3,undefined4 *param_4)

{
  undefined1 *puVar1;
  int iVar2;
  undefined4 *puVar3;
  undefined4 uStack_18;
  undefined1 *puStack_14;
  undefined4 *puStack_10;
  
  if (param_3 == (undefined1 *)0x44) {
    puVar1 = (undefined1 *)0x45;
  }
  else {
    puVar1 = param_3;
    if (param_3 == (undefined1 *)0x45) {
      puVar1 = (undefined1 *)0x44;
    }
  }
  uStack_18 = param_2;
  puStack_14 = param_3;
  puStack_10 = param_4;
  if (puVar1 != (undefined1 *)0xa) {
    if (puVar1 == (undefined1 *)0x42) {
      iVar2 = translate_ui_0059db5c();
      if (iVar2 != 2) {
        puVar3 = (undefined4 *)0x0;
        if (param_4 != (undefined4 *)0x0) {
          puVar3 = (undefined4 *)*param_4;
        }
        iVar2 = FUN_0043d0ce();
        if (iVar2 << 0x1e < 0) {
          puStack_14 = PTR_s_foregroundID____d_0059f4a4;
          uStack_18 = 0xe4;
          puStack_10 = puVar3;
          FUN_0043d574(3,DAT_0059f414,DAT_0059f410,PTR_s_translate_page_event_handler_0059f4a8);
        }
        iVar2 = FUN_0043d0ce();
        if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
          compress_log_output(0xc400000,PTR_s__translate_foregroundID____d_0059f4ac,
                              PTR_s__translate_foregroundID____d_0059f4ac,puVar3);
        }
        if (((*DAT_0059f4b0 != 0) && (puVar3 != (undefined4 *)0x0)) &&
           (puVar3 != (undefined4 *)0x21)) {
          FUN_00441488(*DAT_0059f4b0,0x7f,0);
        }
      }
      goto LAB_0059f0e8;
    }
    if (puVar1 == (undefined1 *)0x43) {
      iVar2 = translate_ui_0059db5c();
      if (iVar2 != 2) {
        FUN_00441488(*DAT_0059f4b0,0xff,0);
      }
      goto LAB_0059f0e8;
    }
    if (((puVar1 != (undefined1 *)0x44) && (puVar1 != (undefined1 *)0x45)) &&
       (puVar1 != &SUB_00000048)) {
      if (puVar1 == (undefined1 *)0x4f) {
        iVar2 = FUN_0045a568();
        if (iVar2 == 1) {
          uStack_18 = *_DAT_0059f4b4;
          puStack_14 = (undefined1 *)_DAT_0059f4b4[1];
          FUN_0048eb32(DAT_0059f46c,2,&uStack_18);
        }
        FUN_0059ec28(7,0);
      }
      goto LAB_0059f0e8;
    }
  }
  translate_ui_0059da94(puVar1,param_4);
LAB_0059f0e8:
  return CONCAT44(uStack_18,1);
}

