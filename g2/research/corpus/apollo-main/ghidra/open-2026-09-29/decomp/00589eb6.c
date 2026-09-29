
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined8
FUN_00589eb6(undefined4 param_1,undefined4 param_2,undefined1 *param_3,undefined4 *param_4)

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
  if (param_3 != (undefined1 *)0xa) {
    if (param_3 == (undefined1 *)0x42) {
      iVar2 = FUN_005540b2(puVar1);
      if (iVar2 != 3) {
        puVar3 = (undefined4 *)0x0;
        if (param_4 != (undefined4 *)0x0) {
          puVar3 = (undefined4 *)*param_4;
        }
        iVar2 = FUN_0043d0ce();
        if (iVar2 << 0x1e < 0) {
          puStack_14 = PTR_s_foregroundID____d_0058a394;
          uStack_18 = 0xf7;
          puStack_10 = puVar3;
          FUN_0043d574(3,DAT_0058a320,DAT_0058a31c,PTR_s_teleprompt_page_event_handler_0058a398);
        }
        iVar2 = FUN_0043d0ce();
        if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
          compress_log_output(0xc400000,PTR_s__teleprompt_foregroundID____d_0058a39c,
                              PTR_s__teleprompt_foregroundID____d_0058a39c,puVar3);
        }
        if (((*DAT_0058a3a0 != 0) && (puVar3 != (undefined4 *)0x0)) &&
           (puVar3 != (undefined4 *)0x21)) {
          FUN_00441488(*DAT_0058a3a0,0x7f,0);
        }
        if (puVar3 == (undefined4 *)0x22) {
          FUN_00556ad4();
        }
        *(undefined1 *)(DAT_0058a368 + 0x3c) = 1;
      }
      goto LAB_00589fe4;
    }
    if (param_3 == (undefined1 *)0x43) {
      iVar2 = FUN_005540b2(puVar1);
      if (iVar2 != 3) {
        FUN_00441488(*DAT_0058a3a0,0xff,0);
        FUN_00556b00();
        FUN_00589cb4();
        *(undefined1 *)(DAT_0058a368 + 0x3c) = 0;
      }
      goto LAB_00589fe4;
    }
    if (((param_3 != (undefined1 *)0x44) && (param_3 != (undefined1 *)0x45)) &&
       ((param_3 != &SUB_00000048 && (param_3 != (undefined1 *)0x4a)))) {
      if (param_3 == (undefined1 *)0x4f) {
        iVar2 = FUN_0045a568();
        if (iVar2 == 1) {
          uStack_18 = *_DAT_0058a3a4;
          puStack_14 = (undefined1 *)_DAT_0058a3a4[1];
          FUN_0048eb32(DAT_0058a37c,2,&uStack_18);
        }
        FUN_00589b68(9,0);
      }
      goto LAB_00589fe4;
    }
  }
  FUN_00555178(puVar1,param_4);
LAB_00589fe4:
  return CONCAT44(uStack_18,1);
}

