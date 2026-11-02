from pathlib import Path
import nbformat
from nbclient import NotebookClient

project = Path(r'C:\Users\yatee\Documents\Codex\2026-11-01\project-cardsense-credit-card-customer-churn\outputs\CardSense')
for name in ['01_data_understanding.ipynb', '02_data_cleaning.ipynb']:
    path = project / 'notebooks' / name
    notebook = nbformat.read(path, as_version=4)
    client = NotebookClient(notebook, timeout=300, kernel_name='python3', resources={'metadata': {'path': str(path.parent)}})
    executed = client.execute()
    print(f'Executed {name}: {sum(c.cell_type == "code" for c in executed.cells)} code cells', flush=True)
    for cell in executed.cells:
        if cell.cell_type == 'code':
            for out in cell.get('outputs', []):
                if out.output_type == 'stream':
                    txt = out.text.strip()
                    if txt: print(txt[-600:], flush=True)
