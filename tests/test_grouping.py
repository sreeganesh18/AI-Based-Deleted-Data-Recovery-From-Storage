from reconstruction.grouping import FragmentGrouper


def test_grouping():
    grouper = FragmentGrouper(n_clusters=2)

    # 3 dummy blocks, two mostly zeros, one mostly ones
    block1 = b"\x00" * 512
    block2 = b"\x01" * 512
    block3 = b"\x00" * 512

    groups = grouper.group_fragments([block1, block2, block3])

    # With 3 samples and 2 clusters, we should have 2 groups
    assert len(groups) == 2

    # Convert lists of bytes into lists of lengths for a simple check, since grouping distributes them
    group_sizes = [len(g) for g in groups.values()]
    assert sum(group_sizes) == 3
