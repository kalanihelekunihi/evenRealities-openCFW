
undefined8 hciTrSerialRxIncoming(char *param_1,ushort param_2,undefined4 param_3,undefined4 param_4)

{
  char cVar1;
  int *piVar2;
  ushort *puVar3;
  char *pcVar4;
  char *pcVar5;
  uint uVar6;
  int iVar7;
  byte bVar8;
  ushort uVar9;
  ushort uVar10;
  uint uVar11;
  uint uVar12;
  undefined4 local_28;
  
  local_28 = CONCAT22((short)((uint)param_4 >> 0x10),param_2);
  uVar10 = 0;
  uVar9 = param_2;
  do {
    pcVar5 = DAT_0053035c;
    pcVar4 = DAT_00530358;
    puVar3 = DAT_0053034c;
    piVar2 = DAT_00530348;
    if (uVar9 == 0) {
      uVar11 = (uint)uVar10;
LAB_00530344:
      return CONCAT44(local_28,uVar11);
    }
    cVar1 = *param_1;
    if (*DAT_0053035c == '\0') {
      *DAT_00530358 = cVar1;
      *DAT_0053034c = 0;
      *pcVar5 = '\x01';
      *DAT_00530350 = 1;
      param_1 = param_1 + 1;
      uVar10 = uVar10 + 1;
      uVar9 = uVar9 - 1;
    }
    else if (*DAT_0053035c == '\x01') {
      uVar11 = 0;
      if (*DAT_00530358 == '\x04') {
        uVar12 = 2;
      }
      else {
        if (*DAT_00530358 != '\x02') {
          *DAT_0053035c = '\0';
          uVar11 = (uint)param_2;
          goto LAB_00530344;
        }
        uVar12 = 4;
      }
      if (*DAT_0053034c != uVar12) {
        *(char *)(DAT_00530360 + (uint)*DAT_0053034c) = cVar1;
        *puVar3 = *puVar3 + 1;
        param_1 = param_1 + 1;
        uVar10 = uVar10 + 1;
        uVar9 = uVar9 - 1;
      }
      if (*puVar3 == uVar12) {
        if (*pcVar4 == '\x04') {
          uVar11 = (uint)*(byte *)(DAT_00530360 + 1);
        }
        else if (*pcVar4 == '\x02') {
          uVar11 = (uint)*(byte *)(DAT_00530360 + 3) * 0x100 + (uint)*(byte *)(DAT_00530360 + 2);
        }
        if ((*pcVar4 == '\x02') && (uVar6 = HciGetMaxRxAclLen(), uVar11 <= uVar6)) {
          iVar7 = WsfMsgDataAlloc(uVar11 + uVar12 & 0xffff,0);
          *DAT_00530354 = iVar7;
        }
        else if ((*pcVar4 == '\x04') && (uVar11 < 0x100)) {
          iVar7 = WsfMsgAlloc(uVar11 + uVar12 & 0xffff);
          *DAT_00530354 = iVar7;
        }
        piVar2 = DAT_00530348;
        if (*DAT_00530354 == 0) {
          *pcVar5 = '\0';
          uVar11 = (uint)param_2;
          goto LAB_00530344;
        }
        *DAT_00530348 = *DAT_00530354;
        for (bVar8 = 0; bVar8 < uVar12; bVar8 = bVar8 + 1) {
          *(undefined1 *)*piVar2 = *(undefined1 *)(DAT_00530360 + (uint)bVar8);
          *piVar2 = *piVar2 + 1;
        }
        *puVar3 = (ushort)uVar11;
        if (*puVar3 == 0) {
          *pcVar5 = '\x03';
        }
        else {
          *pcVar5 = '\x02';
        }
      }
    }
    else if (*DAT_0053035c == '\x02') {
      *(char *)*DAT_00530348 = cVar1;
      *piVar2 = *piVar2 + 1;
      puVar3 = DAT_0053034c;
      *DAT_0053034c = *DAT_0053034c - 1;
      if (*puVar3 == 0) {
        *pcVar5 = '\x03';
      }
      param_1 = param_1 + 1;
      uVar10 = uVar10 + 1;
      uVar9 = uVar9 - 1;
    }
    if (*pcVar5 == '\x03') {
      *DAT_00530350 = 0;
      if (*DAT_00530354 != 0) {
        hciCoreRecv(*DAT_00530358,*DAT_00530354);
      }
      *pcVar5 = '\0';
    }
  } while( true );
}

