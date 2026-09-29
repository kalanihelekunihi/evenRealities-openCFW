
undefined8 FUN_0041acb2(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

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
  
  puVar3 = DAT_0041b0c8;
  local_28 = (undefined1)param_2;
  uStack_27 = (undefined1)((uint)param_2 >> 8);
  uStack_26 = (undefined2)((uint)param_2 >> 0x10);
  if ((*DAT_0041b0cc << 0x1e < 0) || (*DAT_0041b0c8 >> 0x10 != 0x5af0)) {
    bVar1 = false;
  }
  else {
    bVar1 = true;
  }
  local_24 = param_3;
  if (bVar1) {
    if (((((int)(*DAT_0041b0c8 << 0x1f) < 0) || ((int)(*DAT_0041b0c8 << 0x1e) < 0)) ||
        ((int)(*DAT_0041b0c8 << 0x1d) < 0)) ||
       (((int)(*DAT_0041b0c8 << 0x1c) < 0 || ((int)(*DAT_0041b0c8 << 0x1b) < 0)))) {
      bVar7 = 1;
    }
    else {
      bVar7 = (byte)((*DAT_0041b0c8 << 0x1a) >> 0x1f);
    }
    if (bVar7 != 0) {
      if ((int)(*DAT_0041b0c8 << 0x1f) < 0) {
        bVar7 = 1;
      }
      else {
        bVar7 = (byte)((*DAT_0041b0c8 << 0x1e) >> 0x1f);
      }
      if (bVar7 != 0) {
        *DAT_0041b0d0 = *DAT_0041b0d0 | 1;
      }
      uStack_20 = param_4;
      if ((int)(*puVar3 << 0x1f) < 0) {
        *DAT_0041b0d4 = *DAT_0041b0d4 & 0xfffffff3 | 4;
        delay_us(1);
      }
      if ((int)(*puVar3 << 0x1d) < 0) {
        *DAT_0041b0d8 = *DAT_0041b0d8 | 0x20;
        local_28 = 1;
        uStack_27 = 0;
        uStack_26 = 0;
        delay_us_status_check(200,DAT_0041b0dc,0x1000000,0x1000000);
        delay_us(5);
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
        FUN_0041d3e4(2,&uStack_27);
        delay_us(0x5dc);
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
        FUN_0041d90e(0xf,&local_24);
        FUN_0041d92c(0xf,unaff_r5 & 0xfffffff0 | 10);
      }
      if ((int)(*puVar3 << 0x1a) < 0) {
        FUN_0041ca5c();
        puVar2 = DAT_0041b074;
        *DAT_0041b074 = *DAT_0041b074 & 0xfffffffd;
        *puVar2 = *puVar2 & 0xfffffffb;
        *puVar2 = *puVar2 & 0xffffffdf | ((*puVar3 & 0x7f) >> 6) << 5;
        *puVar2 = *puVar2 | 0x100;
        *puVar2 = *puVar2 | 0x20000000;
      }
      FUN_0041bf84(0x1e);
      FUN_0041bf84(0x1f);
      FUN_0041bf84(0x20);
      FUN_0041bf84(0x21);
      FUN_0041bf84(0x1a);
      FUN_0041bf84(0x1b);
      delay_us(5);
      puVar2 = DAT_0041b0e0;
      *DAT_0041b0e0 = *DAT_0041b0e0 | 1;
      puVar4 = DAT_0041b0e4;
      *DAT_0041b0e4 = *DAT_0041b0e4 | 1;
      puVar5 = DAT_0041b0e8;
      *DAT_0041b0e8 = *DAT_0041b0e8 | 1;
      puVar6 = DAT_0041b0ec;
      *DAT_0041b0ec = *DAT_0041b0ec & 0xfffffffe;
      *DAT_0041b0f0 = *DAT_0041b0f0 & 0xf8ffffff;
      FUN_0041e348(0,1);
      delay_us(1);
      if ((int)(*puVar3 << 0x1f) < 0) {
        *DAT_0041b0d4 = *DAT_0041b0d4 & 0xfffffff3 | 8;
      }
      delay_us(0x14);
      *puVar2 = *puVar2 | 1;
      *puVar4 = *puVar4 | 1;
      *puVar5 = *puVar5 | 1;
      *puVar6 = *puVar6 & 0xfffffffe;
      FUN_0041c17a(0x1e);
      FUN_0041c17a(0x1f);
      FUN_0041c17a(0x20);
      FUN_0041c17a(0x21);
      FUN_0041c17a(0x1a);
      FUN_0041c17a(0x1b);
      puVar2 = DAT_0041b074;
      if ((int)(*puVar3 << 0x1a) < 0) {
        *DAT_0041b074 = *DAT_0041b074 & 0xdfffffff;
        *puVar2 = *puVar2 & 0xfffffeff;
        *puVar2 = *puVar2 & 0xffffffdf;
        *puVar2 = *puVar2 | 4;
        *puVar2 = *puVar2 | 2;
        FUN_0041caa2();
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
        FUN_0041d92c(0xf,local_24);
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
        FUN_0041d3e4(4,&local_28);
      }
      if ((int)(*puVar3 << 0x1d) < 0) {
        *DAT_0041b0d8 = *DAT_0041b0d8 & 0xffffffdf;
      }
      if ((int)(*puVar3 << 0x1f) < 0) {
        bVar7 = 1;
      }
      else {
        bVar7 = (byte)((*puVar3 << 0x1e) >> 0x1f);
      }
      if (bVar7 != 0) {
        *DAT_0041b0d0 = *DAT_0041b0d0 & 0xfffffffe;
      }
    }
  }
  puVar3 = DAT_0041b0c8;
  *DAT_0041b0c8 = 0;
  *puVar3 = *puVar3 & 0xffff | 0x5af00000;
  return CONCAT44(local_24,CONCAT22(uStack_26,CONCAT11(uStack_27,local_28)));
}

