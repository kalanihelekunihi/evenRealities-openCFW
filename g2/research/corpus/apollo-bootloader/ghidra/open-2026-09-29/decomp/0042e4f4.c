
undefined4
alignment_dispatch_42e4f4(undefined4 param_1,undefined4 param_2,uint param_3,uint param_4)

{
  undefined4 uVar1;
  
  uVar1 = DAT_0042e510;
  if (((param_3 & 0xf) == 0) && ((param_4 & 3) == 0)) {
    uVar1 = aligned_guarded_dispatch_42e4a0();
  }
  return uVar1;
}

