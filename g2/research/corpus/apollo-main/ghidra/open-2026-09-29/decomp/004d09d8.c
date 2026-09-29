
undefined8 FUN_004d09d8(undefined4 param_1,undefined4 param_2,uint param_3,undefined4 param_4)

{
  bool bVar1;
  uint uVar2;
  uint uVar3;
  undefined4 uVar4;
  
  uVar2 = DAT_004d0a48;
  if ((param_3 & 3) == 0) {
    uVar4 = param_4;
    uVar2 = FUN_00473940();
    FUN_0047f3c6();
    uVar3 = FUN_00541b7c(param_1,1,param_2,param_3 - 0x400000 >> 2,param_4,uVar2,uVar4);
    FUN_0047f418();
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

