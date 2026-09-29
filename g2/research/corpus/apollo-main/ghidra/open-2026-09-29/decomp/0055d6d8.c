
undefined8 FUN_0055d6d8(undefined4 param_1,byte param_2,uint param_3,undefined4 param_4)

{
  uint uVar1;
  uint uVar2;
  undefined4 local_18;
  undefined4 uStack_14;
  
  local_18 = param_3;
  if (param_2 == 1) {
    uVar1 = 0xfffffffe;
  }
  else {
    uStack_14 = param_4;
    uVar1 = FUN_0055d794(param_1,(int)&local_18 + 2);
    if ((uVar1 == 0) && (local_18._2_1_ != '\0')) {
      uVar1 = FUN_0055d588(param_1,4,&local_18,1);
      if (uVar1 != 0) goto LAB_0055d792;
      local_18 = local_18 & 0xfffffffc;
      uVar2 = FUN_0055d5e2(param_1,4,&local_18,1);
      do {
        uVar1 = FUN_0055d794(param_1,(int)&local_18 + 2);
        uVar1 = uVar2 | uVar1;
        if (uVar1 != 0) break;
        uVar2 = 0;
      } while (local_18._2_1_ != '\0');
    }
    if (((uVar1 == 0) && (param_2 != 0)) &&
       (uVar1 = FUN_0055d588(param_1,4,(int)&local_18 + 1,1), uVar1 == 0)) {
      local_18 = local_18 & 0xfffffcff;
      param_2 = param_2 | local_18._1_1_;
      local_18._0_2_ = CONCAT11(param_2,(undefined1)local_18);
      uVar1 = FUN_0055d5e2(param_1,4,(int)&local_18 + 1,1);
    }
  }
LAB_0055d792:
  return CONCAT44(local_18,uVar1);
}

