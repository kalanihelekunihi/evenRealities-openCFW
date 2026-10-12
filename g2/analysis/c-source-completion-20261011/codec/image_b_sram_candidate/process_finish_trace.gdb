set pagination off
target remote host.docker.internal:12349
break *0x1000d46c
commands
  silent
  printf "entry ctx0c=%u ctx10=%u ctx08=%u\n", *(unsigned int *)($r0+12), *(unsigned int *)($r0+16), *(unsigned int *)($r0+8)
  continue
end
break *0x1000dcd4
commands
  silent
  printf "finish count=%u tail=%u output_offset=%u\n", *(unsigned int *)($sp+0x1c), *(unsigned int *)($sp+0x20), *(unsigned int *)($sp+0x18)
  continue
end
continue
