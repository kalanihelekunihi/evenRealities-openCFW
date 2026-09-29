
void FT_Set_Pixel_Sizes(undefined4 param_1,uint param_2,uint param_3)

{
  uint uVar1;
  undefined1 local_18 [4];
  int local_14;
  int local_10;
  undefined4 local_c;
  undefined4 local_8;
  
  uVar1 = param_3;
  if ((param_2 != 0) && (uVar1 = param_2, param_3 == 0)) {
    param_3 = param_2;
  }
  if (uVar1 == 0) {
    uVar1 = 1;
  }
  if (param_3 == 0) {
    param_3 = 1;
  }
  if (0xfffe < uVar1) {
    uVar1 = 0xffff;
  }
  if (0xfffe < param_3) {
    param_3 = 0xffff;
  }
  local_18[0] = 0;
  local_14 = uVar1 << 6;
  local_10 = param_3 << 6;
  local_c = 0;
  local_8 = 0;
  FT_Request_Size(param_1,local_18);
  return;
}

