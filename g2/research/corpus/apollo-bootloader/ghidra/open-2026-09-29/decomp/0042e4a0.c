
undefined8
aligned_guarded_dispatch_42e4a0
          (undefined4 param_1,undefined4 param_2,uint param_3,undefined4 param_4)

{
  bool bVar1;
  uint uVar2;
  uint uVar3;
  undefined4 uVar4;
  
  uVar2 = DAT_0042e510;
  if ((param_3 & 3) == 0) {
    uVar4 = param_4;
    uVar2 = critical_save();
    FUN_0041bd92();
    uVar3 = guarded_call_cleanup_42e8a4
                      (param_1,1,param_2,param_3 - 0x400000 >> 2,param_4,uVar2,uVar4);
    FUN_0041bde4();
    bVar1 = (bool)isCurrentModePrivileged();
    if (bVar1) {
      enableIRQinterrupts((uVar2 & 1) == 1);
    }
    param_2 = param_4;
    if (uVar3 == 0) {
      uVar2 = 0;
    }
    else {
      uVar2 = uVar3 | 0x8000100;
    }
  }
  return CONCAT44(param_2,uVar2);
}

