# FST Writer

This is a small web application providing a rudimentary web interface wrapping [foma](https://fomafst.github.io/).

## Installation

We recommend using a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

For the application to work, `foma` should be installed.

Host, port for the web interface and the path to `foma` can be configured in the file `config.yaml`.

## Running

Since the application is based on Flask, the easiest way to start FST Writer is by running
```bash
source .venv/bin/activate
python ./fstwriter.py
```

After that, the application should be available at `http://host:port` (default [http://localhost:8080](http://localhost:8080)).

## Usage

The application provides two separate areas to write rules and a lexicon. If lexicon area is not empty, it should be combined with the rules like this:
`Lexicon .o. Rule1 .o. Rule2 ...` in the end of the rules section.

An example of rules and a lexicon based on the official `foma` documentation can be found in this repository in the folder `examples/`.

In order to test the rules, put a list of tokens or a text in the corresponding area and press "→ Apply". This will tokenise the input and output all the possible analyses for each token.

If you want to save the model, use the button "Save". It will create a file `model.foma` in the working directory of the service which can be used with `foma` outside of the service.
