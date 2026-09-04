/* SPDX-License-Identifier: MIT */
#ifndef OPEN_CFW_AT_FS_H
#define OPEN_CFW_AT_FS_H

int open_cfw_at_fs_remove(const char *path);
int open_cfw_at_fs_list_recursive(const char *path);
int open_cfw_at_fs_list(const char *path);
int open_cfw_at_fs_mkdir(const char *path);

#endif
