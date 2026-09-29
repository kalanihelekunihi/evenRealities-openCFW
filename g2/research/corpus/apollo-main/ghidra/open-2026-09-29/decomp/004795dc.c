
void FUN_004795dc(undefined1 *param_1)

{
  undefined4 uVar1;
  int iVar2;
  int iVar3;
  char cVar4;
  byte bVar5;
  byte bVar6;
  int local_e4;
  undefined1 auStack_dd [23];
  undefined1 auStack_c6 [16];
  byte local_b6;
  char local_b4;
  undefined1 auStack_b0 [28];
  undefined1 auStack_94 [120];
  
  iVar3 = DAT_0047a2dc;
  cVar4 = '\0';
  iVar2 = FUN_0043d0ce();
  if (iVar2 << 0x1e < 0) {
    FUN_0043d574(4,DAT_0047a2e4,DAT_0047a2e0,DAT_00479b44,0x13a,DAT_00479b40);
  }
  iVar2 = FUN_0043d0ce();
  if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
    compress_log_output(0x10000000,DAT_00479b48,DAT_00479b48);
  }
  FUN_00475014(0,1);
  bVar5 = 0;
  do {
    if (9 < bVar5) {
LAB_00479930:
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        FUN_0043d574(4,DAT_0047a2e4,DAT_0047a2e0,DAT_00479b44,0x18d,DAT_0047a46c,cVar4);
      }
      iVar3 = FUN_0043d0ce();
      if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
        compress_log_output(0x10400000,DAT_0047a62c,DAT_0047a62c,cVar4);
      }
      return;
    }
    FUN_00439be4(&local_e4,iVar3,200);
    uVar1 = DAT_00479b54;
    if ((local_e4 == -1) || (local_e4 == 0)) {
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        FUN_0043d574(4,DAT_0047a2e4,DAT_0047a2e0,DAT_00479b44,0x188,DAT_0047a464,bVar5);
      }
      iVar3 = FUN_0043d0ce();
      if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
        compress_log_output(0x10400000,DAT_0047a468,DAT_0047a468,bVar5);
      }
      goto LAB_00479930;
    }
    if (local_b4 == '\x01') {
      iVar2 = FUN_004751c8(auStack_b0,DAT_00479b54,0x10);
      bVar6 = iVar2 != 0;
      iVar2 = FUN_004751c8(auStack_94,uVar1,0x10);
      if (iVar2 != 0) {
        bVar6 = bVar6 | 2;
      }
      iVar2 = FUN_004751c8(auStack_dd,uVar1,0x10);
      if (iVar2 != 0) {
        bVar6 = bVar6 | 4;
      }
      iVar2 = FUN_004751c8(auStack_c6,uVar1,0x10);
      if (iVar2 != 0) {
        bVar6 = bVar6 | 8;
      }
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        FUN_0043d574(4,DAT_0047a2e4,DAT_0047a2e0,DAT_00479b44,0x15b,DAT_00479b58,local_b6,bVar6);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0x10800000,DAT_00479b5c,DAT_00479b5c,local_b6,bVar6);
      }
      if (local_b6 != bVar6) {
        local_b6 = bVar6;
        FUN_00479b74(&local_e4);
      }
    }
    if ((local_b4 == '\x01') && (local_b6 != 0)) {
      FUN_00439be4(param_1,&local_e4,200);
      param_1[0x2f] = 1;
      param_1[0x30] = 1;
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        FUN_0043d574(4,DAT_0047a2e4,DAT_0047a2e0,DAT_00479b44,0x16c,DAT_00479b60,bVar5,local_b6);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0x10800000,DAT_00479b64,DAT_00479b64,bVar5,local_b6);
      }
      if ((int)((uint)local_b6 << 0x1d) < 0) {
        FUN_0043dacc(DAT_00479b68,0x10,param_1 + 7,0x10);
      }
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        FUN_0043d574(4,DAT_0047a2e4,DAT_0047a2e0,DAT_00479b44,0x176,DAT_00479b6c,bVar5,local_b6,
                     local_b4,param_1[5],param_1[4],param_1[3],param_1[2],param_1[1],*param_1);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0x12400000,DAT_00479b70,DAT_00479b70,bVar5,local_b6,local_b4,param_1[5],
                            param_1[4],param_1[3],param_1[2],param_1[1],*param_1);
      }
      cVar4 = cVar4 + '\x01';
    }
    else {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        FUN_0043d574(4,DAT_0047a2e4,DAT_0047a2e0,DAT_00479b44,0x17e,DAT_00479b4c,bVar5,local_b4,
                     local_b6);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0x10c00000,DAT_00479b50,DAT_00479b50,bVar5,local_b4,local_b6);
      }
      FUN_0043c0e4(param_1,200,0);
      param_1[0x2f] = 0;
      param_1[0x30] = 0;
    }
    param_1 = param_1 + 200;
    iVar3 = iVar3 + 0x100;
    bVar5 = bVar5 + 1;
  } while( true );
}

