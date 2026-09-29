
undefined4 FUN_004ffef8(byte *param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  byte bVar1;
  char cVar2;
  int iVar3;
  undefined4 uVar4;
  uint uVar5;
  int iVar6;
  uint uVar7;
  undefined1 local_4c [2];
  undefined2 local_4a;
  undefined4 local_48;
  undefined2 local_44;
  undefined4 local_40 [10];
  undefined4 local_18;
  undefined4 local_14;
  byte local_10;
  undefined4 uStack_c;
  
  uStack_c = param_4;
  if (param_1 == (byte *)0x0) {
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      FUN_0043d574(1,DAT_00500300,DAT_005002fc,DAT_00500318,0x62,DAT_00500314);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_0050031c,DAT_0050031c);
    }
    uVar4 = 0xffffffff;
  }
  else {
    cVar2 = FUN_0045a570();
    if (cVar2 == '\x01') {
      FUN_0048949c(local_4c,0x40);
      bVar1 = *param_1;
      if (bVar1 == 1) {
        local_4c[0] = 1;
        local_4a = 2;
        local_48 = *(undefined4 *)(param_1 + 4);
        local_44 = CONCAT11(local_44._1_1_,param_1[8]);
      }
      else if (bVar1 != 0) {
        if (bVar1 == 3) {
          local_4c[0] = 3;
          local_4a = 4;
          local_48 = *(undefined4 *)(param_1 + 4);
        }
        else if (bVar1 < 3) {
          local_4c[0] = 2;
          local_4a = 3;
          local_48 = *(undefined4 *)(param_1 + 4);
        }
        else if (bVar1 == 5) {
          local_4c[0] = 5;
          local_4a = 6;
          local_48 = *(undefined4 *)(param_1 + 4);
          local_18 = *(undefined4 *)(param_1 + 0x30);
          local_14 = *(undefined4 *)(param_1 + 0x34);
          local_10 = param_1[0x38];
          if (*(uint *)(param_1 + 4) < 0xb) {
            uVar5 = *(uint *)(param_1 + 4);
          }
          else {
            uVar5 = 10;
          }
          local_44 = (undefined2)uVar5;
          for (uVar7 = 0; uVar7 < uVar5; uVar7 = uVar7 + 1) {
            local_40[uVar7] = *(undefined4 *)(param_1 + uVar7 * 4 + 8);
          }
        }
        else if (bVar1 < 5) {
          local_4c[0] = 4;
          local_4a = 5;
          local_48 = *(undefined4 *)(param_1 + 4);
        }
        else if (bVar1 == 6) {
          local_4c[0] = 6;
          local_4a = 7;
          local_48 = *(undefined4 *)(param_1 + 4);
        }
      }
      iVar3 = *DAT_00500320;
      *DAT_00500320 = iVar3 + 1;
      iVar3 = FUN_004ff7dc(iVar3,0,local_4c);
      if (iVar3 == 0) {
        iVar3 = FUN_0043d0ce();
        if (iVar3 << 0x1e < 0) {
          FUN_0043d574(4,DAT_00500300,DAT_005002fc,DAT_00500318,0xa5,DAT_0050032c);
        }
        iVar3 = FUN_0043d0ce();
        if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
          compress_log_output(0x10000000,DAT_00500330,DAT_00500330);
        }
        uVar4 = 0;
      }
      else {
        iVar6 = FUN_0043d0ce();
        if (iVar6 << 0x1e < 0) {
          FUN_0043d574(1,DAT_00500300,DAT_005002fc,DAT_00500318,0xa1,DAT_00500324,iVar3);
        }
        iVar6 = FUN_0043d0ce();
        if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
          compress_log_output(0x4400000,DAT_00500328,DAT_00500328,iVar3);
        }
        uVar4 = 0xffffffff;
      }
    }
    else {
      uVar4 = 0;
    }
  }
  return uVar4;
}

