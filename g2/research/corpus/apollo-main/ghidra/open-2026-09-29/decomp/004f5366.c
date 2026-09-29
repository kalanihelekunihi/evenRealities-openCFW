
undefined4 FUN_004f5366(int param_1,int param_2,char param_3,undefined1 *param_4,int param_5)

{
  byte bVar1;
  undefined4 uVar2;
  uint uVar3;
  undefined4 uVar4;
  undefined *puVar5;
  int iVar6;
  undefined1 auStack_a8 [12];
  int local_9c;
  undefined4 local_98;
  undefined4 local_94;
  uint local_90;
  undefined4 local_8c;
  char local_80 [32];
  char local_60 [32];
  undefined1 auStack_40 [40];
  
  if ((param_2 < 0) ||
     ((((param_2 < 1 && (param_1 == 0)) || (param_4 == (undefined1 *)0x0)) || (param_5 < 1)))) {
    uVar2 = 0;
  }
  else {
    iVar6 = (short)*(char *)(*DAT_004f5e80 + 8) * 900;
    service_time_current_calendar_get(auStack_40,param_2,iVar6,iVar6 >> 0x1f);
    service_time_epoch_to_calendar(param_1 + iVar6,auStack_a8);
    FUN_0043c0e4(local_80,0x20,0);
    FUN_0043c0e4(local_60,0x20,0);
    if ((param_3 == '\0') || (param_3 == '\x01')) {
      bVar1 = FUN_004f51aa(auStack_40,auStack_a8);
      uVar4 = DAT_004f5fb4;
      uVar2 = DAT_004f5fb0;
      uVar3 = (uint)bVar1;
      if (uVar3 == 0) {
        uVar4 = FUN_00460084(DAT_004f5fb0);
        uVar2 = FUN_0045fffe(uVar2,uVar4);
        FUN_0044b728(local_80,0x20,uVar2);
      }
      else if (uVar3 == 1) {
        uVar2 = FUN_00460084(DAT_004f5fb4);
        uVar2 = FUN_0045fffe(uVar4,uVar2);
        FUN_0044b728(local_80,0x20,uVar2);
      }
      else if (uVar3 - 2 < 4) {
        iVar6 = FUN_00466500();
        if ((iVar6 == 0) || (iVar6 = FUN_00466500(), iVar6 == 1)) {
          FUN_0044b728(local_80,0x20,DAT_004f5fb8,local_98,local_94);
        }
        else {
          FUN_0044b728(local_80,0x20,DAT_004f5fb8,local_94,local_98);
        }
      }
      else {
        iVar6 = FUN_00466500();
        if (iVar6 == 0) {
          FUN_0044b728(local_80,0x20,DAT_004f5fbc,local_9c + 2000,local_98,local_94);
        }
        else {
          iVar6 = FUN_00466500();
          if (iVar6 == 1) {
            FUN_0044b728(local_80,0x20,DAT_004f5fc0,local_98,local_94,local_9c + 2000);
          }
          else {
            FUN_0044b728(local_80,0x20,DAT_004f5fc0,local_94,local_98,local_9c + 2000);
          }
        }
      }
    }
    else {
      local_80[0] = '\0';
    }
    if ((param_3 == '\0') || (param_3 == '\x02')) {
      iVar6 = FUN_0046650c();
      if (iVar6 == 1) {
        uVar3 = local_90 % 0xc;
        if (uVar3 == 0) {
          uVar3 = 0xc;
        }
        if (local_90 < 0xc) {
          puVar5 = &DAT_004f5710;
        }
        else {
          puVar5 = &LAB_004f5714;
        }
        FUN_0044b728(local_60,0x20,DAT_004f5fc4,uVar3,local_8c,puVar5);
      }
      else {
        FUN_0044b728(local_60,0x20,DAT_004f5fc8,local_90,local_8c);
      }
    }
    else {
      local_60[0] = '\0';
    }
    if ((local_80[0] == '\0') || (local_60[0] == '\0')) {
      if (local_80[0] == '\0') {
        if (local_60[0] == '\0') {
          *param_4 = 0;
        }
        else {
          FUN_0044b728(param_4,param_5,&LAB_004f5834,local_60);
        }
      }
      else {
        FUN_0044b728(param_4,param_5,&LAB_004f5834,local_80);
      }
    }
    else {
      FUN_0044b728(param_4,param_5,DAT_004f5fcc,local_80,local_60);
    }
    uVar2 = 1;
  }
  return uVar2;
}

