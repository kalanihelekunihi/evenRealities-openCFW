
undefined4 FUN_004f0998(int param_1,int param_2,undefined4 param_3)

{
  int *piVar1;
  undefined4 uVar2;
  undefined4 uVar3;
  int iVar4;
  undefined *puVar5;
  undefined4 uVar6;
  uint uVar7;
  undefined1 auStack_90 [12];
  uint local_84;
  uint local_80;
  uint local_7c;
  uint local_78;
  undefined4 local_74;
  undefined1 auStack_68 [12];
  uint local_5c;
  uint local_58;
  uint local_54;
  undefined1 auStack_40 [32];
  
  if ((param_1 != 0) && (param_2 != 0)) {
    uVar2 = FUN_0043de82();
    uVar3 = FUN_004515d2(100);
    FUN_0043f506(uVar2,uVar3);
    FUN_0043f568(uVar2,0x3fffffff);
    FUN_0043f0e0(uVar2,0);
    FUN_0043f142(uVar2,param_3);
    FUN_0044129e(uVar2,0,0);
    FUN_0044120e(uVar2,6,0);
    FUN_0044121c(uVar2,6,0);
    FUN_0044122a(uVar2,0xc,0);
    FUN_00441238(uVar2,0xc,0);
    FUN_0044146a(uVar2,6,0);
    FUN_0044131c(uVar2,2,0);
    uVar3 = FUN_0044104c(0xffffff);
    FUN_004412ec(uVar2,uVar3,0);
    FUN_0044130c(uVar2,0,0);
    FUN_0043dfa4(uVar2,0x10);
    uVar3 = FUN_00498668(uVar2);
    FUN_00498680(uVar3,DAT_004f0f08);
    FUN_0043f506(uVar3,0x18);
    FUN_0043f568(uVar3,0x18);
    FUN_0043f0e0(uVar3,0);
    FUN_0043f142(uVar3,2);
    FUN_0043ded4(uVar3,0x10000);
    FUN_0043dfa4(uVar3,0x10);
    FUN_0043c0e4(auStack_40,0x20,0);
    uVar3 = FUN_0047cc60(*(undefined4 *)(param_2 + 0x1c90),*(undefined4 *)(param_2 + 0x1c94),1000,0)
    ;
    service_time_epoch_to_calendar(uVar3,auStack_90);
    service_time_current_calendar_get(auStack_68);
    if (((local_84 < local_5c) || ((local_5c == local_84 && (local_80 < local_58)))) ||
       ((local_5c == local_84 && ((local_58 == local_80 && (local_7c < local_54)))))) {
      iVar4 = FUN_00466500();
      if ((iVar4 == 0) || (iVar4 = FUN_00466500(), iVar4 == 1)) {
        FUN_0044b728(auStack_40,0x20,DAT_004f1274,local_80,local_7c);
      }
      else {
        FUN_0044b728(auStack_40,0x20,DAT_004f1274,local_7c,local_80);
      }
    }
    else {
      iVar4 = FUN_0046650c();
      if (iVar4 == 1) {
        uVar7 = local_78 % 0xc;
        if (uVar7 == 0) {
          uVar7 = 0xc;
        }
        if (local_78 < 0xc) {
          puVar5 = &DAT_004f0e8c;
        }
        else {
          puVar5 = &LAB_004f0e90;
        }
        FUN_0044b728(auStack_40,0x20,DAT_004f1278,uVar7,local_74,puVar5);
      }
      else {
        FUN_0044b728(auStack_40,0x20,DAT_004f127c,local_78,local_74);
      }
    }
    uVar3 = FUN_00499416(uVar2);
    FUN_0043f506(uVar3,0x3fffffff);
    FUN_0043f568(uVar3,0x1c);
    FUN_0043f142(uVar3,0);
    FUN_0043f6b8(uVar3,3,0,0);
    FUN_0049942e(uVar3,auStack_40);
    uVar6 = FUN_0044104c(0xffffff);
    FUN_0044140e(uVar3,uVar6,0);
    piVar1 = DAT_004f0f18;
    FUN_0044143e(uVar3,*DAT_004f0f18,0);
    FUN_0043f66c(uVar3);
    iVar4 = FUN_0043fd9e(uVar3);
    uVar3 = FUN_00499416(uVar2);
    FUN_0043f506(uVar3,0x1fe - iVar4);
    FUN_0043f568(uVar3,0x1c);
    FUN_0043f0e0(uVar3,0x20);
    FUN_0043f142(uVar3,0);
    FUN_00499678(uVar3,1);
    FUN_0049942e(uVar3,param_2 + 1);
    uVar6 = FUN_0044104c(0xffffff);
    FUN_0044140e(uVar3,uVar6,0);
    FUN_0044143e(uVar3,*piVar1,0);
    uVar3 = FUN_00499416(uVar2);
    FUN_0043f506(uVar3,0x216);
    FUN_0043f0e0(uVar3,0);
    FUN_0043f142(uVar3,0x20);
    FUN_0049942e(uVar3,param_2 + 0x81);
    uVar6 = FUN_0044104c(0xffffff);
    FUN_0044140e(uVar3,uVar6,0);
    FUN_0044143e(uVar3,*piVar1,0);
    FUN_0044144c(uVar3,0x1c - *(int *)(*piVar1 + 0xc),0);
    FUN_0043f568(uVar3,0x3fffffff);
    FUN_00499678(uVar3,0);
    FUN_0043f66c(uVar2);
    return uVar2;
  }
  return 0;
}

