
void FUN_0054fb84(undefined4 param_1,undefined4 param_2,undefined4 param_3)

{
  undefined4 uVar1;
  undefined4 uVar2;
  undefined4 uVar3;
  int iVar4;
  undefined4 uVar5;
  undefined4 uVar6;
  undefined4 uVar7;
  undefined *puVar8;
  uint uVar9;
  int local_5c;
  int local_58;
  int local_54;
  int local_50;
  int local_4c;
  undefined4 local_48;
  undefined1 auStack_44 [4];
  undefined1 auStack_40 [12];
  int local_34;
  int local_30;
  int local_2c;
  
  iVar4 = FUN_0054fb46(param_1,&local_54);
  if (iVar4 == 0) {
    iVar4 = FUN_0054fa56(param_1,&local_4c,&local_58,&local_5c,&local_50,&local_48,auStack_44);
    if (iVar4 == 0) {
      service_time_current_calendar_get(auStack_40);
      uVar3 = DAT_00550814;
      uVar2 = DAT_0055080c;
      uVar1 = DAT_00550700;
      uVar7 = DAT_005506f8;
      uVar5 = DAT_0055068c;
      uVar6 = DAT_005505cc;
      local_34 = local_34 + 2000;
      if (local_54 < 0) {
        if (local_54 < -0x3b) {
          if (local_54 < DAT_00550688) {
            if (((local_4c == local_34) && (local_58 == local_30)) && (local_5c == local_2c)) {
              iVar4 = FUN_0046650c();
              if (iVar4 == 1) {
                iVar4 = local_50 % 0xc;
                if (iVar4 == 0) {
                  iVar4 = 0xc;
                }
                if (local_50 < 0xc) {
                  puVar8 = &DAT_0054ff5c;
                }
                else {
                  puVar8 = &DAT_0054ff60;
                }
                FUN_0044b728(param_2,param_3,DAT_005506f0,iVar4,local_48,puVar8);
              }
              else {
                FUN_0044b728(param_2,param_3,DAT_005506f4,local_50,local_48);
              }
            }
            else {
              if (((local_4c == local_34) && (local_58 == local_30)) && (local_5c == local_2c + 1))
              {
                uVar6 = FUN_00460084(DAT_005506f8);
                uVar6 = FUN_0045fffe(uVar7,uVar6);
                FUN_0044b728(param_2,param_3,uVar6);
                return;
              }
              iVar4 = FUN_00466500();
              if ((iVar4 == 0) || (iVar4 = FUN_00466500(), iVar4 == 1)) {
                FUN_0044b728(param_2,param_3,DAT_005506fc,local_58,local_5c);
              }
              else {
                FUN_0044b728(param_2,param_3,DAT_005506fc,local_5c,local_58);
              }
            }
          }
          else {
            uVar6 = FUN_00460084(DAT_0055068c);
            uVar5 = FUN_0045fffe(uVar5,uVar6);
            uVar6 = DAT_00550690;
            uVar7 = FUN_00460084(DAT_00550690);
            uVar6 = FUN_0045fffe(uVar6,uVar7);
            FUN_0044b728(param_2,param_3,DAT_005506ec,uVar6,local_54 / -0x3c,uVar5);
          }
        }
        else {
          uVar5 = FUN_00460084(DAT_005505cc);
          uVar6 = FUN_0045fffe(uVar6,uVar5);
          FUN_0044b728(param_2,param_3,uVar6);
        }
      }
      else if (local_54 < 0x3c) {
        uVar5 = FUN_00460084(DAT_005505cc);
        uVar6 = FUN_0045fffe(uVar6,uVar5);
        FUN_0044b728(param_2,param_3,uVar6);
      }
      else if (local_54 < 0xe10) {
        uVar6 = FUN_00460084(DAT_00550700);
        uVar5 = FUN_0045fffe(uVar1,uVar6);
        uVar6 = DAT_00550704;
        uVar7 = FUN_00460084(DAT_00550704);
        uVar6 = FUN_0045fffe(uVar6,uVar7);
        FUN_0044b728(param_2,param_3,DAT_005506ec,uVar6,local_54 / 0x3c,uVar5);
      }
      else if (local_54 < 0x2a30) {
        uVar6 = FUN_00460084(DAT_0055080c);
        uVar5 = FUN_0045fffe(uVar2,uVar6);
        uVar6 = DAT_00550810;
        uVar7 = FUN_00460084(DAT_00550810);
        uVar6 = FUN_0045fffe(uVar6,uVar7);
        FUN_0044b728(param_2,param_3,DAT_005506ec,uVar6,local_54 / 0xe10,uVar5);
      }
      else if (((local_4c == local_34) && (local_58 == local_30)) && (local_5c == local_2c)) {
        iVar4 = FUN_0046650c();
        if (iVar4 == 1) {
          iVar4 = local_50 % 0xc;
          if (iVar4 == 0) {
            iVar4 = 0xc;
          }
          if (local_50 < 0xc) {
            puVar8 = &DAT_0054ff5c;
          }
          else {
            puVar8 = &DAT_0054ff60;
          }
          FUN_0044b728(param_2,param_3,DAT_005506f0,iVar4,local_48,puVar8);
        }
        else {
          FUN_0044b728(param_2,param_3,DAT_005506f4,local_50,local_48);
        }
      }
      else if (((local_4c == local_34) && (local_58 == local_30)) && (local_5c == local_2c + -1)) {
        uVar6 = FUN_00460084(DAT_00550814);
        uVar6 = FUN_0045fffe(uVar3,uVar6);
        FUN_0044b728(param_2,param_3,uVar6);
      }
      else if (local_54 < DAT_00550818) {
        uVar9 = FUN_004d3cf8(local_4c,local_58,local_5c);
        iVar4 = DAT_0055081c;
        if (uVar9 < 7) {
          uVar6 = FUN_00460084(*(undefined4 *)(DAT_0055081c + uVar9 * 4));
          uVar6 = FUN_0045fffe(*(undefined4 *)(iVar4 + uVar9 * 4),uVar6);
          FUN_0044b728(param_2,param_3,&DAT_0055016c,uVar6);
        }
        else {
          iVar4 = FUN_00466500();
          if ((iVar4 == 0) || (iVar4 = FUN_00466500(), iVar4 == 1)) {
            FUN_0044b728(param_2,param_3,DAT_00550b00,local_58,local_5c);
          }
          else {
            FUN_0044b728(param_2,param_3,DAT_00550b00,local_5c,local_58);
          }
        }
      }
      else {
        iVar4 = FUN_00466500();
        if ((iVar4 == 0) || (iVar4 = FUN_00466500(), iVar4 == 1)) {
          FUN_0044b728(param_2,param_3,DAT_00550b00,local_58,local_5c);
        }
        else {
          FUN_0044b728(param_2,param_3,DAT_00550b00,local_5c,local_58);
        }
      }
    }
    else {
      FUN_0044b728(param_2,param_3,&DAT_0054fe80,param_1);
    }
  }
  else {
    FUN_0044b728(param_2,param_3,&DAT_0054fe80,param_1);
  }
  return;
}

