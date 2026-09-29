
undefined4
FUN_0059138a(byte *param_1,int param_2,undefined4 param_3,undefined4 param_4,int param_5,
            undefined4 param_6)

{
  byte bVar1;
  byte bVar2;
  undefined1 uVar3;
  uint uVar4;
  int iVar5;
  int iVar6;
  byte *pbVar7;
  int iVar8;
  byte *pbVar9;
  uint uVar10;
  byte *local_1e4;
  byte local_1e0;
  undefined1 local_1df;
  uint local_1c8;
  uint local_1c4;
  undefined1 local_1ac;
  byte local_1ab;
  undefined1 local_1a8 [8];
  undefined1 auStack_1a0 [28];
  undefined1 auStack_184 [80];
  byte abStack_134 [12];
  undefined1 auStack_128 [260];
  
  if (param_1 != (byte *)0x0) {
    uVar4 = (uint)param_1[1];
    if (uVar4 < 5) {
      iVar8 = 0x14;
    }
    else {
      iVar8 = *(int *)(DAT_005915b0 + (uint)*param_1 * 0x10 + uVar4 * 8 + -0x28);
    }
    if (iVar8 <= param_5) {
      if (uVar4 < 5) {
        iVar8 = 400;
      }
      else {
        iVar8 = *(int *)(DAT_005915b0 + (uint)*param_1 * 0x10 + uVar4 * 8 + -0x24);
      }
      if (param_5 <= iVar8) {
        (*(code *)(&PTR_FUN_00590f84_1_005915cc)[param_2])(param_1,param_3,param_4);
        local_1e0 = param_1[1];
        uVar4 = (uint)*param_1;
        bVar1 = param_1[2];
        uVar10 = (uint)bVar1;
        pbVar7 = param_1 + *(int *)(param_1 + 0x4a0) * 2 + 0x4ac;
        pbVar9 = param_1 + *(int *)(param_1 + 0x4a4) * 4 + 0x4ac;
        iVar5 = *(int *)(DAT_005915bc + (uint)bVar1 * 4);
        iVar8 = *(int *)(param_1 + 0x4a8);
        local_1df = FUN_00598284(uVar4,bVar1,param_5,param_1 + 4,pbVar7);
        iVar6 = iVar5 >> 1;
        local_1ab = FUN_00438fb8(uVar4,uVar10 & 0xff,param_1 + 0x10,pbVar7,local_1a8);
        FUN_00439710(pbVar7 + iVar6 * -2,pbVar7 + ((uVar4 + 1) * iVar5 - iVar6) * 2,iVar6 << 1);
        FUN_00598ab8(uVar4,uVar10 & 0xff,local_1e0,pbVar9,param_1 + iVar8 * 4 + 0x4ac,pbVar9);
        iVar8 = FUN_00598dec(uVar4,local_1e0,pbVar9,auStack_128);
        if (iVar8 != 0) {
          local_1a8[0] = 0;
        }
        local_1ac = FUN_00598f14(uVar4,local_1e0,auStack_128);
        local_1e4 = pbVar9;
        FUN_00599714(uVar4,local_1e0,param_5,auStack_128,local_1df,auStack_1a0,pbVar9);
        FUN_0059aa84(uVar4,local_1ac,iVar8,param_5,auStack_184,pbVar9);
        local_1e4 = abStack_134;
        FUN_0059bae4(uVar4,local_1e0,param_5,local_1ab,auStack_184,param_1 + 0x498,pbVar9);
        uVar3 = local_1ac;
        iVar8 = *(int *)(param_1 + 0x4a4);
        bVar1 = *param_1;
        bVar2 = param_1[1];
        FUN_00439868(&local_1e4,1,param_6,param_5);
        FUN_00599080(&local_1e4,bVar2,uVar3);
        FUN_0059c1c4(&local_1e4,bVar1,bVar2,abStack_134);
        FUN_0059b5c4(&local_1e4,auStack_184);
        if ((int)(local_1c4 + 1) < 0x21) {
          local_1c8 = (uint)local_1ab << (local_1c4 & 0xff) | local_1c8;
          local_1c4 = local_1c4 + 1;
        }
        else {
          FUN_00439b12(&local_1e4,(uint)local_1ab,1);
        }
        FUN_0059a910(&local_1e4,auStack_1a0);
        if (local_1ab != 0) {
          FUN_004396c2(&local_1e4,local_1a8);
        }
        FUN_0059c204(&local_1e4,bVar1,bVar2,uVar3,param_5,abStack_134,param_1 + iVar8 * 4 + 0x4ac);
        FUN_004399e4(&local_1e4);
        return 0;
      }
    }
  }
  return 0xffffffff;
}

