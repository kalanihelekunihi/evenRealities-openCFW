
undefined8 FUN_005b43ee(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined2 *puVar1;
  ushort *puVar2;
  int iVar3;
  
  puVar2 = DAT_005b48bc;
  if (param_1 == 0) {
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      param_1 = 0x108;
      param_2 = DAT_005b48b0;
      FUN_0043d574(1,DAT_005b485c,DAT_005b4858,DAT_005b48b4,0x108,DAT_005b48b0,param_3,param_4);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_005b48b8,DAT_005b48b8);
    }
  }
  else {
    FUN_00439be4(DAT_005b48bc,param_1,0x88);
    if (*puVar2 < 0x80) {
      *(undefined1 *)((int)puVar2 + *puVar2 + 2) = 0;
    }
    FUN_0043c0e4(DAT_005b48c0,0x36b1,0);
    puVar1 = DAT_005b484c;
    FUN_0043c0e4(DAT_005b484c,0x6d6c,0);
    *puVar1 = (short)*(undefined4 *)(puVar2 + 0x42);
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      param_1 = 0x116;
      param_2 = DAT_005b48c4;
      FUN_0043d574(3,DAT_005b485c,DAT_005b4858,DAT_005b48b4,0x116,DAT_005b48c4,*puVar2,
                   *(undefined4 *)(puVar2 + 0x42));
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      param_1 = *(int *)(puVar2 + 0x42);
      compress_log_output(0xc800000,DAT_005b48c8,DAT_005b48c8,*puVar2);
    }
  }
  return CONCAT44(param_2,param_1);
}

