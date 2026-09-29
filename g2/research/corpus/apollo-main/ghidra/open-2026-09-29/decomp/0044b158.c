
undefined8 FUN_0044b158(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  bool bVar1;
  uint *puVar2;
  uint *puVar3;
  uint *puVar4;
  uint *puVar5;
  uint *puVar6;
  byte bVar7;
  uint unaff_r5;
  undefined1 local_28;
  undefined1 uStack_27;
  undefined2 uStack_26;
  undefined4 local_24;
  undefined4 uStack_20;
  
  puVar3 = DAT_0044b570;
  local_28 = (undefined1)param_2;
  uStack_27 = (undefined1)((uint)param_2 >> 8);
  uStack_26 = (undefined2)((uint)param_2 >> 0x10);
  if ((*DAT_0044b578 << 0x1e < 0) || (*DAT_0044b570 >> 0x10 != 0x5af0)) {
    bVar1 = false;
  }
  else {
    bVar1 = true;
  }
  local_24 = param_3;
  if (bVar1) {
    if (((((int)(*DAT_0044b570 << 0x1f) < 0) || ((int)(*DAT_0044b570 << 0x1e) < 0)) ||
        ((int)(*DAT_0044b570 << 0x1d) < 0)) ||
       (((int)(*DAT_0044b570 << 0x1c) < 0 || ((int)(*DAT_0044b570 << 0x1b) < 0)))) {
      bVar7 = 1;
    }
    else {
      bVar7 = (byte)((*DAT_0044b570 << 0x1a) >> 0x1f);
    }
    if (bVar7 != 0) {
      if ((int)(*DAT_0044b570 << 0x1f) < 0) {
        bVar7 = 1;
      }
      else {
        bVar7 = (byte)((*DAT_0044b570 << 0x1e) >> 0x1f);
      }
      if (bVar7 != 0) {
        *DAT_0044b57c = *DAT_0044b57c | 1;
      }
      uStack_20 = param_4;
      if ((int)(*puVar3 << 0x1f) < 0) {
        *DAT_0044b580 = *DAT_0044b580 & 0xfffffff3 | 4;
        FUN_004807a0(1);
      }
      if ((int)(*puVar3 << 0x1d) < 0) {
        *DAT_0044b584 = *DAT_0044b584 | 0x20;
        local_28 = 1;
        uStack_27 = 0;
        uStack_26 = 0;
        FUN_00480826(200,DAT_0044b588,0x1000000,0x1000000);
        FUN_004807a0(5);
      }
      if ((int)(*puVar3 << 0x1c) < 0) {
        bVar7 = 1;
      }
      else {
        if ((int)(*puVar3 << 0x1a) < 0) {
          bVar7 = (byte)((*puVar3 << 0x19) >> 0x1f);
        }
        else {
          bVar7 = 1;
        }
        bVar7 = bVar7 ^ 1;
      }
      if (bVar7 != 0) {
        uStack_27 = 0;
        FUN_004809c4(2,&uStack_27);
        FUN_004807a0(0x5dc);
      }
      if ((int)(*puVar3 << 0x1b) < 0) {
        bVar7 = 1;
      }
      else {
        if ((int)(*puVar3 << 0x1a) < 0) {
          bVar7 = (byte)((*puVar3 << 0x19) >> 0x1f) ^ 1;
        }
        else {
          bVar7 = 1;
        }
        bVar7 = bVar7 ^ 1;
      }
      if (bVar7 != 0) {
        FUN_00480eee(0xf,&local_24);
        FUN_00480f0c(0xf,unaff_r5 & 0xfffffff0 | 10);
      }
      if ((int)(*puVar3 << 0x1a) < 0) {
        FUN_00480058();
        puVar2 = DAT_0044b51c;
        *DAT_0044b51c = *DAT_0044b51c & 0xfffffffd;
        *puVar2 = *puVar2 & 0xfffffffb;
        *puVar2 = *puVar2 & 0xffffffdf | ((*puVar3 & 0x7f) >> 6) << 5;
        *puVar2 = *puVar2 | 0x100;
        *puVar2 = *puVar2 | 0x20000000;
      }
      FUN_0047f5b8(0x1e);
      FUN_0047f5b8(0x1f);
      FUN_0047f5b8(0x20);
      FUN_0047f5b8(0x21);
      FUN_0047f5b8(0x1a);
      FUN_0047f5b8(0x1b);
      FUN_004807a0(5);
      puVar2 = DAT_0044b58c;
      *DAT_0044b58c = *DAT_0044b58c | 1;
      puVar4 = DAT_0044b590;
      *DAT_0044b590 = *DAT_0044b590 | 1;
      puVar5 = DAT_0044b594;
      *DAT_0044b594 = *DAT_0044b594 | 1;
      puVar6 = DAT_0044b598;
      *DAT_0044b598 = *DAT_0044b598 & 0xfffffffe;
      *DAT_0044b59c = *DAT_0044b59c & 0xf8ffffff;
      FUN_00475014(0,1);
      FUN_004807a0(1);
      if ((int)(*puVar3 << 0x1f) < 0) {
        *DAT_0044b580 = *DAT_0044b580 & 0xfffffff3 | 8;
      }
      FUN_004807a0(0x14);
      *puVar2 = *puVar2 | 1;
      *puVar4 = *puVar4 | 1;
      *puVar5 = *puVar5 | 1;
      *puVar6 = *puVar6 & 0xfffffffe;
      FUN_0047f7ae(0x1e);
      FUN_0047f7ae(0x1f);
      FUN_0047f7ae(0x20);
      FUN_0047f7ae(0x21);
      FUN_0047f7ae(0x1a);
      FUN_0047f7ae(0x1b);
      puVar2 = DAT_0044b51c;
      if ((int)(*puVar3 << 0x1a) < 0) {
        *DAT_0044b51c = *DAT_0044b51c & 0xdfffffff;
        *puVar2 = *puVar2 & 0xfffffeff;
        *puVar2 = *puVar2 & 0xffffffdf;
        *puVar2 = *puVar2 | 4;
        *puVar2 = *puVar2 | 2;
        FUN_0048009e();
      }
      if ((int)(*puVar3 << 0x1b) < 0) {
        bVar7 = 1;
      }
      else {
        if ((int)(*puVar3 << 0x1a) < 0) {
          bVar7 = (byte)((*puVar3 << 0x19) >> 0x1f) ^ 1;
        }
        else {
          bVar7 = 1;
        }
        bVar7 = bVar7 ^ 1;
      }
      if (bVar7 != 0) {
        FUN_00480f0c(0xf,local_24);
      }
      if ((int)(*puVar3 << 0x1c) < 0) {
        bVar7 = 1;
      }
      else {
        if ((int)(*puVar3 << 0x1a) < 0) {
          bVar7 = (byte)((*puVar3 << 0x19) >> 0x1f);
        }
        else {
          bVar7 = 1;
        }
        bVar7 = bVar7 ^ 1;
      }
      if (bVar7 != 0) {
        local_28 = 0;
        FUN_004809c4(4,&local_28);
      }
      if ((int)(*puVar3 << 0x1d) < 0) {
        *DAT_0044b584 = *DAT_0044b584 & 0xffffffdf;
      }
      if ((int)(*puVar3 << 0x1f) < 0) {
        bVar7 = 1;
      }
      else {
        bVar7 = (byte)((*puVar3 << 0x1e) >> 0x1f);
      }
      if (bVar7 != 0) {
        *DAT_0044b57c = *DAT_0044b57c & 0xfffffffe;
      }
    }
  }
  puVar3 = DAT_0044b570;
  *DAT_0044b570 = 0;
  *puVar3 = *puVar3 & 0xffff | 0x5af00000;
  return CONCAT44(local_24,CONCAT22(uStack_26,CONCAT11(uStack_27,local_28)));
}

