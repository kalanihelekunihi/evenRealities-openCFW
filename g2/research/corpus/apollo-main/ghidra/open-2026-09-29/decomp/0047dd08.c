
uint FUN_0047dd08(undefined4 param_1,int param_2,int param_3,uint param_4)

{
  int iVar1;
  int iVar2;
  byte *local_18;
  int local_14 [3];
  
  local_18 = DAT_0047e288;
  local_14[0] = param_2;
  local_14[1] = param_3;
  local_14[2] = param_4;
  FUN_0043c0e4(local_14,0xc,0);
  iVar2 = 0;
  while ((*local_18 != 0 && (iVar2 < 3))) {
    if (*local_18 - 0x30 < 10) {
      iVar1 = FUN_0048d874(local_18,&local_18,10);
      local_14[iVar2] = iVar1;
      iVar2 = iVar2 + 1;
    }
    else {
      local_18 = local_18 + 1;
    }
  }
  return local_14[1] << 8 | local_14[0] << 0x10 | local_14[2];
}

