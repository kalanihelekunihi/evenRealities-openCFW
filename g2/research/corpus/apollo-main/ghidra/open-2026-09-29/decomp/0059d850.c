
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined8
translate_ui_0059d850(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 *puVar1;
  undefined4 uVar2;
  int iVar3;
  undefined4 uStack_10;
  undefined4 uStack_c;
  
  puVar1 = DAT_0059df78;
  uVar2 = FUN_0043de82();
  *puVar1 = uVar2;
  FUN_0043f4c0(*puVar1,0x240,0x120);
  FUN_0043f6b8(*puVar1,2,0,0);
  FUN_0044129e(*puVar1,0,0);
  FUN_0044131c(*puVar1,0,0);
  FUN_0044146a(*puVar1,0,0);
  translate_ui_0059d380(*puVar1,0,0);
  FUN_0043dfa4(*puVar1,0x70);
  iVar3 = FUN_0043d0ce();
  uStack_10 = param_3;
  uStack_c = param_4;
  if (iVar3 << 0x1e < 0) {
    uStack_c = _DAT_0059e260;
    uStack_10 = 0xce;
    FUN_0043d574(4,DAT_0059defc,DAT_0059def8,_DAT_0059e264);
  }
  iVar3 = FUN_0043d0ce();
  if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
    compress_log_output(0x10000000,PTR_s__translate_ui_Main_page_containe_0059e54c,
                        PTR_s__translate_ui_Main_page_containe_0059e54c);
  }
  return CONCAT44(uStack_c,uStack_10);
}

