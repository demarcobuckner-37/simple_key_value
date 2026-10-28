from index import Index

def main():
    print("Simple Key-Value Store")

    index = Index()

    with open("data.db", "r") as file:
        for line in file:
            parts = line.strip().split()

            if len(parts) == 3 and parts[0] == "SET":
                index.set(parts[1], parts[2])

    while True:
        command = input()
        parts = command.split()

        if command == "EXIT":
            break

        if parts and parts[0] == "SET":
            if len(parts) == 3:
                index.set(parts[1], parts[2])

                with open("data.db", "a") as file:
                    file.write(f"SET {parts[1]} {parts[2]}\n")
                
                print("Done")

        if parts and parts[0] == "GET":
            if len(parts) == 2:
                record = index.search(parts[1])

                if record is not None:
                    print(record.value)
                else:
                    print("NULL")

if __name__ == "__main__":
    main()