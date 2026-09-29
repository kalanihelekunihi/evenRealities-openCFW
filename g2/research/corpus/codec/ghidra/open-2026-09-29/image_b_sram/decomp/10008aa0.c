
void FUN_10008aa0(void)

{
  uint uVar1;
  undefined1 *puVar2;
  int in_stack_00000000;
  uint in_stack_00000004;
  char in_stack_00000008;
  int in_stack_0000000c;
  uint in_stack_00000010;
  uint in_stack_00000014;
  uint in_stack_00000018;
  
  if ((in_stack_00000018 & 2) == 0) {
    if ((in_stack_00000014 == 0) || ((in_stack_00000018 & 1) == 0)) {
      if ((in_stack_00000004 < in_stack_00000010) && (in_stack_00000004 < 0x20)) {
LAB_10008ae0:
        puVar2 = (undefined1 *)(in_stack_00000000 + in_stack_00000004);
        do {
          in_stack_00000004 = in_stack_00000004 + 1;
          *puVar2 = 0x30;
          if (in_stack_00000010 <= in_stack_00000004) break;
          puVar2 = puVar2 + 1;
        } while (in_stack_00000004 != 0x20);
        uVar1 = in_stack_00000014;
        if ((in_stack_00000018 & 1) != 0) goto LAB_10008b06;
      }
      goto LAB_10008b3a;
    }
    if ((in_stack_00000008 != '\0') || ((in_stack_00000018 & 0xc) != 0)) {
      in_stack_00000014 = in_stack_00000014 - 1;
    }
    uVar1 = in_stack_00000014;
    if (in_stack_00000004 < in_stack_00000010) {
      if (in_stack_00000004 < 0x20) goto LAB_10008ae0;
      if (in_stack_00000014 <= in_stack_00000004) goto LAB_10008b3a;
    }
    else {
LAB_10008b06:
      in_stack_00000014 = uVar1;
      if (uVar1 <= in_stack_00000004) goto LAB_10008b3a;
      if (in_stack_00000004 < 0x20) {
        puVar2 = (undefined1 *)(in_stack_00000000 + in_stack_00000004);
        do {
          in_stack_00000004 = in_stack_00000004 + 1;
          *puVar2 = 0x30;
          in_stack_00000014 = in_stack_00000004;
          if (in_stack_00000004 == uVar1) goto LAB_10008b3a;
          puVar2 = puVar2 + 1;
          in_stack_00000014 = uVar1;
        } while (in_stack_00000004 != 0x20);
      }
    }
    if ((in_stack_00000018 & 0x10) == 0) goto LAB_10008b96;
    uVar1 = in_stack_00000004;
    if ((in_stack_00000018 & 0x400) == 0) goto LAB_10008be6;
    goto LAB_10008b4e;
  }
LAB_10008b3a:
  if ((in_stack_00000018 & 0x10) != 0) {
    if (((in_stack_00000018 & 0x400) == 0) && (uVar1 = in_stack_00000004, in_stack_00000004 != 0)) {
LAB_10008be6:
      if (((in_stack_00000010 != uVar1) && (in_stack_00000004 = uVar1, uVar1 != in_stack_00000014))
         || (in_stack_00000004 = uVar1 - 1, in_stack_00000004 == 0)) goto LAB_10008b4e;
      if (in_stack_0000000c == 0x10) {
        in_stack_00000004 = uVar1 - 2;
        goto LAB_10008c3c;
      }
LAB_10008b56:
      if (in_stack_0000000c == 2) {
        if (0x1f < in_stack_00000004) goto LAB_10008b96;
        *(undefined1 *)(in_stack_00000000 + in_stack_00000004) = 0x62;
        in_stack_00000004 = in_stack_00000004 + 1;
      }
    }
    else {
LAB_10008b4e:
      if (in_stack_0000000c != 0x10) goto LAB_10008b56;
LAB_10008c3c:
      if ((in_stack_00000018 & 0x20) == 0) {
        if (0x1f < in_stack_00000004) goto LAB_10008b96;
        *(undefined1 *)(in_stack_00000000 + in_stack_00000004) = 0x78;
        in_stack_00000004 = in_stack_00000004 + 1;
      }
      else {
        if (0x1f < in_stack_00000004) goto LAB_10008b96;
        *(undefined1 *)(in_stack_00000000 + in_stack_00000004) = 0x58;
        in_stack_00000004 = in_stack_00000004 + 1;
      }
    }
    if (0x1f < in_stack_00000004) goto LAB_10008b96;
    *(undefined1 *)(in_stack_00000000 + in_stack_00000004) = 0x30;
    in_stack_00000004 = in_stack_00000004 + 1;
  }
  if (in_stack_00000004 < 0x20) {
    if (in_stack_00000008 == '\0') {
      if ((in_stack_00000018 & 4) == 0) {
        if ((in_stack_00000018 & 8) != 0) {
          *(undefined1 *)(in_stack_00000000 + in_stack_00000004) = 0x20;
        }
      }
      else {
        *(undefined1 *)(in_stack_00000000 + in_stack_00000004) = 0x2b;
      }
    }
    else {
      *(undefined1 *)(in_stack_00000000 + in_stack_00000004) = 0x2d;
    }
  }
LAB_10008b96:
  FUN_10008a04();
  return;
}

