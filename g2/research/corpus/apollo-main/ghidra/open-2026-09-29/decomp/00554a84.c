
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined8 FUN_00554a84(int param_1,uint param_2,int param_3,uint param_4)

{
  int iVar1;
  int iVar2;
  uint uVar3;
  
  iVar1 = DAT_00554d28;
  if (param_1 == 0) {
    iVar1 = FUN_0043d0ce();
    uVar3 = param_2;
    if (iVar1 << 0x1e < 0) {
      uVar3 = 0x23a;
      FUN_0043d574(1,DAT_00554d3c,DAT_00554d38,_DAT_00555590,0x23a,DAT_005551d8,param_4);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_005551e0,DAT_005551e0);
    }
    iVar2 = 0;
  }
  else {
    uVar3 = param_2;
    iVar2 = FUN_00554968(param_1,*(undefined4 *)(DAT_00554d28 + 0x2c));
    if (param_2 < *(uint *)(iVar1 + 0x2c)) {
      iVar2 = 0;
    }
    else if (param_2 <= *(int *)(iVar1 + 0x2c) + 3U) {
      iVar1 = param_3 * 0x1c + (param_2 - *(int *)(iVar1 + 0x2c)) * 0x118;
      if ((param_4 & 0xff) != 0) {
        iVar1 = iVar1 + -0x1c;
      }
      if ((iVar1 <= iVar2) && (iVar2 = iVar1, iVar1 < 0)) {
        iVar2 = 0;
      }
    }
  }
  return CONCAT44(uVar3,iVar2);
}

