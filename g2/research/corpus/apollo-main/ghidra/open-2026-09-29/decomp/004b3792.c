
undefined8 FUN_004b3792(undefined2 *param_1,int *param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  undefined4 uVar3;
  int *local_20;
  undefined4 local_1c;
  undefined4 uStack_18;
  
  iVar1 = DAT_004b3c8c;
  local_20 = param_2;
  local_1c = param_3;
  uStack_18 = param_4;
  if (*(char *)(DAT_004b3c8c + 0x74) == '\0') {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      local_1c = DAT_004b42e4;
      local_20 = (int *)0x270;
      FUN_0043d574(2,DAT_004b3ca0,DAT_004b3c9c,DAT_004b42e8);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x8000000,DAT_004b42ec);
    }
  }
  else {
    if (*(char *)((int)param_1 + 3) == '\0') {
      *DAT_004b43f8 = 1;
      *param_2 = *(int *)(iVar1 + 0x70);
      if (*param_2 != 0) {
        if (*param_2 + 0x6c != 0) {
          AttsCccInitTable((char)param_2[1],*param_2 + 0x6c);
        }
        FUN_0047b40c(*param_2,&local_20,&local_1c);
        AttsCsfConnOpen((char)param_2[1],(uint)local_20 & 0xff,local_1c);
        if ((char)local_20 == '\x03') {
          GattSendServiceChangedInd((char)param_2[1],1,0xffff);
        }
        iVar2 = FUN_0047ae78(*param_2,8,0);
        if (iVar2 != 0) {
          AttsSetCsrk((char)param_2[1],iVar2,0);
          AttsSetSignCounter((char)param_2[1],*(undefined4 *)(*param_2 + 0x80));
        }
      }
      if (*(char *)(iVar1 + 0x6c) != '\0') {
        FUN_004b36b2(param_2);
        *(undefined1 *)(iVar1 + 0x6c) = 0;
      }
    }
    else if ((*(char *)((int)param_1 + 3) == '\x05') && (*(int *)(DAT_004b3c8c + 0x70) != 0)) {
      iVar2 = FUN_0047ae78(*(undefined4 *)(DAT_004b3c8c + 0x70),4,0);
      if (iVar2 != 0) {
        DmConnPeerAddr((char)param_2[1],iVar2);
      }
      uVar3 = FUN_0047a630(*(undefined4 *)(iVar1 + 0x70));
      *(undefined4 *)(iVar1 + 0x70) = uVar3;
      if ((*(int *)(iVar1 + 0x70) != 0) &&
         (iVar2 = FUN_0047ae78(*(undefined4 *)(iVar1 + 0x70),4,0), iVar2 != 0)) {
        uVar3 = DmConnPeerAddr((char)param_2[1]);
        DmPrivResolveAddr(uVar3,iVar2,*param_1);
        goto LAB_004b38f0;
      }
    }
    *(undefined1 *)(iVar1 + 0x74) = 0;
    if ((*param_2 == 0) && (*(char *)(*DAT_004b4508 + 4) != '\0')) {
      DmSecSlaveReq((char)param_2[1],*(undefined1 *)*DAT_004b4508);
    }
  }
LAB_004b38f0:
  return CONCAT44(local_1c,local_20);
}

