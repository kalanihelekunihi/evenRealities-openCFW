
undefined4 HciCoreHandler(int param_1,int param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  undefined4 local_10;
  
  local_10 = param_4;
  if (param_2 == 0) {
    if (param_1 << 0x1f < 0) {
      while (iVar1 = DAT_00530d6c, iVar2 = WsfMsgDeq(DAT_00530d6c,&local_10), iVar2 != 0) {
        if ((char)local_10 == '\x04') {
          hciEvtProcessMsg(iVar2);
          if (*(char *)(iVar1 + 0x21) != '\0') {
            hciCoreResetSequence(iVar2);
          }
          WsfMsgFree(iVar2);
        }
        else if ((char)local_10 == '\x02') {
          iVar2 = hciCoreAclReassembly(iVar2);
          if (iVar2 != 0) {
            (**(code **)(iVar1 + 0x10))(iVar2);
          }
        }
        else if (*(int *)(iVar1 + 0x18) == 0) {
          WsfMsgFree(iVar2);
        }
        else {
          (**(code **)(iVar1 + 0x18))(iVar2);
        }
      }
    }
  }
  else if (*(char *)(param_2 + 2) == '\x01') {
    hciCmdTimeout(param_2);
  }
  return local_10;
}

