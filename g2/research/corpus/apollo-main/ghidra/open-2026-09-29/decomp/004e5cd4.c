
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined8
even_ai_input_event_adapter
          (undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int *piVar1;
  int iVar2;
  undefined4 uStack_18;
  undefined4 uStack_14;
  undefined4 uStack_10;
  
  *DAT_004e6550 = 0;
  piVar1 = _DAT_004e6554;
  uStack_18 = param_2;
  uStack_14 = param_3;
  if ((*_DAT_004e6554 != 0) &&
     (uStack_10 = param_4, iVar2 = ui_common_api_fn_00509dfa(*_DAT_004e6554), iVar2 == 0)) {
    FUN_0043c0e4(&uStack_18,6,0);
    iVar2 = ui_common_api_fn_00509e14(*piVar1,&uStack_18,6);
    if (-1 < iVar2) {
      EvenAI_InputEventWarp(&uStack_18,6);
    }
  }
  return CONCAT44(uStack_14,uStack_18);
}

