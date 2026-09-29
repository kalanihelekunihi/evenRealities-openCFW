
undefined4
FUN_0054fa56(int param_1,undefined4 *param_2,undefined4 *param_3,undefined4 *param_4,
            undefined4 *param_5,undefined4 *param_6,undefined4 *param_7)

{
  uint uVar1;
  undefined4 uVar2;
  undefined1 auStack_38 [2];
  undefined1 local_36;
  undefined1 local_34;
  undefined1 auStack_30 [4];
  undefined1 auStack_2c [2];
  undefined1 auStack_2a [2];
  char local_28;
  undefined1 auStack_27 [2];
  undefined1 auStack_25 [2];
  undefined1 auStack_23 [2];
  undefined1 local_21;
  
  if ((param_1 == 0) || (uVar1 = FUN_0044a43c(param_1), uVar1 < 0xf)) {
    uVar2 = 0xffffffff;
  }
  else {
    FUN_0044b5a0(auStack_30,param_1,0xf);
    local_21 = 0;
    if (local_28 == 'T') {
      FUN_0044b5a0(auStack_38,auStack_30,4);
      local_34 = 0;
      uVar2 = thunk_FUN_0048d86c(auStack_38);
      *param_2 = uVar2;
      FUN_0044b5a0(auStack_38,auStack_2c,2);
      local_36 = 0;
      uVar2 = thunk_FUN_0048d86c(auStack_38);
      *param_3 = uVar2;
      FUN_0044b5a0(auStack_38,auStack_2a,2);
      local_36 = 0;
      uVar2 = thunk_FUN_0048d86c(auStack_38);
      *param_4 = uVar2;
      FUN_0044b5a0(auStack_38,auStack_27,2);
      local_36 = 0;
      uVar2 = thunk_FUN_0048d86c(auStack_38);
      *param_5 = uVar2;
      FUN_0044b5a0(auStack_38,auStack_25,2);
      local_36 = 0;
      uVar2 = thunk_FUN_0048d86c(auStack_38);
      *param_6 = uVar2;
      FUN_0044b5a0(auStack_38,auStack_23,2);
      local_36 = 0;
      uVar2 = thunk_FUN_0048d86c(auStack_38);
      *param_7 = uVar2;
      uVar2 = 0;
    }
    else {
      uVar2 = 0xffffffff;
    }
  }
  return uVar2;
}

