
undefined8 WsfMsgAlloc(short param_1)

{
  int iVar1;
  undefined4 unaff_r7;
  
  iVar1 = WsfBufAlloc(param_1 + 8);
  if (iVar1 != 0) {
    iVar1 = iVar1 + 8;
  }
  return CONCAT44(unaff_r7,iVar1);
}

