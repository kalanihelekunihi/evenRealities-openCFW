
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined8 FUN_00511108(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 *puVar2;
  undefined4 uVar3;
  int iVar4;
  int iVar5;
  uint uVar6;
  
  puVar2 = _DAT_00511974;
  _DAT_00511974[1] = _DAT_00511978;
  *puVar2 = _DAT_0051197c;
  puVar2[2] = *_DAT_00511980;
  uVar3 = DAT_00511984;
  iVar4 = FUN_0055eb3e(DAT_00511984,puVar2,0,1,param_2,param_3,param_4);
  iVar1 = DAT_00511964;
  if (iVar4 != DAT_00511964) {
    iVar5 = FUN_0043d0ce();
    if (iVar5 << 0x1e < 0) {
      param_2 = 0x169;
      param_3 = _DAT_00511988;
      FUN_0043d574(1,DAT_00511958,DAT_00511954,_DAT_0051198c,0x169,_DAT_00511988,iVar4);
    }
    iVar5 = FUN_0043d0ce();
    if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
      compress_log_output(0x4400000,_DAT_00511b6c,_DAT_00511b6c,iVar4);
    }
  }
  for (uVar6 = 0; uVar6 < 8; uVar6 = uVar6 + 1) {
    iVar4 = func_0x0055ee04(uVar3,uVar6,0xff);
    if (iVar4 != iVar1) {
      iVar5 = FUN_0043d0ce();
      if (iVar5 << 0x1e < 0) {
        param_2 = 0x171;
        param_3 = _DAT_00511b70;
        FUN_0043d574(1,DAT_00511958,DAT_00511954,_DAT_0051198c,0x171,_DAT_00511b70,iVar4);
      }
      iVar5 = FUN_0043d0ce();
      if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
        compress_log_output(0x4400000,PTR_s__npmx_driver_ERROR__npmx_core_ev_00511bc4,
                            PTR_s__npmx_driver_ERROR__npmx_core_ev_00511bc4,iVar4);
      }
    }
  }
  return CONCAT44(param_3,param_2);
}

