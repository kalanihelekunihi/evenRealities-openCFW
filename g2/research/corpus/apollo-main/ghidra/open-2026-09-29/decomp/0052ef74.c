
undefined4 FUN_0052ef74(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 uVar1;
  undefined4 local_34;
  undefined1 auStack_30 [7];
  undefined1 auStack_29 [9];
  undefined4 local_20;
  undefined4 uStack_1c;
  undefined4 uStack_18;
  undefined4 uStack_14;
  
  local_20 = *DAT_0052f2a8;
  uStack_1c = DAT_0052f2a8[1];
  uStack_18 = DAT_0052f2a8[2];
  local_34 = 0;
  uStack_14 = param_4;
  FUN_0048949c(auStack_30,0x10);
  uVar1 = FUN_0052e612(param_1,&local_20,9,auStack_30,&local_34);
  FUN_00439be4(param_2,auStack_29,8);
  return uVar1;
}

