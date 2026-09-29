
void SmpHandler(undefined4 param_1,undefined2 *param_2)

{
  int iVar1;
  int iVar2;
  undefined1 local_10 [4];
  
  if (param_2 != (undefined2 *)0x0) {
    if (*(char *)(param_2 + 1) == ' ') {
      SmpDbService();
    }
    else {
      if ((*(char *)(param_2 + 1) == '\x1c') && (*(int *)(param_2 + 4) != 0)) {
        WsfBufFree(*(undefined4 *)(param_2 + 4));
      }
      iVar1 = smpCcbByConnId((char)*param_2);
      if (*(char *)(iVar1 + 0x3d) != '\0') {
        if ((*(char *)(param_2 + 1) == '\v') &&
           (*(char *)(iVar1 + 0x41) != *(char *)((int)param_2 + 3))) {
          local_10[0] = 0;
          iVar2 = FUN_004c9c50(0);
          if ((iVar2 == 0) || (iVar2 = FUN_0044b610(PTR_DAT_00537ea0,&DAT_00537eb4,3), iVar2 != 0))
          {
            iVar2 = FUN_004c9c50();
            if ((iVar2 == 0) ||
               (iVar2 = FUN_0044b610(PTR_DAT_00537ea0,PTR_DAT_00537ea0,4), iVar2 != 0)) {
              iVar2 = FUN_004c9c50();
              if ((iVar2 == 0) ||
                 (iVar2 = FUN_0044b610(PTR_DAT_00537ea0,DAT_00537eb0,4), iVar2 != 0)) {
                iVar2 = FUN_004c9c50();
                if (iVar2 == 0) {
                  iVar2 = FUN_004c9c50();
                  if ((iVar2 == 0) ||
                     (iVar2 = FUN_0044b610(&DAT_00537eb8,&DAT_00537ec0,3), iVar2 != 0)) {
                    WsfTrace(PTR_DAT_00537ea0,DAT_00537ee0,*(undefined1 *)(iVar1 + 0x41),
                             *(undefined1 *)((int)param_2 + 3));
                  }
                }
                else {
                  iVar2 = FUN_0043d0ce();
                  if (iVar2 << 0x1e < 0) {
                    FUN_0043d574(4,&DAT_00537eb8,DAT_00537eac,DAT_00537ee4,0x375,DAT_00537ee0,
                                 *(undefined1 *)(iVar1 + 0x41),*(undefined1 *)((int)param_2 + 3));
                  }
                }
              }
              else {
                iVar2 = FUN_0043d0ce();
                if (iVar2 << 0x1e < 0) {
                  FUN_0043d574(3,&DAT_00537eb8,DAT_00537eac,DAT_00537ee4,0x375,DAT_00537ee0,
                               *(undefined1 *)(iVar1 + 0x41),*(undefined1 *)((int)param_2 + 3));
                }
              }
            }
            else {
              iVar2 = FUN_0043d0ce();
              if (iVar2 << 0x1e < 0) {
                FUN_0043d574(2,&DAT_00537eb8,DAT_00537eac,DAT_00537ee4,0x375,DAT_00537ee0,
                             *(undefined1 *)(iVar1 + 0x41),*(undefined1 *)((int)param_2 + 3));
              }
            }
          }
          else {
            iVar2 = FUN_0043d0ce();
            if (iVar2 << 0x1e < 0) {
              FUN_0043d574(1,&DAT_00537eb8,DAT_00537eac,DAT_00537ee4,0x375,DAT_00537ee0,
                           *(undefined1 *)(iVar1 + 0x41),*(undefined1 *)((int)param_2 + 3));
            }
          }
          while (iVar1 = WsfMsgDeq(DAT_00537ee8,local_10), iVar1 != 0) {
            WsfMsgFree();
          }
        }
        else {
          smpSmExecute(iVar1,param_2);
        }
      }
    }
  }
  return;
}

