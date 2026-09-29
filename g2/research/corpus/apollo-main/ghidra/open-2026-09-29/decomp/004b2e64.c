
undefined4 dmDevHciHandler(int param_1)

{
  char cVar1;
  undefined4 unaff_r7;
  
  cVar1 = *(char *)(param_1 + 2);
  if (cVar1 == '\0') {
    dmDevHciEvtReset();
  }
  else if (cVar1 == '\x12') {
    dmDevHciEvtVendorSpecCmdCmpl();
  }
  else if (cVar1 == '\x13') {
    dmDevHciEvtVendorSpec();
  }
  else if (cVar1 == '\x14') {
    dmDevHciEvtHwError();
  }
  return unaff_r7;
}

