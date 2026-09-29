
undefined4 silent_mode_ui_event_handler(int param_1,char *param_2,uint param_3,undefined4 param_4)

{
  undefined4 *puVar1;
  int *piVar2;
  int iVar3;
  undefined4 uVar4;
  undefined4 uVar5;
  int iVar6;
  undefined4 uStack_14;
  
  puVar1 = DAT_00469b98;
  uStack_14 = param_4;
  if (param_1 == 2) {
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      param_3 = (uint)*DAT_00469b88;
      param_1 = 0xd6;
      param_2 = DAT_00469b8c;
      FUN_0043d574(3,DAT_00469b3c,DAT_00469b38,DAT_00469b90,0xd6,DAT_00469b8c,param_3);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0xc400000,DAT_00469b94,DAT_00469b94,*DAT_00469b88,param_1,param_2,param_3)
      ;
    }
    *DAT_00469b44 = 1;
    puVar1 = DAT_00469b98;
    FUN_0043c0e4(DAT_00469b98,0x1c,0);
    piVar2 = DAT_00469b9c;
    if (*DAT_00469b88 == 0) {
      iVar3 = FUN_0043de82(param_4);
      *piVar2 = iVar3;
      FUN_0043f4c0(*piVar2,0x240,0x120);
      FUN_0043f09a(*piVar2,0,0);
      FUN_0043dfa4(*piVar2,0x10);
      uVar4 = FUN_0044104c(0);
      FUN_0044127e(*piVar2,uVar4,0);
      FUN_0044129e(*piVar2,0xff,0);
      FUN_0044131c(*piVar2,0,0);
      FUN_0044146a(*piVar2,0,0);
      silent_mode_apply_text_style(*piVar2,0,0);
      uVar4 = FUN_0043de82(*piVar2);
      *puVar1 = uVar4;
      FUN_0043f4c0(*puVar1,0x240,0x120);
      FUN_0043f09a(*puVar1,0,0);
      FUN_0043dfa4(*puVar1,0x10);
      FUN_0044129e(*puVar1,0,0);
      FUN_0044131c(*puVar1,0,0);
      silent_mode_apply_text_style(*puVar1,0,0);
      uVar4 = FUN_00499416(*puVar1);
      puVar1[1] = uVar4;
      FUN_0043f4c0(puVar1[1],400,0x1e);
      FUN_0044145a(puVar1[1],2,0);
      uVar4 = FUN_0044104c(0xffffff);
      FUN_0044140e(puVar1[1],uVar4,0);
      FUN_0044143e(puVar1[1],*DAT_00469ba0,0);
      FUN_0044129e(puVar1[1],0,0);
      FUN_0044131c(puVar1[1],0,0);
      uVar4 = DAT_00469bb8;
      uVar5 = FUN_00460084(DAT_00469bb8);
      uVar4 = FUN_0045fffe(uVar4,uVar5);
      FUN_0049942e(puVar1[1],uVar4);
      FUN_0043f6b8(puVar1[1],9,0,0);
      puVar1[6] = 0;
    }
    else {
      iVar3 = FUN_0043de82(param_4);
      *piVar2 = iVar3;
      FUN_0043f4c0(*piVar2,0x240,0x120);
      FUN_0043f09a(*piVar2,0,0);
      FUN_0043dfa4(*piVar2,0x10);
      uVar4 = FUN_0044104c(0);
      FUN_0044127e(*piVar2,uVar4,0);
      FUN_0044129e(*piVar2,0xff,0);
      FUN_0044131c(*piVar2,0,0);
      FUN_0044146a(*piVar2,0,0);
      silent_mode_apply_text_style(*piVar2,0,0);
      uVar4 = FUN_0043de82(*piVar2);
      *puVar1 = uVar4;
      FUN_0043f4c0(*puVar1,0x240,0x120);
      FUN_0043f09a(*puVar1,0,0);
      FUN_0043dfa4(*puVar1,0x10);
      FUN_0044129e(*puVar1,0,0);
      FUN_0044131c(*puVar1,0,0);
      silent_mode_apply_text_style(*puVar1,0,0);
      uVar4 = FUN_00499416(*puVar1);
      puVar1[1] = uVar4;
      FUN_0043f4c0(puVar1[1],0x1e4,0x5a);
      FUN_0044145a(puVar1[1],2,0);
      uVar4 = FUN_0044104c(0xffffff);
      FUN_0044140e(puVar1[1],uVar4,0);
      FUN_0044143e(puVar1[1],*DAT_00469ba0,0);
      FUN_0044129e(puVar1[1],0,0);
      FUN_0044131c(puVar1[1],0,0);
      uVar4 = DAT_00469ba4;
      uVar5 = FUN_00460084(DAT_00469ba4);
      uVar4 = FUN_0045fffe(uVar4,uVar5);
      FUN_0049942e(puVar1[1],uVar4);
      FUN_0043f6b8(puVar1[1],2,0,0x20);
      uVar4 = FUN_00498668(*puVar1);
      puVar1[4] = uVar4;
      FUN_0043f09a(puVar1[4],0xd4,0x94);
      FUN_00498680(puVar1[4],DAT_00469ba8);
      FUN_0043dfa4(puVar1[4],0x10);
      uVar4 = FUN_00498668(*puVar1);
      puVar1[5] = uVar4;
      FUN_0043f09a(puVar1[5],0x143,0x94);
      FUN_00498680(puVar1[5],DAT_00469bac);
      FUN_0043dfa4(puVar1[5],0x10);
      uVar4 = FUN_00498668(*puVar1);
      puVar1[2] = uVar4;
      FUN_0043f09a(puVar1[2],0x175,0xc6);
      FUN_00498680(puVar1[2],DAT_00469bb0);
      FUN_0043dfa4(puVar1[2],0x10);
      uVar4 = FUN_00498668(*puVar1);
      puVar1[3] = uVar4;
      FUN_0043f09a(puVar1[3],0xb4,0xc6);
      FUN_00498680(puVar1[3],DAT_00469bb4);
      FUN_0043dfa4(puVar1[3],0x10);
      puVar1[6] = 0;
    }
    piVar2 = DAT_00469b9c;
    FUN_0046410a(*DAT_00469b9c);
    *(int *)(DAT_00469bbc + 4) = *piVar2;
  }
  else if (param_1 == 3) {
    if (((param_2 != (char *)0x0) && (param_3 != 0)) && (*param_2 == -1)) {
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        FUN_0043d574(4,DAT_00469b3c,DAT_00469b38,DAT_00469b90,0x14f,DAT_00469bc0);
      }
      iVar3 = FUN_0043d0ce();
      if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
        compress_log_output(0x10000000,DAT_00469bc4,DAT_00469bc4);
      }
      if (*DAT_00469b9c != 0) {
        FUN_004641b6(*DAT_00469b9c,0x10a);
        *DAT_00469b44 = 0;
        iVar3 = FUN_0045a568();
        if ((iVar3 == 1) && (*DAT_00469b88 == 0)) {
          notify_silent_mode_to_app(0);
          FUN_0045a8ee(1,0,0,500);
        }
      }
    }
  }
  else if (param_1 == 4) {
    if (*DAT_00469b9c == 0) {
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        FUN_0043d574(2,DAT_00469b3c,DAT_00469b38,DAT_00469b90,0x161,DAT_00469bc8);
      }
      iVar3 = FUN_0043d0ce();
      if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
        compress_log_output(0x8000000,DAT_00469bcc,DAT_00469bcc);
      }
    }
    else {
      DAT_00469b98[6] = DAT_00469b98[6] + 1;
      if (0xb3 < (int)puVar1[6]) {
        puVar1[6] = 0;
        iVar3 = FUN_0045a568();
        if (iVar3 == 1) {
          iVar3 = FUN_0043d0ce();
          if (iVar3 << 0x1e < 0) {
            FUN_0043d574(4,DAT_00469b3c,DAT_00469b38,DAT_00469b90,0x16c,DAT_00469bd0);
          }
          iVar3 = FUN_0043d0ce();
          if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
            compress_log_output(0x10000000,DAT_00469bd4,DAT_00469bd4);
          }
          uStack_14 = CONCAT31(uStack_14._1_3_,0xff);
          iVar3 = FUN_00464bb2(0x10a,&uStack_14,1,0);
          if (iVar3 != 0) {
            iVar6 = FUN_0043d0ce();
            if (iVar6 << 0x1e < 0) {
              FUN_0043d574(1,DAT_00469b3c,DAT_00469b38,DAT_00469b90,0x171,DAT_00469bd8,iVar3);
            }
            iVar6 = FUN_0043d0ce();
            if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
              compress_log_output(0x4400000,DAT_00469bdc,DAT_00469bdc,iVar3);
            }
          }
        }
      }
    }
  }
  else if (param_1 == 5) {
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      FUN_0043d574(4,DAT_00469b3c,DAT_00469b38,DAT_00469b90,0x17a,DAT_00469be0);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0x10000000,DAT_00469be4,DAT_00469be4);
    }
    if (*DAT_00469b88 != 0) {
      SilentMode_SetStatus(1);
      notify_silent_mode_to_app(1);
    }
    *DAT_00469b44 = 0;
    *DAT_00469b54 = 0;
    silent_mode_noop_callback();
  }
  return 0;
}

