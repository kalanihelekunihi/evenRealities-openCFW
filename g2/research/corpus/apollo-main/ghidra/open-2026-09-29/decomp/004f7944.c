
void FUN_004f7944(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  bool bVar1;
  int *piVar2;
  int iVar3;
  int iVar4;
  undefined4 uVar5;
  undefined4 uVar6;
  int iVar7;
  int local_34;
  int local_30;
  undefined1 auStack_2c [4];
  undefined1 auStack_28 [4];
  undefined4 uStack_24;
  
  piVar2 = DAT_004f8090;
  uVar6 = *DAT_004f81e4;
  if (*DAT_004f8090 == 0) {
    *DAT_004f7f14 = 0;
  }
  else {
    uStack_24 = param_4;
    FUN_004f6fc4(uVar6,auStack_28,&local_34,auStack_2c,&local_30);
    iVar3 = FUN_0043fdda(*piVar2);
    iVar4 = FUN_0044e498(*piVar2);
    bVar1 = false;
    if (local_34 - iVar4 < 0) {
      bVar1 = true;
      iVar7 = local_34;
    }
    else {
      iVar7 = iVar4;
      if (iVar3 < local_30 + (local_34 - iVar4)) {
        iVar7 = (local_30 + local_34) - iVar3;
        bVar1 = true;
      }
    }
    if (0x110 < (local_30 + local_34) - iVar4) {
      iVar7 = local_30 + local_34 + -0x110;
      bVar1 = true;
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        FUN_0043d574(4,DAT_004f81e0,DAT_004f81dc,DAT_004f833c,0x9d0,DAT_004f8338,iVar7);
      }
      iVar3 = FUN_0043d0ce();
      if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
        compress_log_output(0x10400000,DAT_004f8340,DAT_004f8340,iVar7);
      }
    }
    if (bVar1) {
      uVar5 = FUN_004f6d84(*piVar2,iVar7);
      FUN_004f6e6c(*piVar2,uVar5,100,DAT_004f7f10);
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        FUN_0043d574(4,DAT_004f81e0,DAT_004f81dc,DAT_004f833c,0x9d9,DAT_004f8344,uVar6,iVar4,uVar5);
      }
      iVar3 = FUN_0043d0ce();
      if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
        compress_log_output(0x10c00000,DAT_004f8610,DAT_004f8610,uVar6,iVar4,uVar5);
      }
    }
    else {
      FUN_004f7794(param_1);
    }
  }
  return;
}

