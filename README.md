# Urban Dictionary Word List

Script and sample dataset of all urban dictionary entry names (around 1.4 million total):

```bash
$ head -1000 data/a.data | tail -20
Abanoub
abansion
aba nuckie
ABAP
a bape and a year
Abaphany
Abaqoos
abar
Abarackan
Abarai
Abarai Renji
Abarat
a barbara
Abareh
abarenbou
Abarket
abarkheid
A Barkley
a barlow
a barney
```


## Data
This repo includes a snapshot of all entry names from Urban dictionary taken in May 2016. The lists are found in [`data/`](https://github.com/mattbierner/urban-dictionary-word-list/tree/master/data) and are bucketed by starting letter.

Each entry name is on it's own line in the file.

## Script
The included Python script allows you to download entry names as well in case you want a more up to date snapshot.

``` sh
# download all entries that start with 'a'
$ python main.py a --out "{0}.data"
```

You can also pass in multiple letters:

``` sh
$ python main.py a b c --out "{0}.data"
```

Appends to existing files by default.


## Usage
For reseach purposes. I'm not affiliated with Urban Dictionary.