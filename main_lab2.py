from lab2.ospf import simulate

if __name__ == '__main__':
    linear = {
        "nodes": [0, 1, 2, 3, 4],
        "neighbours": [[1], [0, 2], [1, 3], [2, 4], [3]]
    }
    star = {
        "nodes": [0, 1, 2, 3, 4],
        "neighbours": [[2], [2], [0, 1, 3, 4], [2], [2]]
    }
    circle = {
        "nodes": [0, 1, 2, 3, 4],
        "neighbours": [[1], [2], [3], [4], [0]]
    }
    simulate(star)
