
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined8 FUN_00511882(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 uVar1;
  int iVar2;
  int iVar3;
  
  uVar1 = FUN_0055ef6c(DAT_00511984,0);
  iVar2 = FUN_0055ef76(uVar1,0);
  if (iVar2 != DAT_00511964) {
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      param_1 = 0x223;
      param_2 = _DAT_005122c4;
      FUN_0043d574(1,DAT_00511958,DAT_00511954,_DAT_005122c8,0x223,_DAT_005122c4,iVar2,param_4);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0x4400000,_DAT_00512470,_DAT_00512470,iVar2);
    }
  }
  return CONCAT44(param_2,param_1);
}

