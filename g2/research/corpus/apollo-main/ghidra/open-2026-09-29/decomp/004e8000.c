
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined8 FUN_004e8000(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int *piVar1;
  undefined4 *puVar2;
  undefined4 *puVar3;
  int iVar4;
  
  puVar3 = _DAT_004e8a6c;
  puVar2 = _DAT_004e8a68;
  *_DAT_004e8a6c = *_DAT_004e8a68;
  iVar4 = FUN_0043d0ce();
  if (iVar4 << 0x1e < 0) {
    param_4 = *puVar3;
    param_2 = 0x35b;
    param_3 = _DAT_004e8a70;
    FUN_0043d574(3,DAT_004e8a7c,DAT_004e8a78,_DAT_004e8a74,0x35b,_DAT_004e8a70,param_4);
  }
  iVar4 = FUN_0043d0ce();
  if (-1 < iVar4 << 0x1f) {
    iVar4 = FUN_0043d0ce();
    if (-1 < iVar4 << 0x1d) goto LAB_004e8058;
  }
  compress_log_output(0xc400000,_DAT_004e8a80,_DAT_004e8a80,*puVar3,param_2,param_3,param_4);
LAB_004e8058:
  iVar4 = FUN_00558142();
  if (iVar4 != 0) {
    FUN_00439be4(_DAT_004e8a84,iVar4,0x80);
    *_DAT_004e8a88 = 1;
  }
  *puVar2 = 0;
  *_DAT_004e8a8c = 0;
  *DAT_004e83bc = 0;
  *DAT_004e8bb8 = 0;
  dashboard_watchface_manager_deinit();
  *DAT_004e836c = 0;
  *_DAT_004e8bbc = 0;
  *_DAT_004e8bc0 = 0;
  *_DAT_004e8138 = 200;
  piVar1 = DAT_004e8430;
  if (*DAT_004e8430 != 0) {
    ui_common_api_fn_00509c96(*DAT_004e8430);
    *piVar1 = 0;
  }
  FUN_004efeb0();
  FUN_004ed6c4();
  FUN_004fb08c();
  FUN_004f4ed8();
  FUN_004fd840();
  return CONCAT44(param_3,param_2);
}

