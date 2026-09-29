
void profileAnccProcMsg(undefined4 param_1,undefined2 *param_2)

{
  char cVar1;
  int iVar2;
  
  if (param_2 == (undefined2 *)0x0) {
    return;
  }
  cVar1 = *(char *)(param_2 + 1);
  if (cVar1 != '\x05') {
    if (cVar1 == '\t') {
      return;
    }
    if (cVar1 == '\n') {
      return;
    }
    if ((cVar1 != '\r') && (cVar1 != '\x0e')) {
      if (cVar1 == '\'') {
        iVar2 = DmConnRole((char)*param_2);
        if (iVar2 != 1) {
          return;
        }
        profileAnccConnOpenAdapter((char)*param_2,*DAT_004bf8f0);
        return;
      }
      if (cVar1 == '(') {
        iVar2 = DmConnRole((char)*param_2);
        if (iVar2 != 1) {
          return;
        }
        profileAnccConnCloseAdapter();
        return;
      }
      if (cVar1 != -0x5e) {
        return;
      }
      iVar2 = anccActionListPop();
      if (iVar2 != 0) {
        AnccGetNotificationAttribute
                  (*(undefined4 *)(DAT_004bf970 + 4),
                   *(undefined4 *)(DAT_004bf970 + (uint)*(ushort *)(DAT_004bf970 + 8) * 0xc + 0x20))
        ;
        iVar2 = anccNoConnActive();
        if (iVar2 != 0) {
          return;
        }
        fw_event_loop_push_delayed(DAT_004bf8dc,0xa2,200);
        return;
      }
      fw_event_loop_remove_delayed(DAT_004bf8dc);
      return;
    }
  }
  _ancsValueUpdate(param_2);
  return;
}

