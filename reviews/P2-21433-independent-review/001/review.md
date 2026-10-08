# Independent review — P2-21433

Status: partial; accepted: false.

Fresh replay passed for the 46-byte range. Regenerated instruction and reference files match the candidate exactly, including tiling and PC-relative references.

The 24-byte frame retains the parent, outer-list pointer, and previous node. The node's next pointer is saved before the status load/helper call. Status 3 passes the outer pointer and current node to the helper; after return, unlinking uses the saved next pointer, either updating the parent head or the previous node link. The previous pointer is not advanced on a removal, so consecutive head/interior matches can be removed. Nonmatching nodes update previous and advance using the saved next pointer.

Helper behavior and the continuation after the empty-list branch are unresolved; review remains partial/unaccepted.
