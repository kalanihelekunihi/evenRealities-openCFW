ENTRY(native_fs_read)
SECTIONS {
.body_read 0x4c8ff0 : {*(.body_read)}
.body_write 0x4c900c : {*(.body_write)}
.body_seek 0x4c9028 : {*(.body_seek)}
.body_tell 0x4c9064 : {*(.body_tell)}
.body_close 0x4c8fd8 : {*(.body_close)}
.body_dir_close 0x4c90e4 : {*(.body_dir_close)}
}
