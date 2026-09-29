
undefined8
_ancsAnccAttrCback(ushort *param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  ushort uVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  ushort *puVar6;
  
  iVar2 = DAT_004bf6c0;
  if ((char)param_1[5] == '\0') {
    uVar1 = param_1[0x1ad];
    iVar5 = DAT_004bf6c0 + 0x31c;
    puVar6 = param_1;
    FUN_00439be4(iVar5,param_1 + 0x1ae,uVar1);
    *(undefined1 *)(iVar2 + (uint)uVar1 + 0x31c) = 0;
    iVar4 = FUN_0044a43c(iVar5);
    iVar3 = DAT_004bf900;
    FUN_00439be4(DAT_004bf900 + 8,iVar5,iVar4 + 1);
    *(char *)(iVar3 + 4) = (char)param_1[(uint)*param_1 * 6 + 0xb];
    *(char *)(iVar3 + 5) = (char)param_1[(uint)*param_1 * 6 + 10];
    if (((*(char *)(iVar3 + 5) == '\0') || (*(char *)(iVar3 + 5) == '\x01')) &&
       (*(char *)(iVar2 + 0x31c) != '\0')) {
      iVar4 = FUN_0043d0ce();
      if (iVar4 << 0x1e < 0) {
        puVar6 = (ushort *)0x1ef;
        param_2 = DAT_004bf904;
        FUN_0043d574(4,DAT_004bf220,DAT_004bf21c,DAT_004bf908,0x1ef,DAT_004bf904,iVar5,param_4);
      }
      iVar4 = FUN_0043d0ce();
      if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
        compress_log_output(0x10400000,DAT_004bf90c,DAT_004bf90c,iVar5);
      }
      AncsGetAppAttribute(*(undefined4 *)(iVar2 + 4),iVar5);
    }
    *(undefined1 *)(iVar3 + 6) = *(undefined1 *)((int)param_1 + (uint)*param_1 * 0xc + 0x15);
    *(undefined1 *)(iVar3 + 7) = *(undefined1 *)((int)param_1 + (uint)*param_1 * 0xc + 0x17);
    param_1 = puVar6;
  }
  else if ((char)param_1[5] == '\x01') {
    if (param_1[4] != 0) {
      FUN_00439be4(DAT_004bf910,(int)param_1 + param_1[3] + 0x354,param_1[4]);
    }
  }
  else if ((char)param_1[5] == '\x02') {
    if (param_1[4] != 0) {
      FUN_00439be4(DAT_004bf914,(int)param_1 + param_1[3] + 0x354,param_1[4]);
    }
  }
  else if ((char)param_1[5] == '\x03') {
    if (param_1[4] != 0) {
      FUN_00439be4(DAT_004bf918,(int)param_1 + param_1[3] + 0x354,param_1[4]);
    }
  }
  else if ((char)param_1[5] == '\x05') {
    if (param_1[4] != 0) {
      FUN_00439be4(DAT_004bf91c,(int)param_1 + param_1[3] + 0x354,param_1[4]);
    }
  }
  else if ((char)param_1[5] == '\x06') {
    if (param_1[4] != 0) {
      *(undefined1 *)(DAT_004bf900 + 0x2f8) = 0;
    }
  }
  else if (((char)param_1[5] == '\a') && (param_1[4] != 0)) {
    *(undefined1 *)(DAT_004bf900 + 0x2f8) = 1;
  }
  return CONCAT44(param_2,param_1);
}

