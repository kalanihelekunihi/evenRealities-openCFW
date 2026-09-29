
undefined8 FUN_005537cc(byte param_1,undefined4 param_2,undefined4 param_3,uint param_4)

{
  undefined4 uVar1;
  int iVar2;
  int iVar3;
  
  iVar2 = DAT_00553ff0;
  if ((*DAT_00553d44 == '\0') || (3 < param_1)) {
    uVar1 = 0xffffffff;
  }
  else if (*(int *)(DAT_00553ff0 + (uint)param_1 * 4) == 0) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      param_4 = (uint)param_1;
      param_2 = 0x118;
      param_3 = DAT_00553ff4;
      FUN_0043d574(1,DAT_00554000,DAT_00553ffc,DAT_00553ff8,0x118,DAT_00553ff4,param_4);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x4400000,DAT_00554004,DAT_00554004,param_1,param_2,param_3,param_4);
    }
    uVar1 = 0xffffffff;
  }
  else {
    FUN_0055389a();
    iVar3 = FUN_00463e9a(*(undefined4 *)(iVar2 + (uint)param_1 * 4));
    if (iVar3 != 0) {
      FUN_0043dfa4(iVar3,1);
    }
    FUN_00463ea6(*(undefined4 *)(iVar2 + (uint)param_1 * 4));
    FUN_0043c0e4(DAT_00553fec + (uint)param_1 * 0x10,0x10,0);
    *DAT_00553fe8 = param_1;
    *DAT_00554008 = param_1;
    uVar1 = 0;
  }
  return CONCAT44(param_2,uVar1);
}

