
int FUN_0055eb3e(undefined4 *param_1,undefined4 param_2,undefined4 param_3,uint param_4)

{
  bool bVar1;
  byte bVar2;
  undefined4 uVar3;
  int iVar4;
  int iVar5;
  uint uVar6;
  undefined1 auStack_38 [2];
  undefined1 auStack_36 [2];
  undefined1 auStack_34 [8];
  undefined1 auStack_2c [8];
  uint uStack_24;
  
  param_1[1] = param_2;
  bVar1 = false;
  uStack_24 = param_4;
  while (!bVar1) {
    param_1[2] = param_1;
    if ((param_4 & 0xff) == 0) {
      *(undefined1 *)(param_1 + 3) = 0;
      param_1[4] = 0xd34;
    }
    else {
      uVar3 = FUN_0055f4f2(param_1,0);
      iVar4 = FUN_0055f54e(uVar3,auStack_36);
      iVar5 = DAT_0055ee50;
      if (iVar4 != DAT_0055ee50) {
        return iVar4;
      }
      iVar4 = FUN_0055f5fe(uVar3,auStack_2c);
      if (iVar4 != iVar5) {
        return iVar4;
      }
    }
    bVar1 = true;
  }
  for (bVar2 = 0; bVar2 < 2; bVar2 = bVar2 + 1) {
    param_1[(uint)bVar2 * 2 + 5] = param_2;
    *(byte *)(param_1 + (uint)bVar2 * 2 + 6) = bVar2;
  }
  bVar1 = false;
  do {
    if (bVar1) {
      bVar1 = false;
      while (!bVar1) {
        param_1[9] = param_1;
        bVar1 = true;
      }
      for (bVar2 = 0; bVar2 < 5; bVar2 = bVar2 + 1) {
        param_1[(uint)bVar2 * 2 + 10] = param_2;
        *(byte *)(param_1 + (uint)bVar2 * 2 + 0xb) = bVar2;
      }
      for (bVar2 = 0; bVar2 < 2; bVar2 = bVar2 + 1) {
        param_1[(uint)bVar2 * 2 + 0x14] = param_2;
        *(byte *)(param_1 + (uint)bVar2 * 2 + 0x15) = bVar2;
      }
      for (bVar2 = 0; bVar2 < 3; bVar2 = bVar2 + 1) {
        param_1[(uint)bVar2 * 2 + 0x18] = param_2;
        *(byte *)(param_1 + (uint)bVar2 * 2 + 0x19) = bVar2;
      }
      bVar1 = false;
      while (!bVar1) {
        param_1[0x1e] = param_2;
        bVar1 = true;
      }
      bVar1 = false;
      do {
        if (bVar1) {
          bVar1 = false;
          while (!bVar1) {
            param_1[0x21] = param_2;
            bVar1 = true;
          }
          bVar1 = false;
          while (!bVar1) {
            param_1[0x22] = param_2;
            bVar1 = true;
          }
          *(undefined1 *)(param_1 + 0x33) = 0;
          param_1[0x25] = param_3;
          for (uVar6 = 0; uVar6 < 0xb; uVar6 = uVar6 + 1) {
            param_1[uVar6 + 0x26] = param_3;
          }
          *param_1 = 0;
          *(char *)((int)param_1 + 0xcd) = (char)param_4;
          return DAT_0055ee50;
        }
        param_1[0x1f] = param_2;
        if ((param_4 & 0xff) == 0) {
          *(undefined1 *)(param_1 + 0x20) = 0;
        }
        else {
          uVar3 = FUN_0055fc60(param_1,0);
          iVar5 = FUN_0055fc74(uVar3,auStack_34);
          if (iVar5 != DAT_0055ee50) {
            return iVar5;
          }
        }
        bVar1 = true;
      } while( true );
    }
    param_1[0x23] = param_1;
    if ((param_4 & 0xff) == 0) {
      *(undefined2 *)(param_1 + 0x24) = 0x20;
      *(undefined2 *)((int)param_1 + 0x92) = 0x53c;
    }
    else {
      uVar3 = FUN_0055eff0(param_1,0);
      iVar4 = FUN_0055f180(uVar3,auStack_38);
      iVar5 = DAT_0055ee50;
      if (iVar4 != DAT_0055ee50) {
        return iVar4;
      }
      iVar4 = FUN_0055f218(uVar3,auStack_38);
      if (iVar4 != iVar5) {
        return iVar4;
      }
    }
    bVar1 = true;
  } while( true );
}

