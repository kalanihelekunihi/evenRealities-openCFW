
void FUN_004830da(undefined4 param_1)

{
  uint uVar1;
  int in_stack_00000000;
  uint in_stack_00000004;
  char in_stack_00000008;
  int in_stack_0000000c;
  uint in_stack_00000010;
  uint in_stack_00000014;
  uint in_stack_00000018;
  
  if (-1 < (int)(in_stack_00000018 << 0x1e)) {
    if (((in_stack_00000014 != 0) && ((int)(in_stack_00000018 << 0x1f) < 0)) &&
       ((in_stack_00000008 != '\0' || ((in_stack_00000018 & 0xc) != 0)))) {
      in_stack_00000014 = in_stack_00000014 - 1;
    }
    for (; (in_stack_00000004 < in_stack_00000010 && (in_stack_00000004 < 0x20));
        in_stack_00000004 = in_stack_00000004 + 1) {
      *(undefined1 *)(in_stack_00000000 + in_stack_00000004) = 0x30;
    }
    for (; (((int)(in_stack_00000018 << 0x1f) < 0 && (in_stack_00000004 < in_stack_00000014)) &&
           (in_stack_00000004 < 0x20)); in_stack_00000004 = in_stack_00000004 + 1) {
      *(undefined1 *)(in_stack_00000000 + in_stack_00000004) = 0x30;
    }
  }
  uVar1 = in_stack_00000004;
  if ((int)(in_stack_00000018 << 0x1b) < 0) {
    if ((((-1 < (int)(in_stack_00000018 << 0x15)) && (in_stack_00000004 != 0)) &&
        ((in_stack_00000004 == in_stack_00000010 || (in_stack_00000004 == in_stack_00000014)))) &&
       ((uVar1 = in_stack_00000004 - 1, uVar1 != 0 && (in_stack_0000000c == 0x10)))) {
      uVar1 = in_stack_00000004 - 2;
    }
    if (((in_stack_0000000c == 0x10) && (-1 < (int)(in_stack_00000018 << 0x1a))) && (uVar1 < 0x20))
    {
      *(undefined1 *)(in_stack_00000000 + uVar1) = 0x78;
      uVar1 = uVar1 + 1;
    }
    else if (((in_stack_0000000c == 0x10) && ((int)(in_stack_00000018 << 0x1a) < 0)) &&
            (uVar1 < 0x20)) {
      *(undefined1 *)(in_stack_00000000 + uVar1) = 0x58;
      uVar1 = uVar1 + 1;
    }
    else if ((in_stack_0000000c == 2) && (uVar1 < 0x20)) {
      *(undefined1 *)(in_stack_00000000 + uVar1) = 0x62;
      uVar1 = uVar1 + 1;
    }
    if (uVar1 < 0x20) {
      *(undefined1 *)(in_stack_00000000 + uVar1) = 0x30;
      uVar1 = uVar1 + 1;
    }
  }
  if (uVar1 < 0x20) {
    if (in_stack_00000008 == '\0') {
      if ((int)(in_stack_00000018 << 0x1d) < 0) {
        *(undefined1 *)(in_stack_00000000 + uVar1) = 0x2b;
      }
      else if ((int)(in_stack_00000018 << 0x1c) < 0) {
        *(undefined1 *)(in_stack_00000000 + uVar1) = 0x20;
      }
    }
    else {
      *(undefined1 *)(in_stack_00000000 + uVar1) = 0x2d;
    }
  }
  FUN_0048306c(param_1);
  return;
}

