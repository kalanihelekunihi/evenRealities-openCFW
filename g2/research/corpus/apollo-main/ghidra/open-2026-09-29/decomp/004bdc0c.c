
undefined4 evenOtaProcMsg(undefined2 *param_1)

{
  char cVar1;
  int iVar2;
  undefined4 unaff_r7;
  
  cVar1 = *(char *)(param_1 + 1);
  if (cVar1 == '\x12') {
    if (*(char *)((int)param_1 + 3) == '\0') {
      DAT_004bde14[3] = 1;
    }
    else {
      DAT_004bde14[3] = 0;
    }
  }
  else if (cVar1 == '\x14') {
    _evenOtaProcCccState();
  }
  else if (cVar1 != '\'') {
    if (cVar1 == '(') {
      iVar2 = DmConnRole((char)*param_1);
      if (iVar2 == 1) {
        *DAT_004bde14 = 0;
        semantic_OtaCancelExport();
      }
    }
    else if (cVar1 == -0x60) {
      FUN_004d3534(0,0);
    }
    else if (cVar1 == -0x5f) {
      FUN_004bb04a(*DAT_004bde14);
      fw_event_loop_push_delayed(DAT_004bde24,0,200);
    }
    else if (cVar1 == -0x59) {
      DAT_004bde14[3] = 0;
      AttsHandleValueNtf((char)*param_1,0x824,param_1[4],*(undefined4 *)(param_1 + 2));
    }
  }
  return unaff_r7;
}

