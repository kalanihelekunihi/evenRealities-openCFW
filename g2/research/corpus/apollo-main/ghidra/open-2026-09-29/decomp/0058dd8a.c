
undefined4 FUN_0058dd8a(int param_1,uint param_2)

{
  undefined4 uVar1;
  
  param_2 = param_2 | *(uint *)(DAT_0058e450 + param_1 * 0x1000 + 0x3c);
  uVar1 = DAT_0058e84c;
  if ((((-1 < (int)(param_2 << 0x19)) && (uVar1 = DAT_0058e850, -1 < (int)(param_2 << 0x18))) &&
      (uVar1 = DAT_0058e854, -1 < (int)(param_2 << 0x17))) &&
     (((uVar1 = DAT_0058e858, -1 < (int)(param_2 << 0x16) &&
       (uVar1 = DAT_0058e85c, -1 < (int)(param_2 << 0x15))) &&
      (uVar1 = 0, (int)(param_2 << 0x13) < 0)))) {
    uVar1 = DAT_0058e910;
  }
  return uVar1;
}

