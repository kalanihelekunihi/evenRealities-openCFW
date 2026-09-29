
undefined8 FUN_0058e3f8(uint *param_1,int param_2)

{
  byte bVar1;
  undefined4 uVar2;
  undefined4 unaff_r7;
  
  if ((param_1 == (uint *)0x0) || ((*param_1 & 0x1ffffff) != DAT_0058e914)) {
    uVar2 = 2;
  }
  else {
    bVar1 = *(byte *)(param_2 + 0x34);
    if (bVar1 == 0) {
      uVar2 = FUN_0058e454();
    }
    else if (bVar1 == 2) {
      uVar2 = FUN_0058e4e8();
    }
    else if (bVar1 < 2) {
      uVar2 = FUN_0058e49e();
    }
    else if (bVar1 == 3) {
      uVar2 = FUN_0058e50a();
    }
    else {
      uVar2 = 1;
    }
  }
  return CONCAT44(unaff_r7,uVar2);
}

