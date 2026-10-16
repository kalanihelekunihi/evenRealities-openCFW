/* ================================================================
 * entry: 0x00073968
 * end:   0x000739a3
 * size:  60 bytes
 * name:  FUN_00073968
 * ================================================================ */

undefined4 FUN_00073968(int param_1,undefined4 param_2,uint param_3)

{
  int iVar1;
  undefined4 uVar2;

  iVar1 = DAT_000739a4;
  if (*(ushort *)(param_1 + 0x14) == param_3) {
    (**(code **)(*(int *)(DAT_000739a4 + 4) + 0x1c))();
    *(ushort *)(param_1 + 0x12) = *(ushort *)(param_1 + 0x12) | 1;
    FUN_0002775c(param_1 + 0x18,param_2,param_3);
    (**(code **)(*(int *)(iVar1 + 4) + 0x20))();
    uVar2 = 0;
  }
  else {
    uVar2 = 5;
  }
  return uVar2;
}



