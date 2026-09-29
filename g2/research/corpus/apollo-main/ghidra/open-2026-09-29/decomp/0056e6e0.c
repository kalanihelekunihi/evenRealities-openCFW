
undefined8 smpProcPairing(int param_1,undefined1 *param_2,byte *param_3,undefined4 param_4)

{
  bool bVar1;
  undefined4 uVar2;
  byte bVar3;
  undefined4 uStack_10;
  undefined4 uStack_c;
  
  bVar1 = true;
  *param_3 = 0;
  *param_2 = 0;
  if ((*(char *)(param_1 + 0x22) == '\x01') && (*(char *)(param_1 + 0x29) == '\x01')) {
    *param_2 = 1;
    bVar1 = false;
  }
  else if (((((int)((uint)*(byte *)(param_1 + 0x23) << 0x1d) < 0) ||
            ((int)((uint)*(byte *)(param_1 + 0x2a) << 0x1d) < 0)) &&
           ((*(char *)(param_1 + 0x21) != '\x03' && (*(char *)(param_1 + 0x28) != '\x03')))) &&
          (((*(char *)(param_1 + 0x21) != '\0' && (*(char *)(param_1 + 0x21) != '\x01')) ||
           ((*(char *)(param_1 + 0x28) != '\0' && (*(char *)(param_1 + 0x28) != '\x01')))))) {
    bVar1 = false;
    if (((*(char *)(param_1 + 0x21) == '\0') || (*(char *)(param_1 + 0x21) == '\x01')) ||
       ((*(char *)(param_1 + 0x21) == '\x04' &&
        ((*(char *)(param_1 + 0x28) == '\x02' || (*(char *)(param_1 + 0x28) == '\x04')))))) {
      bVar3 = 1;
    }
    else {
      bVar3 = 0;
    }
    *param_3 = bVar3;
    if ((*(char *)(param_1 + 0x28) != '\x02') || (*(char *)(param_1 + 0x21) != '\x02')) {
      *param_3 = *(char *)(param_1 + 0x3a) == '\0' ^ *param_3;
    }
  }
  if (bVar1) {
    *(byte *)(param_1 + 0x40) = *(byte *)(param_1 + 0x23) & *(byte *)(param_1 + 0x2a) & 0xfb;
  }
  else {
    *(byte *)(param_1 + 0x40) = *(byte *)(param_1 + 0x23) & *(byte *)(param_1 + 0x2a) | 4;
  }
  if (*(char *)(param_1 + 0x3a) == '\0') {
    bVar3 = *(byte *)(param_1 + 0x2a);
  }
  else {
    bVar3 = *(byte *)(param_1 + 0x23);
  }
  uStack_c = param_4;
  if ((bVar1) && ((int)((uint)(bVar3 & *(byte *)(*DAT_0056f150 + 8)) << 0x1d) < 0)) {
    uStack_10._0_2_ = (ushort)*(byte *)(param_1 + 0x3d);
    uStack_10._0_3_ = CONCAT12(3,(ushort)uStack_10);
    uStack_10 = (byte *)CONCAT13(3,(undefined3)uStack_10);
    smpSmExecute(param_1,&uStack_10);
    uVar2 = 0;
  }
  else if ((*(byte *)(param_1 + 0x24) < *(byte *)(*DAT_0056f150 + 5)) ||
          (*(byte *)(param_1 + 0x2b) < *(byte *)(*DAT_0056f150 + 5))) {
    uStack_10._0_2_ = (ushort)*(byte *)(param_1 + 0x3d);
    uStack_10._0_3_ = CONCAT12(3,(ushort)uStack_10);
    uStack_10 = (byte *)CONCAT13(6,(undefined3)uStack_10);
    smpSmExecute(param_1,&uStack_10);
    uVar2 = 0;
  }
  else {
    uVar2 = 1;
    uStack_10 = param_3;
  }
  return CONCAT44(uStack_10,uVar2);
}

