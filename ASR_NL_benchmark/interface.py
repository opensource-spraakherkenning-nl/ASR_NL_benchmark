from flask import Flask
from flask import render_template, request, redirect
import os
import pandas
from threading import Thread
import pathlib


from ASR_NL_benchmark import pipeline

app = Flask(__name__)
app.template_folder = os.path.join(pathlib.Path(__file__).parent, 'templates')

print(os.path.join(pathlib.Path(__file__).parent, 'templates'))


@app.route('/', methods=['GET', 'POST'])
def upload_page():
    if request.method == 'POST':
        hyp = os.path.join(os.path.sep,'input',request.form.get('hyp'))
        ref = os.path.join(os.path.sep,'input',request.form.get('ref'))
        kind = request.form.get('kind')
        global benchmarking
        benchmarking = pipeline.Pipeline(hyp, 'ctm', ref, 'stm', kind)
        Thread(target=benchmarking.main).start()
        return redirect(f'/progress?ref={ref}&hyp={hyp}')
    return render_template('select_files.html')


@app.route('/progress', methods=['GET','POST'])
def progress():
    global benchmarking
    done = benchmarking.progress
    failed = benchmarking.failed
    print('reloaded')
    print(done)
    if done == 1.0:
        return redirect(f'/results')
    else:
        return render_template('progress.html', done=done*100, failed=failed)


@app.route('/results', methods=['GET','POST'])
def results():

    print('loading results')
    return render_template('results.html', dfs=get_dfs())


def get_dfs():
    dfs = {}


    category_folders = [f.path for f in os.scandir(os.path.join(os.path.sep,'input','results','')) if
                        f.is_file() and f.name.startswith('results_category') and f.name.endswith('.csv')]


    for folder in category_folders:
        index = ('.').join(('_').join(folder.split('_')[2:]).split('.')[:-1])
        dfs[index] = {}
        dfs[index]['cat']= {}
        dfs[index]['cat']['agregation'] = 'Per categorie'
        dfs[index]['cat']['df'] = pandas.read_csv(folder)
        dfs[index]['cat']['kind'] = dfs[index]['cat']['df']['kind'].iloc[0]
        dfs[index]['cat']['df'] = dfs[index]['cat']['df'].drop('kind',1)
        dfs[index]['cat']['df']['product'] = dfs[index]['cat']['df']['WER'] * dfs[index]['cat']['df']['ref_words']
        dfs[index]['cat']['wer'] = dfs[index]['cat']['df']['product'].sum() / dfs[index]['cat']['df']['ref_words'].sum()
        dfs[index]['cat']['df'] = dfs[index]['cat']['df'].drop('product',1)
        print(dfs)

    speaker_folders = [f.path for f in os.scandir(os.path.join(os.path.sep,'input','results','')) if
                       f.is_file() and f.name.startswith('results_speaker') and f.name.endswith('.csv')]

    for folder in speaker_folders:
        index = ('.').join(('_').join(folder.split('_')[2:]).split('.')[:-1])
        try:
            dfs[index]['spk'] = {}
        except KeyError:
            dfs[index] = {}
            dfs[index]['spk']= {}
        dfs[index]['spk']['agregation'] = 'Per spreker'
        dfs[index]['spk']['df'] = pandas.read_csv(folder)
        dfs[index]['spk']['kind'] = dfs[index]['spk']['df']['kind'].iloc[0]
        dfs[index]['spk']['df'] = dfs[index]['spk']['df'].drop('kind', 1)

        dfs[index]['spk']['df']['product'] = dfs[index]['spk']['df']['WER'] * dfs[index]['spk']['df'][
            'ref_words']
        dfs[index]['spk']['wer'] = dfs[index]['spk']['df']['product'].sum() / dfs[index]['spk']['df']['ref_words'].sum()
        dfs[index]['spk']['df'] = dfs[index]['spk']['df'].drop('product', 1)
        print(dfs)

    return dfs

def main():
    print('Interface active')
    app.run(port=5000, host='0.0.0.0')

if __name__ == '__main__':
    app.run(port=5000)


