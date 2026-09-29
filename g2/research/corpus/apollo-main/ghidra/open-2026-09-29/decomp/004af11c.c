
undefined4 SVC_NvdbWriteSysData(byte param_1,undefined4 *param_2)

{
  undefined1 *puVar1;
  byte bVar2;
  undefined2 uVar3;
  uint uVar4;
  int iVar5;
  undefined4 uVar6;
  bool bVar7;
  
  bVar7 = false;
  uVar6 = 0;
  if (param_1 == 0) {
    if (param_2 != (undefined4 *)0x0) {
      iVar5 = FUN_0043d0ce();
      if (iVar5 << 0x1e < 0) {
        FUN_0043d574(4,DAT_004af890,DAT_004af88c,DAT_004afca8,0x6c,DAT_004afc0c,param_2);
      }
      iVar5 = FUN_0043d0ce();
      if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
        compress_log_output(0x10400000,DAT_004afc64,DAT_004afc64,param_2);
      }
      uVar4 = FUN_0044a43c(param_2);
      if (uVar4 < 0xf) {
        bVar2 = FUN_0044a43c(param_2);
      }
      else {
        bVar2 = 0xe;
      }
      puVar1 = DAT_004af880;
      FUN_00439be4(DAT_004af880 + 1,param_2,bVar2);
      puVar1[bVar2 + 1] = 0;
      bVar7 = true;
    }
  }
  else if (param_1 == 2) {
    if (param_2 != (undefined4 *)0x0) {
      iVar5 = FUN_0043d0ce();
      if (iVar5 << 0x1e < 0) {
        FUN_0043d574(4,DAT_004af890,DAT_004af88c,DAT_004afca8,0x85,DAT_004afcb8,*param_2);
      }
      iVar5 = FUN_0043d0ce();
      if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
        compress_log_output(0x10400000,DAT_004afcbc,DAT_004afcbc,*param_2);
      }
      *(undefined4 *)(DAT_004af880 + 0x28) = *param_2;
      bVar7 = true;
    }
  }
  else if (param_1 < 2) {
    if (param_2 != (undefined4 *)0x0) {
      iVar5 = FUN_0043d0ce();
      if (iVar5 << 0x1e < 0) {
        FUN_0043d574(4,DAT_004af890,DAT_004af88c,DAT_004afca8,0x79,DAT_004afcac,param_2);
      }
      iVar5 = FUN_0043d0ce();
      if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
        compress_log_output(0x10400000,DAT_004afcb0,DAT_004afcb0,param_2);
      }
      uVar4 = FUN_0044a43c(param_2);
      if (uVar4 < 0x16) {
        bVar2 = FUN_0044a43c(param_2);
      }
      else {
        bVar2 = 0x15;
      }
      puVar1 = DAT_004af880;
      FUN_00439be4(DAT_004af880 + 0x10,param_2,bVar2);
      puVar1[bVar2 + 0x10] = 0;
      bVar7 = true;
    }
  }
  else if (param_1 == 4) {
    if (param_2 != (undefined4 *)0x0) {
      iVar5 = FUN_0043d0ce();
      if (iVar5 << 0x1e < 0) {
        FUN_0043d574(4,DAT_004af890,DAT_004af88c,DAT_004afca8,0x99,DAT_004afcc8,
                     *(undefined1 *)param_2);
      }
      iVar5 = FUN_0043d0ce();
      if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
        compress_log_output(0x10400000,DAT_004afccc,DAT_004afccc,*(undefined1 *)param_2);
      }
      DAT_004af880[0x2d] = *(undefined1 *)param_2;
      bVar7 = true;
    }
  }
  else if (param_1 < 4) {
    if (param_2 != (undefined4 *)0x0) {
      iVar5 = FUN_0043d0ce();
      if (iVar5 << 0x1e < 0) {
        FUN_0043d574(4,DAT_004af890,DAT_004af88c,DAT_004afca8,0x8f,DAT_004afcc0,
                     *(undefined1 *)param_2);
      }
      iVar5 = FUN_0043d0ce();
      if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
        compress_log_output(0x10400000,DAT_004afcc4,DAT_004afcc4,*(undefined1 *)param_2);
      }
      DAT_004af880[0x2c] = *(undefined1 *)param_2;
      bVar7 = true;
    }
  }
  else if (param_1 == 6) {
    if (param_2 != (undefined4 *)0x0) {
      iVar5 = FUN_0043d0ce();
      if (iVar5 << 0x1e < 0) {
        FUN_0043d574(4,DAT_004af890,DAT_004af88c,DAT_004afca8,0xad,DAT_004afcd0,param_2[3],
                     param_2[4],param_2[5],param_2[6],param_2[7],param_2[8]);
      }
      iVar5 = FUN_0043d0ce();
      if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
        compress_log_output(0x11800000,DAT_004afcd4,DAT_004afcd4,param_2[3],param_2[4],param_2[5],
                            param_2[6],param_2[7],param_2[8]);
      }
      FUN_00439c04(DAT_004afcd8,param_2,0x28);
      bVar7 = true;
    }
  }
  else if (param_1 < 6) {
    if (param_2 != (undefined4 *)0x0) {
      iVar5 = FUN_0043d0ce();
      if (iVar5 << 0x1e < 0) {
        FUN_0043d574(4,DAT_004af890,DAT_004af88c,DAT_004afca8,0xa3,DAT_004afbb8,
                     *(undefined1 *)param_2);
      }
      iVar5 = FUN_0043d0ce();
      if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
        compress_log_output(0x10400000,DAT_004afca4,DAT_004afca4,*(undefined1 *)param_2);
      }
      DAT_004af880[0x2e] = *(undefined1 *)param_2;
      bVar7 = true;
    }
  }
  else if (param_1 == 8) {
    if (param_2 != (undefined4 *)0x0) {
      iVar5 = FUN_0043d0ce();
      if (iVar5 << 0x1e < 0) {
        FUN_0043d574(4,DAT_004af890,DAT_004af88c,DAT_004afca8,0xc0,DAT_004aff64,param_2[3],
                     param_2[4],param_2[5],param_2[6],param_2[7],param_2[8]);
      }
      iVar5 = FUN_0043d0ce();
      if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
        compress_log_output(0x11800000,DAT_004aff68,DAT_004aff68,param_2[3],param_2[4],param_2[5],
                            param_2[6],param_2[7],param_2[8]);
      }
      FUN_00439c04(DAT_004aff6c,param_2,0x28);
      bVar7 = true;
    }
  }
  else if (param_1 < 8) {
    if (param_2 != (undefined4 *)0x0) {
      iVar5 = FUN_0043d0ce();
      if (iVar5 << 0x1e < 0) {
        FUN_0043d574(4,DAT_004af890,DAT_004af88c,DAT_004afca8,0xb7,DAT_004aff58,param_2[3],
                     param_2[4],param_2[5],param_2[6],param_2[7],param_2[8]);
      }
      iVar5 = FUN_0043d0ce();
      if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
        compress_log_output(0x11800000,DAT_004aff5c,DAT_004aff5c,param_2[3],param_2[4],param_2[5],
                            param_2[6],param_2[7],param_2[8]);
      }
      FUN_00439c04(DAT_004aff60,param_2,0x28);
      bVar7 = true;
    }
  }
  else if (param_1 == 10) {
    if (param_2 != (undefined4 *)0x0) {
      iVar5 = FUN_0043d0ce();
      if (iVar5 << 0x1e < 0) {
        FUN_0043d574(4,DAT_004af890,DAT_004af88c,DAT_004afca8,0xd2,DAT_004aff78,
                     *(undefined1 *)param_2);
      }
      iVar5 = FUN_0043d0ce();
      if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
        compress_log_output(0x10400000,DAT_004aff7c,DAT_004aff7c,*(undefined1 *)param_2);
      }
      DAT_004af880[0xa9] = *(undefined1 *)param_2;
      bVar7 = true;
    }
  }
  else if (param_1 < 10) {
    if (param_2 != (undefined4 *)0x0) {
      iVar5 = FUN_0043d0ce();
      if (iVar5 << 0x1e < 0) {
        FUN_0043d574(4,DAT_004af890,DAT_004af88c,DAT_004afca8,0xc9,DAT_004aff70,
                     *(undefined1 *)param_2);
      }
      iVar5 = FUN_0043d0ce();
      if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
        compress_log_output(0x10400000,DAT_004aff74,DAT_004aff74,*(undefined1 *)param_2);
      }
      DAT_004af880[0xa8] = *(undefined1 *)param_2;
      bVar7 = true;
    }
  }
  else if (param_1 == 0xc) {
    if (param_2 != (undefined4 *)0x0) {
      iVar5 = FUN_0043d0ce();
      if (iVar5 << 0x1e < 0) {
        FUN_0043d574(4,DAT_004af890,DAT_004af88c,DAT_004afca8,0xec,DAT_004aff88,
                     *(undefined1 *)param_2);
      }
      iVar5 = FUN_0043d0ce();
      if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
        compress_log_output(0x10400000,DAT_004aff8c,DAT_004aff8c,*(undefined1 *)param_2);
      }
      DAT_004af880[0xab] = *(undefined1 *)param_2;
      bVar7 = true;
    }
  }
  else if (param_1 < 0xc) {
    if (param_2 != (undefined4 *)0x0) {
      iVar5 = FUN_0043d0ce();
      if (iVar5 << 0x1e < 0) {
        FUN_0043d574(4,DAT_004af890,DAT_004af88c,DAT_004afca8,0xe3,DAT_004aff80,
                     *(undefined1 *)param_2);
      }
      iVar5 = FUN_0043d0ce();
      if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
        compress_log_output(0x10400000,DAT_004aff84,DAT_004aff84,*(undefined1 *)param_2);
      }
      DAT_004af880[0xaa] = *(undefined1 *)param_2;
      bVar7 = true;
    }
  }
  else if (param_1 == 0xd) {
    bVar7 = param_2 != (undefined4 *)0x0;
    if (bVar7) {
      FUN_00439be4(DAT_004af880,param_2,0xac);
    }
  }
  else {
    iVar5 = FUN_0043d0ce();
    if (iVar5 << 0x1e < 0) {
      FUN_0043d574(2,DAT_004af890,DAT_004af88c,DAT_004afca8,0xf2,DAT_004aff90);
    }
    iVar5 = FUN_0043d0ce();
    if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
      compress_log_output(0x8000000,DAT_004aff94,DAT_004aff94);
    }
    bVar7 = false;
  }
  puVar1 = DAT_004af880;
  if (bVar7) {
    *DAT_004af880 = 2;
    uVar3 = FUN_0049acd4(puVar1,0x26,0);
    *(undefined2 *)(puVar1 + 0x26) = uVar3;
    uVar6 = SVC_NvdbWrite(DAT_004af898,puVar1,0xac);
  }
  return uVar6;
}

