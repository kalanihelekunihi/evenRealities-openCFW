
undefined4
smpDmConnCback(undefined2 *param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined1 uVar1;
  int iVar2;
  int iVar3;
  undefined4 local_10;
  
  local_10 = param_4;
  iVar2 = smpCcbByConnId((char)*param_1);
  if (*(char *)(param_1 + 1) == '\'') {
    iVar3 = DmConnRole((char)*param_1);
    if (iVar3 == 0) {
      *(undefined1 *)(iVar2 + 0x3a) = 1;
      *(undefined1 *)(iVar2 + 0x3f) = 0xb;
    }
    else {
      *(undefined1 *)(iVar2 + 0x3a) = 0;
      *(undefined1 *)(iVar2 + 0x3f) = 1;
    }
    *(undefined2 *)(iVar2 + 0x38) = param_1[3];
    *(char *)(iVar2 + 0x3d) = (char)*param_1;
    *(undefined1 *)(iVar2 + 0x3b) = 0;
    *(undefined1 *)(iVar2 + 0x3c) = 0;
    uVar1 = SmpDbGetFailureCount((char)*param_1);
    *(undefined1 *)(iVar2 + 0x42) = uVar1;
    *(undefined1 *)(iVar2 + 0x43) = 0;
    *(undefined1 *)(iVar2 + 0x3e) = 0;
    *(undefined1 *)(iVar2 + 0x44) = 0;
    smpResumeAttemptsState((char)*param_1);
  }
  else if ((*(char *)(iVar2 + 0x3d) != '\0') && (*(char *)(param_1 + 1) == '(')) {
    SmpDbSetFailureCount((char)*param_1,*(undefined1 *)(iVar2 + 0x42));
    local_10 = CONCAT13(*(char *)(param_1 + 4) + ' ',CONCAT12(10,*param_1));
    smpSmExecute(iVar2,&local_10);
    *(undefined1 *)(iVar2 + 0x3d) = 0;
    if (*(int *)(iVar2 + 0x34) != 0) {
      WsfMsgFree(*(undefined4 *)(iVar2 + 0x34));
      *(undefined4 *)(iVar2 + 0x34) = 0;
    }
  }
  return local_10;
}

