
undefined4 pt_cmd_2A_handler(int param_1,byte param_2,undefined1 *param_3,undefined1 *param_4)

{
  char cVar1;
  int iVar2;
  undefined4 uVar3;
  char cVar4;
  undefined1 uVar5;
  bool bVar6;
  bool bVar7;
  bool bVar8;
  bool bVar9;
  undefined4 uVar10;
  undefined4 uVar11;
  int local_34;
  int local_30;
  undefined1 *local_2c;
  undefined1 *puStack_28;
  
  puStack_28 = param_4;
  iVar2 = FUN_0043d0ce();
  if (iVar2 << 0x1e < 0) {
    FUN_0043d574(3,DAT_005735f4,DAT_005735f0,DAT_005735fc,0x838,DAT_005735f8);
  }
  iVar2 = FUN_0043d0ce();
  if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
    compress_log_output(0xc000000,DAT_00573600,DAT_00573600);
  }
  if ((((param_3 == (undefined1 *)0x0) || (local_2c = param_4, param_4 == (undefined1 *)0x0)) ||
      (param_1 == 0)) || (param_2 < 4)) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(1,DAT_005735f4,DAT_005735f0,DAT_005735fc,0x83b,DAT_00573200,DAT_005735fc);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x4400000,DAT_00573300,DAT_00573300,DAT_005735fc);
    }
    uVar3 = 0xffffffff;
  }
  else {
    *param_3 = 0x35;
    param_3[1] = 1;
    param_3[2] = 3;
    param_3[3] = 1;
    uVar3 = DAT_0057389c;
    cVar4 = '\0';
    local_30 = 0;
    local_34 = 1;
    iVar2 = file_open(DAT_0057389c,&DAT_0057301c);
    if (iVar2 == 0) {
      cVar4 = '\x01';
    }
    else {
      cVar1 = file_write(&local_34,1,4,iVar2);
      file_close(iVar2);
      if (cVar1 == '\x04') {
        iVar2 = file_open(uVar3,&DAT_00573020);
        if (iVar2 == 0) {
          cVar4 = '\x01';
        }
        else {
          cVar1 = file_read(&local_30,1,4,iVar2);
          file_close(iVar2);
          if ((cVar1 != '\x04') || (local_30 != local_34)) {
            cVar4 = '\x02';
            iVar2 = FUN_0043d0ce();
            if (iVar2 << 0x1e < 0) {
              FUN_0043d574(1,DAT_005735f4,DAT_005735f0,DAT_005735fc,0x86d,DAT_005738a8,4,cVar1);
            }
            iVar2 = FUN_0043d0ce();
            if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
              compress_log_output(0x4800000,DAT_005738ac,DAT_005738ac,4,cVar1);
            }
          }
        }
      }
      else {
        cVar4 = '\x02';
        iVar2 = FUN_0043d0ce();
        if (iVar2 << 0x1e < 0) {
          FUN_0043d574(1,DAT_005735f4,DAT_005735f0,DAT_005735fc,0x85a,DAT_005738a0,4,cVar1);
        }
        iVar2 = FUN_0043d0ce();
        if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
          compress_log_output(0x4800000,DAT_005738a4,DAT_005738a4,4,cVar1);
        }
      }
    }
    param_3[4] = cVar4;
    uVar3 = DAT_005738bc;
    uVar10 = DAT_005738b8;
    uVar11 = DAT_005738b4;
    iVar2 = file_open(DAT_005738b0,&DAT_00573020);
    bVar6 = iVar2 != 0;
    if (bVar6) {
      file_close();
    }
    iVar2 = file_open(uVar11,&DAT_00573020);
    bVar7 = iVar2 != 0;
    if (bVar7) {
      file_close();
    }
    iVar2 = file_open(uVar10,&DAT_00573020);
    bVar8 = iVar2 != 0;
    if (bVar8) {
      file_close();
    }
    iVar2 = file_open(uVar3,&DAT_00573020);
    bVar9 = iVar2 != 0;
    if (bVar9) {
      file_close();
    }
    if ((((bVar7 && bVar6) && bVar8) && bVar9) && (cVar4 == '\0')) {
      param_3[4] = 0;
      uVar5 = 0;
    }
    else {
      uVar5 = 1;
      param_3[4] = 1;
    }
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(3,DAT_005735f4,DAT_005735f0,DAT_005735fc,0x897,DAT_005738c0,bVar6,bVar7,bVar8,
                   bVar9,uVar5);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0xd400000,DAT_005738c4,DAT_005738c4,bVar6,bVar7,bVar8,bVar9,uVar5);
    }
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(3,DAT_005735f4,DAT_005735f0,DAT_005735fc,0x89a,DAT_005738c8,uVar5);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0xc400000,DAT_00573c50,DAT_00573c50,uVar5);
    }
    *local_2c = 5;
    uVar3 = 0;
  }
  return uVar3;
}

