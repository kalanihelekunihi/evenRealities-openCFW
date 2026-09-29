
undefined8 pt_cmd_1B_handler(int param_1,byte param_2,undefined1 *param_3,byte *param_4)

{
  int iVar1;
  undefined4 uVar2;
  uint uVar3;
  byte bVar4;
  uint in_fpscr;
  undefined4 uVar5;
  undefined4 extraout_s1;
  undefined4 extraout_s1_00;
  double dVar6;
  undefined4 extraout_s1_01;
  int local_28 [2];
  
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    FUN_0043d574(3,DAT_00572ae8,DAT_00572ae4,DAT_00572ae0,0x712,DAT_00572adc);
  }
  iVar1 = FUN_0043d0ce();
  if (-1 < iVar1 << 0x1f) {
    iVar1 = FUN_0043d0ce();
    if (-1 < iVar1 << 0x1d) goto LAB_00572060;
  }
  compress_log_output(0xc000000,DAT_00572aec,DAT_00572aec);
LAB_00572060:
  if ((((param_3 == (undefined1 *)0x0) || (param_4 == (byte *)0x0)) || (param_1 == 0)) ||
     (param_2 < 4)) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(1,DAT_00572ae8,DAT_00572ae4,DAT_00572ae0,0x715,DAT_005726ec,DAT_00572ae0);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x4400000,DAT_00572850,DAT_00572850,DAT_00572ae0);
    }
    uVar2 = 0xffffffff;
  }
  else {
    *param_3 = 0x20;
    param_3[1] = 1;
    param_3[2] = 3;
    param_3[3] = 0x20;
    bVar4 = 4;
    uVar2 = FUN_0058f8e4();
    uVar5 = FUN_0058f970(uVar2);
    local_28[0] = (uint)(0.0 < (double)CONCAT44(extraout_s1_00,uVar5)) *
                  (int)(longlong)(double)CONCAT44(extraout_s1_00,uVar5);
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(3,DAT_00572ae8,DAT_00572ae4,DAT_00572ae0,0x723,DAT_00572b98,
                   CONCAT44(extraout_s1,uVar2));
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0xc400000,DAT_00572b9c,DAT_00572b9c);
    }
    for (uVar3 = 0; uVar3 < 4; uVar3 = uVar3 + 1) {
      param_3[bVar4] = *(undefined1 *)((int)local_28 + uVar3);
      bVar4 = bVar4 + 1;
    }
    for (iVar1 = 0; iVar1 < 0x18; iVar1 = iVar1 + 1) {
      param_3[bVar4] = 0;
      bVar4 = bVar4 + 1;
    }
    dVar6 = (double)VectorSignedToFloat(*(undefined4 *)(DAT_00572c40 + 0x28),
                                        (byte)(in_fpscr >> 0x16) & 3);
    dVar6 = (dVar6 * (double)CONCAT44(extraout_s1,uVar2)) / DAT_0057238c;
    uVar2 = FUN_0058f970(SUB84(dVar6,0));
    local_28[0] = (uint)(0.0 < (double)CONCAT44(extraout_s1_01,uVar2)) *
                  (int)(longlong)(double)CONCAT44(extraout_s1_01,uVar2);
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(3,DAT_00572ae8,DAT_00572ae4,DAT_00572ae0,0x732,DAT_00572c44,dVar6);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0xc400000,DAT_00572c48,DAT_00572c48);
    }
    for (uVar3 = 0; uVar3 < 4; uVar3 = uVar3 + 1) {
      param_3[bVar4] = *(undefined1 *)((int)local_28 + uVar3);
      bVar4 = bVar4 + 1;
    }
    *param_4 = bVar4;
    uVar2 = 0;
  }
  return CONCAT44(param_4,uVar2);
}

