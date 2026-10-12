set pagination off
target remote host.docker.internal:12349
break *0x1000db5c
commands
  silent
  printf "db5c r10=%u r11=%u ctx0c=%u ctx10=%u\n", $r10, $r11, *(unsigned int *)($r17+12), *(unsigned int *)($r17+16)
  continue
end
break *0x1000dcd4
commands
  silent
  printf "dcd4 count=%u tail=%u r10=%u r11=%u\n", *(unsigned int *)($sp+0x1c), *(unsigned int *)($sp+0x20), $r10, $r11
  continue
end
continue
