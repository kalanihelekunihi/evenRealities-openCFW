
undefined4 FUN_005b44d8(uint *param_1)

{
  ushort *puVar1;
  int iVar2;
  undefined4 uVar3;
  uint uVar4;
  ushort uVar5;
  
  iVar2 = DAT_005b48c0;
  puVar1 = DAT_005b484c;
  if (param_1 == (uint *)0x0) {
    iVar2 = FUN_0043d0ce(0,0);
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(1,DAT_005b485c,DAT_005b4858,DAT_005b48d0,0x120,DAT_005b48cc);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_005b48d4,DAT_005b48d4);
    }
    uVar3 = 0xffffffff;
  }
  else if (*DAT_005b484c == 0) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(2,DAT_005b485c,DAT_005b4858,DAT_005b48d0,0x125,DAT_005b48d8);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x8000000,DAT_005b48dc);
    }
    uVar3 = 0xffffffff;
  }
  else {
    uVar4 = *param_1;
    if ((uVar4 & 0xffff) == (uint)DAT_005b484c[1]) {
      if ((uVar4 & 0xffff) < (uint)*DAT_005b484c) {
        if ((ushort)param_1[1] < 0x36b1) {
          uVar5 = (ushort)param_1[1];
        }
        else {
          uVar5 = 14000;
        }
        if ((ushort)(14000 - DAT_005b484c[2]) < uVar5) {
          uVar5 = 14000 - DAT_005b484c[2];
        }
        if (uVar5 != 0) {
          FUN_00439be4(DAT_005b48c0 + (uint)DAT_005b484c[2],(int)param_1 + 6,uVar5);
          puVar1[2] = uVar5 + puVar1[2];
          *(undefined1 *)(iVar2 + (uint)puVar1[2]) = 0;
        }
        puVar1[1] = puVar1[1] + 1;
        *(bool *)(puVar1 + 4) = *puVar1 <= puVar1[1];
        if ((char)puVar1[4] != '\0') {
          FUN_005b4164(DAT_005b48c0,puVar1[2]);
        }
        iVar2 = FUN_0043d0ce();
        if (iVar2 << 0x1e < 0) {
          FUN_0043d574(3,DAT_005b485c,DAT_005b4858,DAT_005b48d0,0x154,DAT_005b48f0,uVar4 & 0xffff,
                       uVar5,puVar1[2],puVar1[1],*puVar1,(char)puVar1[4] != '\0');
        }
        iVar2 = FUN_0043d0ce();
        if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
          compress_log_output(0xd800000,DAT_005b48f4,DAT_005b48f4,uVar4 & 0xffff,uVar5,puVar1[2],
                              puVar1[1],*puVar1,(char)puVar1[4] != '\0');
        }
        uVar3 = 0;
      }
      else {
        iVar2 = FUN_0043d0ce();
        if (iVar2 << 0x1e < 0) {
          FUN_0043d574(2,DAT_005b485c,DAT_005b4858,DAT_005b48d0,0x134,DAT_005b48e8,uVar4 & 0xffff,
                       *puVar1);
        }
        iVar2 = FUN_0043d0ce();
        if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
          compress_log_output(0x8800000,DAT_005b48ec,DAT_005b48ec,uVar4 & 0xffff,*puVar1);
        }
        uVar3 = 0xffffffff;
      }
    }
    else {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        FUN_0043d574(2,DAT_005b485c,DAT_005b4858,DAT_005b48d0,0x12d,DAT_005b48e0,uVar4 & 0xffff,
                     puVar1[1]);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0x8800000,DAT_005b48e4,DAT_005b48e4,uVar4 & 0xffff,puVar1[1]);
      }
      uVar3 = 0xffffffff;
    }
  }
  return uVar3;
}

