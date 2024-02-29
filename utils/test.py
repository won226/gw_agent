if __name__ == "__main__":
    a = ['1', '2', '3', '4', '7', '8']
    b = ['3', '4', '8']

    delete_values = []
    delete_items = []
    deleted = False
    first = True
    total_deletion = 0
    deletions = 0

    for item in a:
        if item not in b:
            delete_values.append(item)
            total_deletion += 1

    while True:
        if deletions >= total_deletion:
            break
        for index in range(0, len(a)):
            if a[index] in delete_values:
                delete_items.append(a.pop(index))
                deletions += 1
                break
    print(a)
    print(b)
    print(delete_items)




