
undefined8 UX_SendBLEStatusReply(char param_1)

{
  int iVar1;
  undefined4 uVar2;
  undefined4 local_10;
  undefined1 local_c;
  undefined1 local_b;
  undefined1 local_a;
  undefined1 uStack_9;
  
  local_10 = *DAT_0047d9c0;
  uVar2 = DAT_0047d9c0[1];
  local_c = (undefined1)uVar2;
  local_b = (undefined1)((uint)uVar2 >> 8);
  local_a = (undefined1)((uint)uVar2 >> 0x10);
  uStack_9 = (undefined1)((uint)uVar2 >> 0x18);
  local_c = FUN_0045a568();
  iVar1 = FUN_0045a568();
  if (iVar1 == 1) {
    local_b = 2;
  }
  else {
    local_b = 1;
  }
  local_a = param_1 != '\0';
  FUN_00464d1c(0x103,&local_10,8,0);
  return CONCAT17(uStack_9,CONCAT16(local_a,CONCAT15(local_b,CONCAT14(local_c,local_10))));
}

