
undefined4 FUN_004723d6(char param_1,char param_2)

{
  undefined1 local_110;
  undefined1 local_10f;
  undefined1 local_10e;
  undefined1 local_10d;
  byte local_10c [252];
  
  FUN_0043c0e4(&local_110,0xfe,0);
  local_110 = 0;
  local_10f = 0x1a;
  local_10e = 0x89;
  local_10d = 1;
  FUN_0043c0e4(local_10c,4,0);
  local_10c[0] = param_2 << 6 | param_1 << 7;
  APP_BleRingSendDataMsg(&local_110,8);
  return 0;
}

