
undefined4 even_ai_heartbeat_timer_mgr_check_timeout(void)

{
  int *piVar1;
  undefined4 uVar2;
  int iVar3;
  
  piVar1 = DAT_004e316c;
  if (*(char *)((int)DAT_004e316c + 9) == '\0') {
    uVar2 = 0;
  }
  else {
    iVar3 = osKernelGetTickCount();
    if ((uint)(iVar3 - *piVar1) < (uint)piVar1[1]) {
      uVar2 = 0;
    }
    else {
      *(undefined1 *)(piVar1 + 2) = 2;
      *(undefined1 *)((int)piVar1 + 9) = 0;
      uVar2 = 1;
    }
  }
  return uVar2;
}

