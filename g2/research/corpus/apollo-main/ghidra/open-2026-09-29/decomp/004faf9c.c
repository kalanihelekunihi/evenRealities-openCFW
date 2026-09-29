
undefined8 FUN_004faf9c(undefined4 param_1,uint param_2,undefined4 param_3,undefined4 param_4)

{
  int *piVar1;
  undefined4 *puVar2;
  int iVar3;
  undefined4 uVar4;
  
  piVar1 = DAT_004fb174;
  if (*DAT_004fb174 != 0) {
    ui_common_api_fn_00509c96(*DAT_004fb174);
    *piVar1 = 0;
  }
  iVar3 = ui_common_api_fn_00509c1c();
  *piVar1 = iVar3;
  if (*piVar1 == 0) {
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      param_2 = 0x1251;
      FUN_0043d574(1,DAT_004fb13c,DAT_004fb07c,DAT_004fb188,0x1251,DAT_004fb184);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_004fb18c,DAT_004fb18c);
    }
    uVar4 = 0xffffffff;
  }
  else {
    *DAT_004fb14c = 0;
    *DAT_004fb190 = 0;
    *DAT_004fb160 = 0xffffffff;
    puVar2 = DAT_004fb194;
    *DAT_004fb194 = 0;
    puVar2[1] = 0;
    *DAT_004fb198 = 0;
    *DAT_004fb19c = 0;
    *DAT_004fb17c = 0;
    FUN_004fac74(param_1);
    *DAT_004fb178 = 1;
    if (*DAT_004fb150 == 0) {
      param_2 = 0;
      FUN_005001d2(0,0,0,0,0,param_3,param_4);
    }
    else {
      param_2 = (uint)(*(char *)((int)DAT_004fb150 + 0x129) != '\0');
      FUN_005001d2(0,0,0,*(undefined4 *)(DAT_004fb150 + 0x8a),param_2,param_3,param_4);
    }
    uVar4 = 0;
  }
  return CONCAT44(param_2,uVar4);
}

