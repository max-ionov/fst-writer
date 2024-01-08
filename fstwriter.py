from flask import Flask, jsonify, request, render_template, send_file
#from flask_cors import CORS

# import foma
import tempfile
import os
import yaml
import subprocess
import logging
import re

foma_interaction = """
{lexc}
{rules}
apply {direction}

"""

foma_save = """
{lexc}
{rules}
save stack {name}
"""

lexc_template = """
set verbose 0
read lexc {}
define Lexicon;
"""

web_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'web')
config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.yaml')

app = Flask(__name__, static_url_path='', template_folder=web_path, static_folder=web_path)
# cors = CORS(app, resources={'/api/*': {'origins': '*'}})


def tokenize(text):
    words = re.split(r'\W+', text)
    return words if words[-1] else words[:-1]


def convert_response(output_words, input_words):
    if not input_words:
        return ''

    cur_word = None
    output = []

    for line in output_words:
        if input_words and line == input_words[0]:
            cur_word = input_words.pop(0)
            continue
        output.append('{} → {}'.format(cur_word, line))
    return '\n'.join(output)


def save_lexc(lexicon):
    out_file = tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', delete=False)
    out_file.write(lexicon + '\n')

    return out_file.name


def call_foma(command, words=''):
    foma_process = subprocess.Popen([config['foma']['path'], '-q'],
                                    stdin=subprocess.PIPE, stdout=subprocess.PIPE, encoding='utf-8')

    logging.debug('FOMA COMMANDS: {}'.format(command.strip()))
    stdout, stderr = foma_process.communicate(command+words)
    logging.debug('STDERR: {}'.format(stderr))
    logging.debug('STDOUT: {}'.format(stdout.strip()))

    output_lines = stdout.strip().split('\n')
    command_n_lines = command.replace('\n\n', '\n').strip().count('\n') + 1

    return convert_response(output_words=output_lines[command_n_lines+2:], input_words=words.split('\n'))


def response(output, error):
    status = 200 if not error else 400
    return jsonify({'success': error is None, 'outputData': output, 'error': error}), status


@app.route('/')
def main():
    return render_template('fstwriter.html')


@app.route('/api/parse/', methods=['POST'])
@app.route('/api/parse', methods=['POST'])
@app.route('/api/generate/', methods=['POST'])
@app.route('/api/generate', methods=['POST'])
def apply_model():
    directions = {'parse': 'up', 'generate': 'down'}
    rules = request.json.get('rules')
    lexicon = request.json.get('lexicon')
    inp_data = request.json.get('inputData')

    direction = request.base_url.strip('/').split('/')[-1]

    lexc_file = save_lexc(lexicon) if lexicon else None

    results = call_foma(foma_interaction.format(rules=rules,
                                                lexc=lexc_template.format(lexc_file) if lexc_file else '',
                                                direction=directions[direction]), words='\n'.join(tokenize(inp_data)))
    return response(results, 'Syntax error' if results is None else None)


@app.route('/api/save/', methods=['POST'])
@app.route('/api/save', methods=['POST'])
def save_model():
    rules = request.json.get('rules')
    lexicon = request.json.get('lexicon')
    logging.debug(rules)

    lexc_file = save_lexc(lexicon) if lexicon else None
    tmp_model_name = 'model.foma'
    results = call_foma(foma_save.format(rules=rules,
                                         lexc=lexc_template.format(lexc_file) if lexc_file else '',
                                         name=tmp_model_name))

    #if lexc_file:
    #    os.unlink(lexc_file)

    return send_file(tmp_model_name, as_attachment=True) if tmp_model_name else jsonify({'success': False,
                                                                                         'outputData': None,
                                                                                         'error': 'Error creating Foma model'}), 400


if __name__ == '__main__':
    with open(config_path, encoding='utf-8') as inp_file:
        config = yaml.load(inp_file, Loader=yaml.SafeLoader)

    logging.basicConfig(level=logging.INFO)
    app.run(debug=False, host=config['api']['host'], port=config['api']['port'])
