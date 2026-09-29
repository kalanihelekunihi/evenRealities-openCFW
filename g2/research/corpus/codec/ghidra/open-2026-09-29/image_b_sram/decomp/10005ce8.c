
undefined4 FUN_10005ce8(uint param_1,uint param_2,uint param_3,uint param_4,uint param_5)

{
  uint *puVar1;
  undefined4 uVar2;
  uint uVar3;
  
  puVar1 = DAT_10005e94;
  gx8002_platform_gate(3,1);
  FUN_100113c4(puVar1,0,0x1c);
  FUN_100051ec();
  uRam00000000 = uRam00000000 & 0x5fffffff | 0xa0000000;
  uRam0000010c = 0;
  if (param_2 == 0) {
    uVar2 = 0xffffffff;
  }
  else {
    puVar1[2] = param_2;
    if (param_3 != 0) {
      puVar1[4] = param_3;
    }
    if (param_1 != 0) {
      puVar1[3] = param_1;
    }
    if (param_4 != 0) {
      puVar1[5] = param_4;
    }
    if (param_5 != 0) {
      puVar1[6] = param_5;
    }
    (*(code *)(param_2 & 0xfffffffe))();
    gx8002_backup_request_irq(2,PTR_DAT_10005e98,0);
    if (param_1 != 0) {
      uVar3 = puVar1[1];
      if ((uVar3 & 1) != 0) {
        uRam00000100 = uRam00000100 & 0xfffffffe | 1;
      }
      if ((uVar3 & 2) != 0) {
        uRam00000100 = uRam00000100 & 0xfffffffd | 2;
      }
      if ((uVar3 & 4) != 0) {
        uRam00000100 = uRam00000100 & 0xfffffffb | 4;
      }
    }
    uVar3 = *puVar1;
    if ((uVar3 & 1) != 0) {
      uRam0000000c = uRam0000000c & 0xfffffdff | 0x200;
      uRam00000000 = uRam00000000 & 0xffffff7f;
    }
    if ((uVar3 & 2) != 0) {
      if ((uRam00000028 & 0xf) < 2) {
        uRam00000028 = uRam00000028 & 0xfffffdff | 0x200;
      }
      if ((uRam0000002c & 0xf) < 2) {
        uRam0000002c = uRam0000002c & 0xfffffdff | 0x200;
      }
      uRam00000000 = uRam00000000 & 0xffff7fff;
    }
    uVar2 = 0;
    if ((uVar3 & 4) != 0) {
      if ((uRam00000048 & 0xf) < 8) {
        uRam00000048 = uRam00000048 & 0xfffffdff | 0x200;
      }
      if ((uRam0000004c & 0xf) < 8) {
        uRam0000004c = uRam0000004c & 0xfffffdff | 0x200;
      }
      uVar2 = 0;
      uRam00000004 = uRam00000004 & 0x7fffffff;
    }
  }
  return uVar2;
}

