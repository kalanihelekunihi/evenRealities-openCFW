
undefined8
hciEvtProcessLeConlessIQReport
          (byte *param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined2 *puVar1;
  int iVar2;
  undefined4 local_18;
  undefined4 local_14;
  
  puVar1 = (undefined2 *)WsfBufAlloc(0xc0);
  local_18 = param_3;
  local_14 = param_4;
  if (puVar1 != (undefined2 *)0x0) {
    iVar2 = FUN_004c9c50();
    if ((iVar2 == 0) || (iVar2 = FUN_0044b610(DAT_0056b144,&DAT_0056a968,3), iVar2 != 0)) {
      iVar2 = FUN_004c9c50();
      if ((iVar2 == 0) || (iVar2 = FUN_0044b610(DAT_0056b144,DAT_0056b380,4), iVar2 != 0)) {
        iVar2 = FUN_004c9c50();
        if ((iVar2 == 0) || (iVar2 = FUN_0044b610(DAT_0056b144,DAT_0056b144,4), iVar2 != 0)) {
          iVar2 = FUN_004c9c50();
          if (iVar2 == 0) {
            iVar2 = FUN_004c9c50();
            if ((iVar2 == 0) || (iVar2 = FUN_0044b610(&LAB_0056abd0,&DAT_0056aa2c,3), iVar2 != 0)) {
              WsfTrace(DAT_0056b144,DAT_0056b388);
            }
          }
          else {
            iVar2 = FUN_0043d0ce();
            if (iVar2 << 0x1e < 0) {
              local_14 = DAT_0056b388;
              local_18 = 0x690;
              FUN_0043d574(4,&LAB_0056abd0,DAT_0056b37c,DAT_0056b38c);
            }
          }
        }
        else {
          iVar2 = FUN_0043d0ce();
          if (iVar2 << 0x1e < 0) {
            local_14 = DAT_0056b388;
            local_18 = 0x690;
            FUN_0043d574(3,&LAB_0056abd0,DAT_0056b37c,DAT_0056b38c);
          }
        }
      }
      else {
        iVar2 = FUN_0043d0ce();
        if (iVar2 << 0x1e < 0) {
          local_14 = DAT_0056b388;
          local_18 = 0x690;
          FUN_0043d574(2,&LAB_0056abd0,DAT_0056b37c,DAT_0056b38c);
        }
      }
    }
    else {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        local_14 = DAT_0056b388;
        local_18 = 0x690;
        FUN_0043d574(1,&LAB_0056abd0,DAT_0056b37c,DAT_0056b38c);
      }
    }
    puVar1[2] = (ushort)param_1[1] * 0x100 + (ushort)*param_1;
    *(byte *)(puVar1 + 3) = param_1[2];
    puVar1[4] = (ushort)param_1[4] * 0x100 + (ushort)param_1[3];
    *(byte *)(puVar1 + 5) = param_1[5];
    *(byte *)((int)puVar1 + 0xb) = param_1[6];
    *(byte *)(puVar1 + 6) = param_1[7];
    *(byte *)((int)puVar1 + 0xd) = param_1[8];
    puVar1[7] = (ushort)param_1[10] * 0x100 + (ushort)param_1[9];
    *(byte *)(puVar1 + 8) = param_1[0xb];
    *(undefined2 **)(puVar1 + 10) = puVar1 + 0xe;
    FUN_00439be4(*(undefined4 *)(puVar1 + 10),param_1 + 0xc,*(undefined1 *)(puVar1 + 8));
    *(undefined2 **)(puVar1 + 0xc) = puVar1 + 0x37;
    FUN_00439be4(*(undefined4 *)(puVar1 + 10),param_1 + 0xc + *(byte *)(puVar1 + 8),
                 *(undefined1 *)(puVar1 + 8));
    *puVar1 = puVar1[2];
    *(undefined1 *)((int)puVar1 + 3) = *(undefined1 *)((int)puVar1 + 0xd);
    *(undefined1 *)(puVar1 + 1) = 0x56;
    (**(code **)(DAT_0056b140 + 8))(puVar1);
    WsfBufFree(puVar1);
  }
  return CONCAT44(local_14,local_18);
}

