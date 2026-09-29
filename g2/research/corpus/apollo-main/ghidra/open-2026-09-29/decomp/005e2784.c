
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined8 smpScProcPairing(int param_1,char *param_2,byte *param_3,undefined4 param_4)

{
  bool bVar1;
  byte bVar2;
  undefined4 uVar3;
  int iVar4;
  undefined4 uStack_18;
  undefined4 uStack_14;
  
  bVar1 = true;
  *param_3 = 0;
  *param_2 = '\0';
  if (((int)((uint)*(byte *)(param_1 + 0x23) << 0x1c) < 0) &&
     ((int)((uint)*(byte *)(param_1 + 0x2a) << 0x1c) < 0)) {
    if ((*(char *)(param_1 + 0x22) == '\x01') || (*(char *)(param_1 + 0x29) == '\x01')) {
      *param_2 = '\x01';
      bVar1 = false;
    }
  }
  else if ((*(char *)(param_1 + 0x22) == '\x01') && (*(char *)(param_1 + 0x29) == '\x01')) {
    *param_2 = '\x01';
    bVar1 = false;
  }
  if (((*param_2 == '\0') &&
      (((((int)((uint)*(byte *)(param_1 + 0x23) << 0x1d) < 0 ||
         ((int)((uint)*(byte *)(param_1 + 0x2a) << 0x1d) < 0)) &&
        (*(char *)(param_1 + 0x21) != '\x03')) && (*(char *)(param_1 + 0x28) != '\x03')))) &&
     (((*(char *)(param_1 + 0x21) != '\0' && (*(char *)(param_1 + 0x21) != '\x01')) ||
      ((*(char *)(param_1 + 0x28) != '\0' && (*(char *)(param_1 + 0x28) != '\x01')))))) {
    bVar1 = false;
    if (((*(char *)(param_1 + 0x21) == '\0') || (*(char *)(param_1 + 0x21) == '\x01')) ||
       ((*(char *)(param_1 + 0x21) == '\x04' &&
        ((*(char *)(param_1 + 0x28) == '\x02' || (*(char *)(param_1 + 0x28) == '\x04')))))) {
      bVar2 = 1;
    }
    else {
      bVar2 = 0;
    }
    *param_3 = bVar2;
    if ((*(char *)(param_1 + 0x28) != '\x02') || (*(char *)(param_1 + 0x21) != '\x02')) {
      *param_3 = *(char *)(param_1 + 0x3a) == '\0' ^ *param_3;
    }
  }
  uStack_14 = param_4;
  if (((int)((uint)*(byte *)(param_1 + 0x23) << 0x1c) < 0) &&
     ((int)((uint)*(byte *)(param_1 + 0x2a) << 0x1c) < 0)) {
    if (*(char *)(DAT_005e30f0 + 0xf8) == '\0') {
      uStack_18._0_2_ = (ushort)*(byte *)(param_1 + 0x3d);
      uStack_18._0_3_ = CONCAT12(3,(ushort)uStack_18);
      uStack_18 = CONCAT13(3,(undefined3)uStack_18);
      smpSmExecute(param_1,&uStack_18);
      uVar3 = 0;
      goto LAB_005e2ab8;
    }
    **(undefined1 **)(param_1 + 0x48) = 1;
    *(undefined1 *)(*(int *)(param_1 + 0x48) + 1) = 1;
    *(byte *)(*(int *)(param_1 + 0x48) + 4) = *param_3;
    if (*param_2 == '\0') {
      if (bVar1) {
        if ((*(char *)(param_1 + 0x28) == '\x01') && (*(char *)(param_1 + 0x21) == '\x01')) {
          *(undefined1 *)(*(int *)(param_1 + 0x48) + 1) = 4;
          bVar1 = false;
        }
        else if ((*(char *)(param_1 + 0x28) == '\x03') || (*(char *)(param_1 + 0x21) == '\x03')) {
          bVar1 = false;
        }
      }
      else {
        *(undefined1 *)(*(int *)(param_1 + 0x48) + 1) = 3;
        if (((*(char *)(param_1 + 0x28) == '\x04') &&
            ((*(char *)(param_1 + 0x21) == '\x01' || (*(char *)(param_1 + 0x21) == '\x04')))) ||
           ((*(char *)(param_1 + 0x28) == '\x01' && (*(char *)(param_1 + 0x21) == '\x04')))) {
          *(undefined1 *)(*(int *)(param_1 + 0x48) + 1) = 4;
        }
        else if (((int)((uint)*(byte *)(param_1 + 0x23) << 0x1b) < 0) &&
                ((int)((uint)*(byte *)(param_1 + 0x2a) << 0x1b) < 0)) {
          *(undefined1 *)(*(int *)(param_1 + 0x48) + 2) = 1;
        }
      }
    }
    else {
      *(undefined1 *)(*(int *)(param_1 + 0x48) + 1) = 2;
    }
    uStack_18 = CONCAT22((short)((uint)param_3 >> 0x10),(ushort)*(byte *)(param_1 + 0x3d));
    iVar4 = SmpScAllocScratchBuffers(param_1);
    if (iVar4 == 0) {
      uStack_18._0_3_ = CONCAT12(3,(ushort)uStack_18);
      uStack_18 = CONCAT13(8,(undefined3)uStack_18);
    }
    else {
      uVar3 = DmSecGetEccKey();
      FUN_00439be4(*(undefined4 *)(*(int *)(param_1 + 0x48) + 0xc),uVar3,0x20);
      iVar4 = DmSecGetEccKey();
      FUN_00439be4(*(int *)(*(int *)(param_1 + 0x48) + 0xc) + 0x20,iVar4 + 0x20,0x20);
      iVar4 = DmSecGetEccKey();
      FUN_00439be4(*(undefined4 *)(*(int *)(param_1 + 0x48) + 0x10),iVar4 + 0x40,0x20);
      uStack_18._0_3_ = CONCAT12(0x11,(ushort)uStack_18);
    }
    smpSmExecute(param_1,&uStack_18);
  }
  else {
    if ((int)((uint)*(byte *)(*_DAT_005e30f4 + 8) << 0x1c) < 0) {
      uStack_18._0_2_ = (ushort)*(byte *)(param_1 + 0x3d);
      uStack_18._0_3_ = CONCAT12(3,(ushort)uStack_18);
      uStack_18 = CONCAT13(3,(undefined3)uStack_18);
      smpSmExecute(param_1,&uStack_18);
      uVar3 = 0;
      goto LAB_005e2ab8;
    }
    **(undefined1 **)(param_1 + 0x48) = 0;
    uStack_18._3_1_ = (undefined1)((uint)param_3 >> 0x18);
    uStack_18._0_3_ = CONCAT12(0x12,(ushort)*(byte *)(param_1 + 0x3d));
    smpSmExecute(param_1,&uStack_18);
  }
  if (bVar1) {
    *(byte *)(param_1 + 0x40) = *(byte *)(param_1 + 0x23) & *(byte *)(param_1 + 0x2a) & 0xfb;
  }
  else {
    *(byte *)(param_1 + 0x40) = *(byte *)(param_1 + 0x23) & *(byte *)(param_1 + 0x2a) | 4;
  }
  if (*(char *)(param_1 + 0x3a) == '\0') {
    bVar2 = *(byte *)(param_1 + 0x2a);
  }
  else {
    bVar2 = *(byte *)(param_1 + 0x23);
  }
  if ((bVar1) && ((int)((uint)(bVar2 & *(byte *)(*_DAT_005e30f4 + 8)) << 0x1d) < 0)) {
    uStack_18._0_2_ = (ushort)*(byte *)(param_1 + 0x3d);
    uStack_18._0_3_ = CONCAT12(3,(ushort)uStack_18);
    uStack_18 = CONCAT13(3,(undefined3)uStack_18);
    smpSmExecute(param_1,&uStack_18);
    uVar3 = 0;
  }
  else if ((*(byte *)(param_1 + 0x24) < *(byte *)(*_DAT_005e30f4 + 5)) ||
          (*(byte *)(param_1 + 0x2b) < *(byte *)(*_DAT_005e30f4 + 5))) {
    uStack_18._0_2_ = (ushort)*(byte *)(param_1 + 0x3d);
    uStack_18._0_3_ = CONCAT12(3,(ushort)uStack_18);
    uStack_18 = CONCAT13(6,(undefined3)uStack_18);
    smpSmExecute(param_1,&uStack_18);
    uVar3 = 0;
  }
  else {
    uVar3 = 1;
  }
LAB_005e2ab8:
  return CONCAT44(uStack_18,uVar3);
}

