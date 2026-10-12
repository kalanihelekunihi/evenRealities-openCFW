.text
.global channel_notify
channel_notify:
ld r1,[r0,2796]
cmp_s r1,0
jeq_s [blink]
ldb_s r0,[r0,1]
j_s [r1]
.global phy_notify
phy_notify:
ld r1,[r0,2800]
cmp_s r1,0
jeq_s [blink]
ldb_s r0,[r0,1]
j_s [r1]
