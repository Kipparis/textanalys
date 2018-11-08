In [3]: pwd
Out[3]: '/home/kip/files/textanalys'

In [4]: path = '/home/kip/files/textanalys'

In [5]: import sys

In [6]: sys.path.insert(0, path)  
  
Создаём унограммы, биграммы как вектора признаков  
Используем дельта tf-idf как классификатор в перемешку с уже готовым словарём  
  
https://habr.com/post/149605/ -- основа  
http://nlpx.net/archives/57 -- tf-idf