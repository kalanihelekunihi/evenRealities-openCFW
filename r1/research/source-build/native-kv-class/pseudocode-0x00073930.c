/* ================================================================
 * entry: 0x00073930
 * end:   0x00073963
 * size:  52 bytes
 * name:  FUN_00073930
 * ================================================================ */

undefined4 FUN_00073930(int param_1,undefined4 param_2,uint param_3)

{
  int iVar1;
  undefined4 uVar2;

  iVar1 = DAT_00073964;
  if (*(ushort *)(param_1 + 0x14) == param_3) {
    (**(code **)(*(int *)(DAT_00073964 + 4) + 0x1c))();
    FUN_0002775c(param_2,param_1 + 0x18,param_3);
    (**(code **)(*(int *)(iVar1 + 4) + 0x20))();
    uVar2 = 0;
  }
  else {
    uVar2 = 5;
  }
  return uVar2;
}



