# NNs
Все входные данные хранятся в каталоге ***input_files***.

Все выходные данные, соответственно в каталоге ***output_files***.

Для запуска программы необходимо передать в качестве аргумента командной строки номер задания.

Пример:

    > python nn.py -t 1

Можно также передать дополнительные параметры.

Пример:

    > python nn.py -t 1 --ig ingraph.txt --og outgraph.json

    > python nn.py -t 2 --ig ingraph.txt --og outgraph.json --of outfunction.txt

    > python nn.py -t 3 --ig ingraph.txt --og outgraph.json --op inoperations.txt --of outfunction.txt

Добавлено задание 4.