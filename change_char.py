from sys import argv

if len(argv) == 3:
    curr_char = argv[1]
    new_char = argv[2]
    tiles = []
    print(f"Cambiando {curr_char} por {new_char} ")
    with open("material/map.txt") as file_:
        for line in file_:
            new_line = []
            for char in line:
                if char == curr_char:
                    new_line.append(new_char)
                else:
                    new_line.append(char)
            tiles.append(new_line)



    with open("material/map.txt", "w") as file_:
        for line in tiles:
            for char in line:
                file_.write(char)
else:
    print("Error")



