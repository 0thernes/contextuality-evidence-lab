"""Publication figures generated exclusively from recorded experiment results."""
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
data = json.loads((ROOT / 'results/experiment.json').read_text())
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 9, 'svg.fonttype': 'none'})
fig, axes = plt.subplots(1, 2, figsize=(10.2, 3.5), gridspec_kw={'width_ratios':[1.7, 1]})
for report, label, color in (
    (data['classical_attack']['naive'], 'Classical: naive calibration', '#bf4d38'),
    (data['classical_attack']['protected'], 'Classical: corrected calibration', '#087f76'),
    (data['moonlab_readout'], 'Moonlab + noise: corrected', '#5575be')):
    axes[0].plot([p['trial'] for p in report['trace']], [p['log10_capital'] for p in report['trace']], label=label, color=color, linewidth=1.6)
axes[0].axhline(2, color='#222222', linestyle='--', linewidth=.8, label='1% threshold')
axes[0].set(xlabel='Trial', ylabel='log10 evidence', title='A. Recorded sequential traces')
axes[0].legend(fontsize=7, loc='lower left')
risks = [100 * data['exact_iid_hitting'][k]['decimal'] for k in ('naive', 'protected')]
axes[1].bar(['Naive', 'Corrected'], risks, color=['#bf4d38', '#087f76'], width=.55)
axes[1].axhline(1, color='#222222', linestyle='--', linewidth=.8)
axes[1].set(yscale='log', ylim=(.4, 200), ylabel='False rejection probability (%)', title='B. Exact classical risk by trial 1,000')
for i, value in enumerate(risks):
    axes[1].text(i, value * 1.13, f'{value:.3f}%', ha='center', fontsize=9)
for axis in axes:
    axis.spines[['top','right']].set_visible(False)
    axis.grid(axis='y', alpha=.15)
fig.tight_layout(pad=1.5)
for folder in (ROOT / 'paper/figures', ROOT / 'docs/paper/figures'):
    folder.mkdir(parents=True, exist_ok=True)
    fig.savefig(folder / 'evidence.svg', bbox_inches='tight')
    fig.savefig(folder / 'evidence.png', dpi=180, bbox_inches='tight')
fig.savefig(ROOT / 'paper/figures/evidence.pdf', bbox_inches='tight')
print('Saved evidence figure (SVG, PNG, PDF).')
