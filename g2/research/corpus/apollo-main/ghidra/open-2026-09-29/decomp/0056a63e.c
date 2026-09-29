
undefined8
hciEvtProcessLeConnIQReport(byte *param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined2 *puVar2;
  undefined4 local_18;
  undefined4 local_14;
  
  iVar1 = FUN_004c9c50();
  local_18 = param_3;
  local_14 = param_4;
  if ((iVar1 == 0) || (iVar1 = FUN_0044b610(DAT_0056b144,&DAT_0056a968,3), iVar1 != 0)) {
    iVar1 = FUN_004c9c50();
    if ((iVar1 == 0) || (iVar1 = FUN_0044b610(DAT_0056b144,DAT_0056b380,4), iVar1 != 0)) {
      iVar1 = FUN_004c9c50();
      if ((iVar1 == 0) || (iVar1 = FUN_0044b610(DAT_0056b144,DAT_0056b144,4), iVar1 != 0)) {
        iVar1 = FUN_004c9c50();
        if (iVar1 == 0) {
          iVar1 = FUN_004c9c50();
          if ((iVar1 == 0) || (iVar1 = FUN_0044b610(&DAT_0056a904,&DAT_0056aa2c,3), iVar1 != 0)) {
            WsfTrace(DAT_0056b144,DAT_0056b148);
          }
        }
        else {
          iVar1 = FUN_0043d0ce();
          if (iVar1 << 0x1e < 0) {
            local_14 = DAT_0056b148;
            local_18 = 0x659;
            FUN_0043d574(4,&DAT_0056a904,DAT_0056b37c,DAT_0056b14c);
          }
        }
      }
      else {
        iVar1 = FUN_0043d0ce();
        if (iVar1 << 0x1e < 0) {
          local_14 = DAT_0056b148;
          local_18 = 0x659;
          FUN_0043d574(3,&DAT_0056a904,DAT_0056b37c,DAT_0056b14c);
        }
      }
    }
    else {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        local_14 = DAT_0056b148;
        local_18 = 0x659;
        FUN_0043d574(2,&DAT_0056a904,DAT_0056b37c,DAT_0056b14c);
      }
    }
  }
  else {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      local_14 = DAT_0056b148;
      local_18 = 0x659;
      FUN_0043d574(1,&DAT_0056a904,DAT_0056b37c,DAT_0056b14c);
    }
  }
  puVar2 = (undefined2 *)WsfBufAlloc(0xc0);
  if (puVar2 != (undefined2 *)0x0) {
    iVar1 = FUN_004c9c50();
    if ((iVar1 == 0) || (iVar1 = FUN_0044b610(DAT_0056b144,&DAT_0056a968,3), iVar1 != 0)) {
      iVar1 = FUN_004c9c50();
      if ((iVar1 == 0) || (iVar1 = FUN_0044b610(DAT_0056b144,DAT_0056b380,4), iVar1 != 0)) {
        iVar1 = FUN_004c9c50();
        if ((iVar1 == 0) || (iVar1 = FUN_0044b610(DAT_0056b144,DAT_0056b144,4), iVar1 != 0)) {
          iVar1 = FUN_004c9c50();
          if (iVar1 == 0) {
            iVar1 = FUN_004c9c50();
            if ((iVar1 == 0) || (iVar1 = FUN_0044b610(&DAT_0056a904,&DAT_0056aa2c,3), iVar1 != 0)) {
              WsfTrace(DAT_0056b144,DAT_0056b384);
            }
          }
          else {
            iVar1 = FUN_0043d0ce();
            if (iVar1 << 0x1e < 0) {
              local_14 = DAT_0056b384;
              local_18 = 0x65d;
              FUN_0043d574(4,&DAT_0056a904,DAT_0056b37c,DAT_0056b14c);
            }
          }
        }
        else {
          iVar1 = FUN_0043d0ce();
          if (iVar1 << 0x1e < 0) {
            local_14 = DAT_0056b384;
            local_18 = 0x65d;
            FUN_0043d574(3,&DAT_0056a904,DAT_0056b37c,DAT_0056b14c);
          }
        }
      }
      else {
        iVar1 = FUN_0043d0ce();
        if (iVar1 << 0x1e < 0) {
          local_14 = DAT_0056b384;
          local_18 = 0x65d;
          FUN_0043d574(2,&DAT_0056a904,DAT_0056b37c,DAT_0056b14c);
        }
      }
    }
    else {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        local_14 = DAT_0056b384;
        local_18 = 0x65d;
        FUN_0043d574(1,&DAT_0056a904,DAT_0056b37c,DAT_0056b14c);
      }
    }
    puVar2[2] = (ushort)param_1[1] * 0x100 + (ushort)*param_1;
    *(byte *)(puVar2 + 3) = param_1[2];
    *(byte *)((int)puVar2 + 7) = param_1[3];
    puVar2[4] = (ushort)param_1[5] * 0x100 + (ushort)param_1[4];
    *(byte *)(puVar2 + 5) = param_1[6];
    *(byte *)((int)puVar2 + 0xb) = param_1[7];
    *(byte *)(puVar2 + 6) = param_1[8];
    *(byte *)((int)puVar2 + 0xd) = param_1[9];
    puVar2[7] = (ushort)param_1[0xb] * 0x100 + (ushort)param_1[10];
    *(byte *)(puVar2 + 8) = param_1[0xc];
    *(undefined2 **)(puVar2 + 10) = puVar2 + 0xe;
    FUN_00439be4(*(undefined4 *)(puVar2 + 10),param_1 + 0xd,*(undefined1 *)(puVar2 + 8));
    *(undefined2 **)(puVar2 + 0xc) = puVar2 + 0x37;
    FUN_00439be4(*(undefined4 *)(puVar2 + 10),param_1 + 0xd + *(byte *)(puVar2 + 8),
                 *(undefined1 *)(puVar2 + 8));
    *puVar2 = puVar2[2];
    *(undefined1 *)((int)puVar2 + 3) = *(undefined1 *)((int)puVar2 + 0xd);
    *(undefined1 *)(puVar2 + 1) = 0x3d;
    (**(code **)(DAT_0056b140 + 8))(puVar2);
    WsfBufFree(puVar2);
  }
  return CONCAT44(local_14,local_18);
}

