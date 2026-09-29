
void FUN_005ecc74(undefined1 *param_1,uint param_2,undefined4 *param_3)

{
  uint uVar1;
  
  if (((param_1 != (undefined1 *)0x0) && (param_2 != 0)) &&
     (*param_1 = 0, param_3 != (undefined4 *)0x0)) {
    uVar1 = (uint)*(ushort *)(param_3 + 1);
    if (param_2 <= uVar1) {
      uVar1 = param_2 - 1;
    }
    if (uVar1 != 0) {
      FUN_00439be4(param_1,(int)param_3 + 6,uVar1);
    }
    param_1[uVar1] = 0;
    if (uVar1 == 0) {
      FUN_0044b728(param_1,param_2,DAT_005ed8d8,*param_3);
    }
  }
  return;
}

