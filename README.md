# Urban Dictionary Dictionary

Script and sample dataset of all urban dictionary words (around 2.7 million total).
Also provides code to fetch definitions and turn them into a `.dict.dz` file,
for use with `dictd(8)`.

## Data

This repo includes a snapshot of all entry names from Urban dictionary taken in
December 2022. The lists are found in `data/` and are bucketed by starting
letter. Each entry name is on its own line in the file.

It also has an abbreviated list of the definitions, in the `-c5` dict format.

## To Get a `dict.dz`

Requirements:

- Python 3 (For getting words; I used 3.11.1)
- Node (For getting definitions; I used v19.3.0)
- dictfmt and dictzip (For building the dictionary; I used 1.13.1)

```bash
# Update to latest wordlists (optional)
python3 -m venv .venv/
source .venv/bin/activate
pip install -r requirements.txt
./main.py --remove-dead # This step takes a while

# Update to latest definitions (optional)
# Tweak the constraints if the dict size is too big.
# Try and get it right the first time though, there's no caching yet.
# 50 for top and 10 for any yields a ~115mb file
./get_all_defs.sh

# Check for an acceptable error rate (only do if you ran the above two)
cat data/*.err

# If things are acceptable:
./build_dict.sh
```

Now, if you're running a linux box, the next step will look something like this:

```bash
mv ud.dict.dz /usr/share/dictd
mv ud.index /usr/share/dictd
dictdconfig -w
systemctl restart dictd.service
```

For macOS, instructions are forthcoming, nobody seems to have packaged homebrew
`dictd` nicely... If you just want the info though, you can probably use
[pyglossary][damnapple] to convert it to something that Dictionary.app can read.

For reference though, if I don't finish that, this should be a place to start:

`dictd.conf`

```conf
database ud {
    data "/full/path/to/ud.dict.dz"
    index "/full/path/to/ud.index"
}
```

```bash
brew install dict

# Terminal 1
dictd --pid-file /tmp/dict.pid -d nodetach --config dictd.conf --verbose

# Terminal 2
dict "sussy baka"
```

## Next Steps

- Add caching, to be nicer to UD API and make development much faster
- Add other dictionary outputs
  - This is preferable to just converting, because we can do more metadata
- Figure out how to make homebrew service for dictd
- Package *this* bad boy for homebrew
- Set up GitHub Actions to run a new release monthly
- More options for creating the dict, like:
  - Maximum number of definitions
  - Only including ascii
  - See if casefolding is necessary

[damnapple]: https://apple.stackexchange.com/questions/41894/spanish-to-english-and-english-to-spanish-dictionary-for-dictionary-app/119166#119166
