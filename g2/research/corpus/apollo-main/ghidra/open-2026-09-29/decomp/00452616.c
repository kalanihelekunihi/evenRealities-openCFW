
undefined8 FUN_00452616(undefined4 param_1,int param_2,undefined4 *param_3,undefined4 param_4)

{
  byte bVar1;
  undefined1 uVar2;
  byte bVar3;
  undefined4 uVar4;
  int iVar5;
  uint uVar6;
  undefined1 local_20;
  undefined1 uStack_1f;
  undefined1 uStack_1e;
  undefined1 uStack_1d;
  undefined4 uStack_1c;
  
  local_20 = SUB41(param_3,0);
  uStack_1f = (undefined1)((uint)param_3 >> 8);
  uStack_1e = (undefined1)((uint)param_3 >> 0x10);
  uStack_1d = (undefined1)((uint)param_3 >> 0x18);
  *param_3 = param_1;
  param_3[1] = param_2;
  uStack_1c = param_4;
  bVar1 = FUN_00452df0(param_1,param_2,param_3);
  if ((param_2 == 0) || (2 < bVar1)) {
    uVar4 = FUN_004525f4(param_1,param_2);
    param_3[7] = uVar4;
    if (*(char *)(param_3 + 8) != '\0') {
      uVar2 = FUN_00452308(param_1,param_2);
      *(undefined1 *)(param_3 + 8) = uVar2;
      if (2 < *(byte *)(param_3 + 8)) {
        uVar4 = FUN_004522e8(param_1,param_2);
        uVar4 = FUN_00452e22(param_1,param_2,param_3,uVar4);
        local_20 = (undefined1)uVar4;
        uStack_1f = (undefined1)((uint)uVar4 >> 8);
        uStack_1e = (undefined1)((uint)uVar4 >> 0x10);
        uStack_1d = (undefined1)((uint)uVar4 >> 0x18);
        FUN_00439be4((int)param_3 + 0x21,&local_20,3);
        iVar5 = FUN_0045236c(param_1,param_2);
        if ((iVar5 == 0) || ((*(byte *)(iVar5 + 0xb) & 0xf) == 0)) {
          bVar3 = FUN_00452334(param_1,param_2);
          *(byte *)((int)param_3 + 0x2f) = *(byte *)((int)param_3 + 0x2f) & 0xf0 | bVar3 & 0xf;
          if ((*(byte *)((int)param_3 + 0x2f) & 0xf) != 0) {
            FUN_00439be4(param_3 + 9,(int)param_3 + 0x21,3);
            uVar4 = FUN_00452314(param_1,param_2);
            uVar4 = FUN_00452e22(param_1,param_2,param_3,uVar4);
            local_20 = (undefined1)uVar4;
            uStack_1f = (undefined1)((uint)uVar4 >> 8);
            uStack_1e = (undefined1)((uint)uVar4 >> 0x10);
            uStack_1d = (undefined1)((uint)uVar4 >> 0x18);
            FUN_00439be4((int)param_3 + 0x29,&local_20,3);
            uVar2 = FUN_00452340(param_1,param_2);
            *(undefined1 *)(param_3 + 10) = uVar2;
            uVar2 = FUN_0045234a(param_1,param_2);
            *(undefined1 *)((int)param_3 + 0x2d) = uVar2;
            uVar2 = FUN_00452354(param_1,param_2);
            *(undefined1 *)((int)param_3 + 0x27) = uVar2;
            uVar2 = FUN_00452360(param_1,param_2);
            *(undefined1 *)(param_3 + 0xb) = uVar2;
          }
        }
        else {
          FUN_00454738(param_3 + 9,iVar5,0xc);
        }
      }
    }
    if (*(char *)(param_3 + 0x12) != '\0') {
      uVar4 = FUN_004523fa(param_1,param_2);
      param_3[0x11] = uVar4;
      if (param_3[0x11] != 0) {
        uVar2 = FUN_004523ee(param_1,param_2);
        *(undefined1 *)(param_3 + 0x12) = uVar2;
        if (2 < *(byte *)(param_3 + 0x12)) {
          bVar3 = FUN_00452404(param_1,param_2);
          *(byte *)((int)param_3 + 0x49) = *(byte *)((int)param_3 + 0x49) & 0xe0 | bVar3 & 0x1f;
          uVar4 = FUN_004523ce(param_1,param_2);
          uVar4 = FUN_00452e22(param_1,param_2,param_3,uVar4);
          local_20 = (undefined1)uVar4;
          uStack_1f = (undefined1)((uint)uVar4 >> 8);
          uStack_1e = (undefined1)((uint)uVar4 >> 0x10);
          uStack_1d = (undefined1)((uint)uVar4 >> 0x18);
          FUN_00439be4((int)param_3 + 0x3e,&local_20,3);
        }
      }
    }
    if (*(char *)(param_3 + 0x16) != '\0') {
      uVar4 = FUN_00452410(param_1,param_2);
      param_3[0x14] = uVar4;
      if (param_3[0x14] != 0) {
        uVar2 = FUN_0045243a(param_1,param_2);
        *(undefined1 *)(param_3 + 0x16) = uVar2;
        if (2 < *(byte *)(param_3 + 0x16)) {
          uVar4 = FUN_00452446(param_1,param_2);
          param_3[0x15] = uVar4;
          uVar4 = FUN_0045241a(param_1,param_2);
          uVar4 = FUN_00452e22(param_1,param_2,param_3,uVar4);
          local_20 = (undefined1)uVar4;
          uStack_1f = (undefined1)((uint)uVar4 >> 8);
          uStack_1e = (undefined1)((uint)uVar4 >> 0x10);
          uStack_1d = (undefined1)((uint)uVar4 >> 0x18);
          FUN_00439be4((int)param_3 + 0x4a,&local_20,3);
        }
      }
    }
    if (*(char *)((int)param_3 + 0x3b) != '\0') {
      uVar4 = FUN_00452376(param_1,param_2);
      param_3[0xc] = uVar4;
      if (param_3[0xc] != 0) {
        uVar2 = FUN_00452380(param_1,param_2);
        *(undefined1 *)((int)param_3 + 0x3b) = uVar2;
        if (2 < *(byte *)((int)param_3 + 0x3b)) {
          iVar5 = FUN_00488cb8(param_3[0xc]);
          if (iVar5 == 2) {
            uVar4 = FUN_004525be(param_1,param_2);
            param_3[0xd] = uVar4;
            uVar4 = FUN_00452592(param_1,param_2);
            uVar4 = FUN_00452e22(param_1,param_2,param_3,uVar4);
            local_20 = (undefined1)uVar4;
            uStack_1f = (undefined1)((uint)uVar4 >> 8);
            uStack_1e = (undefined1)((uint)uVar4 >> 0x10);
            uStack_1d = (undefined1)((uint)uVar4 >> 0x18);
            FUN_00439be4(param_3 + 0xe,&local_20,3);
          }
          else {
            uVar4 = FUN_0045238c(param_1,param_2);
            local_20 = FUN_004523ac(param_1,param_2);
            uStack_1f = 0;
            uStack_1e = 0;
            uStack_1d = 0;
            uVar6 = FUN_00452e68(param_1,param_2,param_3,uVar4);
            local_20 = (undefined1)uVar6;
            uStack_1f = (undefined1)(uVar6 >> 8);
            uStack_1e = (undefined1)(uVar6 >> 0x10);
            uStack_1d = (undefined1)(uVar6 >> 0x18);
            *(undefined1 *)(param_3 + 0xf) = uStack_1d;
            uVar4 = FUN_00441068(uStack_1e,uStack_1f,uVar6 & 0xff);
            local_20 = (undefined1)uVar4;
            uStack_1f = (undefined1)((uint)uVar4 >> 8);
            uStack_1e = (undefined1)((uint)uVar4 >> 0x10);
            uStack_1d = (undefined1)((uint)uVar4 >> 0x18);
            FUN_00439be4(param_3 + 0xe,&local_20,3);
            uVar2 = FUN_004523b8(param_1,param_2);
            *(undefined1 *)((int)param_3 + 0x3d) = uVar2;
          }
        }
      }
    }
    if (*(char *)(param_3 + 0x1b) != '\0') {
      uVar4 = FUN_00452450(param_1,param_2);
      param_3[0x17] = uVar4;
      if ((param_3[0x17] != 0) && (2 < *(byte *)(param_3 + 0x1b))) {
        uVar2 = FUN_00452498(param_1,param_2);
        *(undefined1 *)(param_3 + 0x1b) = uVar2;
        if (2 < *(byte *)(param_3 + 0x1b)) {
          uVar4 = FUN_0045245a(param_1,param_2);
          param_3[0x18] = uVar4;
          uVar4 = FUN_00452464(param_1,param_2);
          param_3[0x19] = uVar4;
          uVar4 = FUN_0045246e(param_1,param_2);
          param_3[0x1a] = uVar4;
          uVar4 = FUN_00452478(param_1,param_2);
          uVar4 = FUN_00452e22(param_1,param_2,param_3,uVar4);
          local_20 = (undefined1)uVar4;
          uStack_1f = (undefined1)((uint)uVar4 >> 8);
          uStack_1e = (undefined1)((uint)uVar4 >> 0x10);
          uStack_1d = (undefined1)((uint)uVar4 >> 0x18);
          FUN_00439be4((int)param_3 + 0x59,&local_20,3);
        }
      }
    }
    if (bVar1 < 0xfd) {
      *(char *)(param_3 + 8) = (char)((uint)bVar1 * (uint)*(byte *)(param_3 + 8) >> 8);
      *(char *)((int)param_3 + 0x3b) =
           (char)((uint)bVar1 * (uint)*(byte *)((int)param_3 + 0x3b) >> 8);
      *(char *)(param_3 + 0x12) = (char)((uint)bVar1 * (uint)*(byte *)(param_3 + 0x12) >> 8);
      *(char *)(param_3 + 0x1b) = (char)((uint)bVar1 * (uint)*(byte *)(param_3 + 0x1b) >> 8);
      *(char *)(param_3 + 0x16) = (char)((uint)bVar1 * (uint)*(byte *)(param_3 + 0x16) >> 8);
    }
  }
  else {
    *(undefined1 *)(param_3 + 8) = 0;
    *(undefined1 *)((int)param_3 + 0x3b) = 0;
    *(undefined1 *)(param_3 + 0x12) = 0;
    *(undefined1 *)(param_3 + 0x16) = 0;
    *(undefined1 *)(param_3 + 0x1b) = 0;
  }
  return CONCAT44(uStack_1c,CONCAT13(uStack_1d,CONCAT12(uStack_1e,CONCAT11(uStack_1f,local_20))));
}

