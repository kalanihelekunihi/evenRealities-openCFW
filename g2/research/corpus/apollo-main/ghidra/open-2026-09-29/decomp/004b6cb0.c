
undefined8
DmReadRemoteFeatures(uint param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  ushort local_20;
  undefined1 local_1e;
  undefined1 local_1d;
  undefined1 local_1c;
  undefined1 uStack_1b;
  undefined2 local_1a;
  undefined4 local_18;
  undefined4 uStack_14;
  
  local_1c = (undefined1)param_2;
  uStack_1b = (undefined1)((uint)param_2 >> 8);
  local_1a = (undefined2)((uint)param_2 >> 0x10);
  local_20 = (ushort)param_1;
  local_1e = (undefined1)(param_1 >> 0x10);
  local_1d = (undefined1)(param_1 >> 0x18);
  local_18 = param_3;
  uStack_14 = param_4;
  iVar1 = dmConnCcbById(param_1 & 0xff);
  if (iVar1 != 0) {
    if (*(char *)(iVar1 + 0x2c) == '\0') {
      HciLeReadRemoteFeatCmd(*(undefined2 *)(iVar1 + 0xc));
    }
    else {
      FUN_0043c0e4(&local_20,0x10,0);
      local_1e = 0x57;
      local_20 = (ushort)*(byte *)(iVar1 + 0x10);
      local_1d = 0;
      local_1c = 0;
      local_1a = *(undefined2 *)(iVar1 + 0xc);
      local_18 = CONCAT13((char)((uint)*(undefined4 *)(iVar1 + 0x28) >> 0x18),
                          CONCAT12((char)((uint)*(undefined4 *)(iVar1 + 0x28) >> 0x10),
                                   CONCAT11((char)((uint)*(undefined4 *)(iVar1 + 0x28) >> 8),
                                            (char)*(undefined4 *)(iVar1 + 0x28))));
      (**(code **)(DAT_004b7430 + 0x9c))(&local_20);
    }
  }
  return CONCAT26(local_1a,CONCAT15(uStack_1b,
                                    CONCAT14(local_1c,CONCAT13(local_1d,CONCAT12(local_1e,local_20))
                                            )));
}

