
void FUN_00508e5c(undefined4 param_1,uint param_2)

{
  if (param_2 < 0x100) {
    FUN_00508e9a(param_1,param_2 & 0xff);
  }
  else {
    FUN_00508f34(param_1,param_2 & 0xffff);
  }
  return;
}

