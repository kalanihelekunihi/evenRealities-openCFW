
undefined4 FUN_005b7b60(int param_1,undefined4 param_2,char *param_3,undefined4 param_4)

{
  undefined4 *puVar1;
  undefined4 *puVar2;
  undefined4 *puVar3;
  undefined *puVar4;
  undefined *puVar5;
  undefined4 *puVar6;
  int *piVar7;
  int *piVar8;
  undefined1 uVar9;
  int iVar10;
  undefined4 uVar11;
  char cVar12;
  byte bVar13;
  uint local_88 [3];
  undefined1 auStack_7c [12];
  undefined1 auStack_70 [4];
  int local_6c;
  undefined4 local_60;
  undefined4 local_5c;
  uint local_58;
  uint local_54;
  undefined1 auStack_48 [32];
  undefined4 uStack_28;
  
  uStack_28 = param_4;
  if (param_1 == 0) {
    iVar10 = FUN_0043d0ce();
    if (iVar10 << 0x1e < 0) {
      FUN_0043d574(1,PTR_s_dashboard_wf_l1_005b84a0,PTR_s_D__01_workspace_s200_ap510b_iar__005b849c,
                   DAT_005b87d4,0xfd,DAT_005b8718);
    }
    iVar10 = FUN_0043d0ce();
    if ((iVar10 << 0x1f < 0) || (iVar10 = FUN_0043d0ce(), iVar10 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_005b8730,DAT_005b8730);
    }
    uVar11 = 0xffffffff;
  }
  else {
    if ((param_3 == (char *)0x0) || (*param_3 != '\x01')) {
      *DAT_005b8734 = '\0';
      cVar12 = '\x01';
      bVar13 = 4;
    }
    else {
      *DAT_005b8734 = param_3[4];
      cVar12 = param_3[5];
      bVar13 = param_3[6];
    }
    iVar10 = FUN_0043d0ce();
    if (iVar10 << 0x1e < 0) {
      local_88[0] = (uint)bVar13;
      FUN_0043d574(3,PTR_s_dashboard_wf_l1_005b84a0,PTR_s_D__01_workspace_s200_ap510b_iar__005b849c,
                   DAT_005b87d4,0x10f,DAT_005b8738,*DAT_005b8734,cVar12);
    }
    iVar10 = FUN_0043d0ce();
    if ((iVar10 << 0x1f < 0) || (iVar10 = FUN_0043d0ce(), iVar10 << 0x1d < 0)) {
      compress_log_output(0xcc00000,DAT_005b87cc,DAT_005b87cc,*DAT_005b8734,cVar12,bVar13);
    }
    puVar1 = DAT_005b87d0;
    uVar11 = FUN_0043de82(param_1);
    *puVar1 = uVar11;
    FUN_0043f4c0(*puVar1,200,0x120);
    FUN_0043f09a(*puVar1,param_2,0);
    uVar11 = FUN_0044104c(0);
    FUN_0044127e(*puVar1,uVar11,0);
    FUN_0044129e(*puVar1,0,0);
    FUN_0044131c(*puVar1,0,0);
    FUN_0044133a(*puVar1,0,0);
    FUN_00441378(*puVar1,0,0);
    FUN_00441386(*puVar1,0,0);
    FUN_005b7934(*puVar1,0,0);
    FUN_0044146a(*puVar1,0,0);
    uVar11 = FUN_0044104c(0xffffff);
    FUN_0044140e(*puVar1,uVar11,0);
    FUN_0044142e(*puVar1,0xff,0);
    FUN_0043dfa4(*puVar1,0x10);
    service_time_current_calendar_get(auStack_70);
    puVar2 = DAT_005b8864;
    uVar11 = FUN_00499416(*puVar1);
    *puVar2 = uVar11;
    FUN_0043f506(*puVar2,0x3fffffff);
    FUN_0043f568(*puVar2,0x3fffffff);
    FUN_0043f0e0(*puVar2,0);
    FUN_0043f142(*puVar2,1);
    FUN_0043c0e4(auStack_48,0x20,0);
    iVar10 = DAT_005b8868;
    uVar11 = FUN_00460084(*(undefined4 *)(DAT_005b8868 + local_6c * 4));
    uVar11 = FUN_0045fffe(*(undefined4 *)(iVar10 + local_6c * 4),uVar11);
    FUN_004b4728(auStack_48,DAT_005b886c,uVar11,local_5c);
    FUN_0049942e(*puVar2,auStack_48);
    *DAT_005b8870 = local_60;
    *DAT_005b8874 = local_5c;
    *DAT_005b8878 = local_6c;
    FUN_0044143e(*puVar2,DAT_005b8860,0);
    puVar2 = DAT_005b887c;
    uVar11 = FUN_0043de82(*puVar1);
    *puVar2 = uVar11;
    FUN_0043f4c0(*puVar2,0x3fffffff,0x3fffffff);
    FUN_0044129e(*puVar2,0,0);
    FUN_0044131c(*puVar2,0,0);
    FUN_0044133a(*puVar2,0,0);
    FUN_00441386(*puVar2,0,0);
    FUN_005b7934(*puVar2,0,0);
    FUN_0044146a(*puVar2,0,0);
    FUN_0043dfa4(*puVar2,0x10);
    FUN_0043f6ac(*puVar2,3);
    FUN_0043f0e0(*puVar2,0);
    FUN_0043f142(*puVar2,5);
    FUN_0048ba78(*puVar2,0);
    FUN_0048ba92(*puVar2,0,2,2);
    FUN_00441254(*puVar2,0xc,0);
    puVar3 = DAT_005b898c;
    uVar11 = FUN_00498668(*puVar2);
    *puVar3 = uVar11;
    FUN_0043ded4(*puVar3,0x10000);
    FUN_0043dfa4(*puVar3,0x10);
    uVar9 = ui_common_api_fn_00509f8e();
    uVar11 = FUN_005b7966(uVar9);
    FUN_00498680(*puVar3,uVar11);
    iVar10 = FUN_0047d9c4();
    puVar3 = DAT_005b8990;
    if (iVar10 != 0) {
      uVar11 = FUN_00498668(*puVar2);
      *puVar3 = uVar11;
      FUN_0043ded4(*puVar3,0x10000);
      FUN_0043dfa4(*puVar3,0x10);
      iVar10 = FUN_0047d9cc();
      if (iVar10 == 0) {
        FUN_00498680(*puVar3,DAT_005b8994);
      }
      else {
        uVar9 = FUN_0049c5bc();
        uVar11 = FUN_005b7a02(uVar9);
        FUN_00498680(*puVar3,uVar11);
      }
    }
    puVar2 = DAT_005b8998;
    uVar11 = FUN_00499416(*puVar1);
    *puVar2 = uVar11;
    FUN_0043f506(*puVar2,0x3fffffff);
    FUN_0043f568(*puVar2,0x3fffffff);
    puVar3 = DAT_005b899c;
    uVar11 = FUN_00499416(*puVar1);
    *puVar3 = uVar11;
    FUN_0043f506(*puVar3,0x3fffffff);
    FUN_0043f568(*puVar3,0x3fffffff);
    FUN_0043c0e4(auStack_7c,10,0);
    FUN_0043c0e4(local_88,10,0);
    if (*DAT_005b8734 == '\0') {
      FUN_0043f0e0(*puVar2,0x2a);
      FUN_0043f142(*puVar2,0x46);
      puVar4 = PTR_s__1d__1d_005b89a0;
      FUN_004b4728(auStack_7c,PTR_s__1d__1d_005b89a0,local_58 / 10,local_58 % 10);
      FUN_0049942e(*puVar2,auStack_7c);
      puVar5 = PTR_DAT_005b89a4;
      FUN_0044143e(*puVar2,PTR_DAT_005b89a4,0);
      FUN_0043f0e0(*puVar3,0x2a);
      FUN_0043f142(*puVar3,0x9c);
      FUN_004b4728(local_88,puVar4,local_54 / 10,local_54 % 10);
      FUN_0049942e(*puVar3,local_88);
      FUN_0044143e(*puVar3,puVar5,0);
    }
    else {
      FUN_0043f0e0(*puVar2,0x2c);
      FUN_0043f142(*puVar2,0x74);
      FUN_004b4728(auStack_7c,PTR_DAT_005b89a8,local_58);
      FUN_0049942e(*puVar2,auStack_7c);
      puVar4 = PTR_DAT_005b89ac;
      FUN_0044143e(*puVar2,PTR_DAT_005b89ac,0);
      puVar6 = DAT_005b89b0;
      uVar11 = FUN_00499416(*puVar1);
      *puVar6 = uVar11;
      FUN_0043f506(*puVar6,0x3fffffff);
      FUN_0043f568(*puVar6,0x3fffffff);
      FUN_0049942e(*puVar6,&DAT_005b82c8);
      FUN_0044143e(*puVar6,puVar4,0);
      FUN_0043f6d6(*puVar6,*puVar2,0x14,6,0);
      FUN_004b4728(local_88,PTR_DAT_005b89a8,local_54);
      FUN_0049942e(*puVar3,local_88);
      FUN_0044143e(*puVar3,puVar4,0);
      FUN_0043f6d6(*puVar3,*puVar6,0x14,6,0);
    }
    *DAT_005b89b4 = local_58;
    *DAT_005b89b8 = local_54;
    piVar7 = DAT_005b89bc;
    FUN_005b7aba(DAT_005b89bc,*puVar1,cVar12,1);
    piVar8 = DAT_005b89c0;
    FUN_005b7aba(DAT_005b89c0,*puVar1,bVar13,0);
    puVar2 = DAT_005b89c4;
    uVar11 = FUN_0043de82(*puVar1);
    *puVar2 = uVar11;
    FUN_0043f506(*puVar2,0x82);
    FUN_0043f568(*puVar2,0x18);
    FUN_0043f0e0(*puVar2,0);
    FUN_0043f142(*puVar2,0x106);
    uVar11 = FUN_0044104c(0);
    FUN_0044127e(*puVar2,uVar11,0);
    FUN_0044129e(*puVar2,0xff,0);
    FUN_0044131c(*puVar2,0,0);
    FUN_005b7934(*puVar2,0,0);
    FUN_0043dfa4(*puVar2,0x10);
    puVar1 = DAT_005b89c8;
    uVar11 = FUN_00498668(*puVar2);
    *puVar1 = uVar11;
    FUN_0043f506(*puVar1,0x3fffffff);
    FUN_0043f568(*puVar1,0x3fffffff);
    FUN_0043f0e0(*puVar1,0);
    FUN_0043f142(*puVar1,0);
    FUN_00498680(*puVar1,PTR_DAT_005b89cc);
    FUN_0043ded4(*puVar1,0x10000);
    FUN_0043dfa4(*puVar1,0x10);
    iVar10 = UX_GetSystemBLEStatus();
    if (iVar10 == 0) {
      if (*piVar7 != 0) {
        FUN_0043ded4(*piVar7,1);
      }
      if (piVar7[1] != 0) {
        FUN_0043ded4(piVar7[1],1);
      }
      FUN_0043dfa4(*puVar2,1);
      if (*piVar8 != 0) {
        FUN_0043ded4(*piVar8,1);
      }
      if (piVar8[1] != 0) {
        FUN_0043ded4(piVar8[1],1);
      }
    }
    else {
      FUN_0043ded4(*puVar2,1);
      if (*piVar7 != 0) {
        FUN_0043dfa4(*piVar7,1);
      }
      if (piVar7[1] != 0) {
        FUN_0043dfa4(piVar7[1],1);
      }
      if (*piVar8 != 0) {
        FUN_0043dfa4(*piVar8,1);
      }
      if (piVar8[1] != 0) {
        FUN_0043dfa4(piVar8[1],1);
      }
    }
    iVar10 = FUN_0043d0ce();
    if (iVar10 << 0x1e < 0) {
      FUN_0043d574(3,PTR_s_dashboard_wf_l1_005b84a0,PTR_s_D__01_workspace_s200_ap510b_iar__005b849c,
                   DAT_005b87d4,0x1cd,PTR_s_layout1_created_at_x__d_005b89d0,param_2);
    }
    iVar10 = FUN_0043d0ce();
    if ((iVar10 << 0x1f < 0) || (iVar10 = FUN_0043d0ce(), iVar10 << 0x1d < 0)) {
      compress_log_output(0xc400000,PTR_s__dashboard_wf_l1_layout1_created_005b89d4,
                          PTR_s__dashboard_wf_l1_layout1_created_005b89d4,param_2);
    }
    uVar11 = 0;
  }
  return uVar11;
}

