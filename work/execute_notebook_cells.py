from pathlib import Path
import json
import matplotlib
matplotlib.use('Agg')
for filename in ['01_data_understanding.ipynb', '02_data_cleaning.ipynb']:
    nb = json.loads((Path.cwd() / filename).read_text(encoding='utf-8'))
    scope = {'display': lambda *args, **kwargs: None}
    for cell in nb['cells']:
        if cell['cell_type'] == 'code':
            exec(''.join(cell['source']), scope)
    print(f'{filename}: executed all code cells')
