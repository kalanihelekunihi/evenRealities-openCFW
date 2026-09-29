
void FUN_004ac828(undefined1 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  char cVar1;
  undefined1 auStack_1c [4];
  undefined1 local_18;
  undefined1 local_17;
  char local_16;
  undefined1 local_15;
  undefined1 auStack_14 [4];
  undefined4 uStack_10;
  
  uStack_10 = param_4;
  FUN_0043c0e4(&local_18,8,0);
  FUN_0043c0e4(auStack_1c,4,0);
  cVar1 = FUN_0045a568();
  FUN_004ac776(auStack_1c);
  local_17 = 4;
  if (cVar1 == '\x01') {
    local_15 = 2;
  }
  else {
    local_15 = 1;
  }
  local_18 = param_1;
  local_16 = cVar1;
  FUN_00439be4(auStack_14,auStack_1c,4);
  FUN_00465480(0x81,&local_18,8,0,5);
  return;
}

