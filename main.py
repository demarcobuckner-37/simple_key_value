import os
from index import Index
import time
import copy

def main():
    print("Simple Key-Value Store")

    index = Index()

    in_transaction = False
    transaction_index = None
    transaction_log = []

    # Recover saved data when the program starts
    if not os.path.exists("data.db"):
        open("data.db", "a").close()
    
    with open("data.db", "r") as file:
        for line in file:
            parts = line.strip().split()

            if len(parts) == 3 and parts[0] == "SET":
                index.set(parts[1], parts[2])

            elif len(parts) == 4 and parts[0] == "HSET":
                index.hset(parts[1], parts[2], parts[3])

            elif len(parts) == 3 and parts[0] == "LPUSH":
                index.lpush(parts[1], parts[2])

            elif len(parts) == 3 and parts[0] == "RPUSH":
                index.rpush(parts[1], parts[2])

            elif len(parts) == 1 and parts[0] == "FLUSHDB":
                index.flushdb()

            elif len(parts) == 2 and parts[0] == "DEL":
                index.delete(parts[1])

            elif len(parts) == 3 and parts[0] == "EXPIRE":
                record = index.search(parts[1])

                if record is not None:
                    record.expires_at = float(parts[2])

    while True:
        command = input()
        parts = command.split()

        active_index = transaction_index if in_transaction else index

        if command == "BEGIN":
            if not in_transaction:
                transaction_index = copy.deepcopy(index)
                transaction_log = []
                in_transaction = True
                print("OK")
            else:
                print("ERROR")
            continue

        if command == "COMMIT":
            if in_transaction:
                with open("data.db", "a") as file:
                    file.writelines(transaction_log)

                index = transaction_index
                transaction_index = None
                transaction_log = []
                in_transaction = False

                print("OK")
            else:
                print("ERROR")
            continue

        if command == "ABORT":
            if in_transaction:
                transaction_index = None
                transaction_log = []
                in_transaction = False

                print("OK")
            else:
                print("ERROR")
            continue

        if command == "EXIT":
            break

        if parts and parts[0] == "SET":
            if len(parts) == 3:
                active_index.set(parts[1], parts[2])

                log_entry = f"SET {parts[1]} {parts[2]}\n"

                if in_transaction:
                    transaction_log.append(log_entry)
                else:
                    with open("data.db", "a") as file:
                        file.write(log_entry)

                print("Done")

        if parts and parts[0] == "GET":
            if len(parts) == 2:
                record = active_index.search(parts[1])

                if record is not None:
                    print(record.value)
                else:
                    print("NULL")

        if parts and parts[0] == "DEL":
            if len(parts) == 2:
                deleted = active_index.delete(parts[1])

                if deleted:
                    log_entry = f"DEL {parts[1]}\n"

                    if in_transaction:
                        transaction_log.append(log_entry)
                    else:
                        with open("data.db", "a") as file:
                            file.write(log_entry)

                    print("1")
                else:
                    print("0")

        if parts and parts[0] == "EXISTS":
            if len(parts) == 2:
                record = active_index.search(parts[1])

                if record is not None:
                    print("1")
                else:
                    print("0")

        if parts and parts[0] == "HSET":
            if len(parts) == 4:
                active_index.hset(parts[1], parts[2], parts[3])

                log_entry = f"HSET {parts[1]} {parts[2]} {parts[3]}\n"

                if in_transaction:
                    transaction_log.append(log_entry)
                else:
                    with open("data.db", "a") as file:
                        file.write(log_entry)

                print("OK")

        if parts and parts[0] == "HGET":
            if len(parts) == 3:
                value = active_index.hget(parts[1], parts[2])

                if value is not None:
                    print(value)
                else:
                    print("NULL")

        if parts and parts[0] == "HGETALL":
            if len(parts) == 2:
                fields = active_index.hgetall(parts[1])

                for hash_field in fields:
                    print(hash_field.field, hash_field.value)

        if parts and parts[0] == "LPUSH":
            if len(parts) == 3:
                active_index.lpush(parts[1], parts[2])

                log_entry = f"LPUSH {parts[1]} {parts[2]}\n"

                if in_transaction:
                    transaction_log.append(log_entry)
                else:
                    with open("data.db", "a") as file:
                        file.write(log_entry)

                print("OK")

        if parts and parts[0] == "RPUSH":
            if len(parts) == 3:
                active_index.rpush(parts[1], parts[2])

                log_entry = f"RPUSH {parts[1]} {parts[2]}\n"

                if in_transaction:
                    transaction_log.append(log_entry)
                else:
                    with open("data.db", "a") as file:
                        file.write(log_entry)

                print("OK")

        if parts and parts[0] == "LRANGE":
            if len(parts) == 4:
                try:
                    start = int(parts[2])
                    end = int(parts[3])
                    values = active_index.lrange(parts[1], start, end)

                    for value in values:
                        print(value)

                except ValueError:
                    print("ERROR")

        if command == "FLUSHDB":
            active_index.flushdb()

            log_entry = "FLUSHDB\n"

            if in_transaction:
                transaction_log.append(log_entry)
            else:
                with open("data.db", "a") as file:
                    file.write(log_entry)

            print("OK")

        if parts and parts[0] == "MSET":
            if len(parts) >= 3 and len(parts) % 2 == 1:
                for i in range(1, len(parts), 2):
                    active_index.set(parts[i], parts[i + 1])

                    log_entry = f"SET {parts[i]} {parts[i + 1]}\n"

                    if in_transaction:
                        transaction_log.append(log_entry)
                    else:
                        with open("data.db", "a") as file:
                            file.write(log_entry)

                print("OK")

        if parts and parts[0] == "MGET":
            if len(parts) >= 2:
                for key in parts[1:]:
                    record = active_index.search(key)

                    if record is not None:
                        print(record.value)
                    else:
                        print("NULL")

        if parts and parts[0] == "INCR":
            if len(parts) == 2:
                record = active_index.search(parts[1])

                if record is not None:
                    try:
                        value = int(record.value)
                        new_value = value + 1

                        active_index.set(parts[1], str(new_value))

                        log_entry = f"SET {parts[1]} {new_value}\n"

                        if in_transaction:
                            transaction_log.append(log_entry)
                        else:
                            with open("data.db", "a") as file:
                                file.write(log_entry)

                        print(str(new_value))

                    except (ValueError, TypeError):
                        print("ERROR")
                else:
                    print("ERROR")

        if parts and parts[0] == "DECR":
            if len(parts) == 2:
                record = active_index.search(parts[1])

                if record is not None:
                    try:
                        value = int(record.value)
                        new_value = value - 1

                        active_index.set(parts[1], str(new_value))

                        log_entry = f"SET {parts[1]} {new_value}\n"

                        if in_transaction:
                            transaction_log.append(log_entry)
                        else:
                            with open("data.db", "a") as file:
                                file.write(log_entry)

                        print(str(new_value))

                    except (ValueError, TypeError):
                        print("ERROR")
                else:
                    print("ERROR")

        if parts and parts[0] == "EXPIRE":
            if len(parts) == 3:
                record = active_index.search(parts[1])

                if record is not None:
                    try:
                        expires_in = int(parts[2])
                        record.expires_at = time.time() + expires_in

                        log_entry = f"EXPIRE {parts[1]} {record.expires_at}\n"

                        if in_transaction:
                            transaction_log.append(log_entry)
                        else:
                            with open("data.db", "a") as file:
                                file.write(log_entry)

                        print("OK")

                    except ValueError:
                        print("ERROR")
                else:
                    print("ERROR")

        if parts and parts[0] == "TTL":
            if len(parts) == 2:
                record = active_index.search(parts[1])

                if record is not None:
                    if record.expires_at is not None:
                        time_left = record.expires_at - time.time()
                        print(int(time_left))
                    else:
                        print("-1")
                else:
                    print("-2")

        if parts and parts[0] == "RANGE":
            if len(parts) == 3:
                results = active_index.range_query(parts[1], parts[2])

                for record in results:
                    print(f"{record.key} {record.value}")

if __name__ == "__main__":
    main()
