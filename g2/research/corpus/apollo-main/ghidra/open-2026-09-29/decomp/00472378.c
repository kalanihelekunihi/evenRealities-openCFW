
undefined4 FUN_00472378(char param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined1 local_110;
  undefined1 local_10f;
  undefined1 local_10e;
  undefined1 local_10d;
  undefined1 local_10c;
  undefined1 local_10b;
  undefined1 local_10a;
  undefined1 local_109;
  undefined4 uStack_10;
  
  uStack_10 = param_4;
  FUN_0043c0e4(&local_110,0xfe,0);
  local_110 = 0;
  local_10f = 0x1a;
  local_10e = 0x85;
  local_10d = 1;
  local_10b = 0xaa;
  local_10a = 0xaa;
  local_109 = 0xaa;
  if (param_1 == '\0') {
    local_10c = 0xff;
  }
  else {
    local_10c = 0;
  }
  APP_BleRingSendDataMsg(&local_110,8);
  return 0;
}

