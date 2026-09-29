
void FUN_005ecef6(short param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  uint uVar3;
  undefined4 uVar4;
  uint uVar5;
  undefined1 auStack_60 [64];
  undefined4 uStack_20;
  
  iVar1 = DAT_005ed744;
  uStack_20 = param_4;
  iVar2 = td_active_session();
  uVar3 = FUN_005eca48();
  FUN_005eceb2();
  uVar4 = FUN_0043de82(*DAT_005ed9c8);
  *(undefined4 *)(iVar1 + 0x240) = uVar4;
  FUN_0043f4c0(*(undefined4 *)(iVar1 + 0x240),0x240,0x120);
  FUN_0043f09a(*(undefined4 *)(iVar1 + 0x240),0,0);
  FUN_0043dfa4(*(undefined4 *)(iVar1 + 0x240),0x10);
  uVar4 = FUN_0044104c(0);
  FUN_0044127e(*(undefined4 *)(iVar1 + 0x240),uVar4,0);
  FUN_0044129e(*(undefined4 *)(iVar1 + 0x240),0xff,0);
  FUN_0044131c(*(undefined4 *)(iVar1 + 0x240),0,0);
  FUN_005eca00(*(undefined4 *)(iVar1 + 0x240),0,0);
  FUN_0044146a(*(undefined4 *)(iVar1 + 0x240),0,0);
  uVar4 = FUN_0043de82(*(undefined4 *)(iVar1 + 0x240));
  *(undefined4 *)(iVar1 + 0x244) = uVar4;
  FUN_0043f4c0(*(undefined4 *)(iVar1 + 0x244),0x240,200);
  FUN_0043f09a(*(undefined4 *)(iVar1 + 0x244),0,0);
  FUN_0044129e(*(undefined4 *)(iVar1 + 0x244),0,0);
  FUN_0044131c(*(undefined4 *)(iVar1 + 0x244),0,0);
  FUN_005eca00(*(undefined4 *)(iVar1 + 0x244),0,0);
  FUN_0048ba78(*(undefined4 *)(iVar1 + 0x244),1);
  FUN_0048ba92(*(undefined4 *)(iVar1 + 0x244),0,0,0);
  FUN_00441246(*(undefined4 *)(iVar1 + 0x244),0,0);
  FUN_0043ded4(*(undefined4 *)(iVar1 + 0x244),0x10);
  FUN_0043dfa4(*(undefined4 *)(iVar1 + 0x244),0x60);
  FUN_0044e368(*(undefined4 *)(iVar1 + 0x244),0);
  uVar4 = FUN_005ecd06(*(undefined4 *)(iVar1 + 0x244),PTR_s_New_Session_005ed9cc,0,0);
  *(undefined4 *)(iVar1 + 0x248) = uVar4;
  for (uVar5 = 0; uVar5 < uVar3; uVar5 = uVar5 + 1) {
    FUN_005ecc74(auStack_60,0x40,uVar5 * 0x90 + iVar2 + 0x9c);
    uVar4 = FUN_005ecd06(*(undefined4 *)(iVar1 + 0x244),auStack_60,1,
                         *(undefined1 *)(iVar2 + uVar5 * 0x90 + 0x122));
    *(undefined4 *)(iVar1 + uVar5 * 4 + 0x24c) = uVar4;
  }
  if ((param_1 == -2) || ((param_1 != -1 && (iVar2 = FUN_005eca64((int)param_1), iVar2 == 0)))) {
    param_1 = FUN_005ecaac();
  }
  FUN_005ecb88((int)param_1);
  FUN_0044ea2e(*(undefined4 *)(iVar1 + param_1 * 4 + 0x24c),0);
  return;
}

