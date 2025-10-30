# generate_latency_report.py
# Reads tts_results.csv and produces latency_report.csv and two PDFs (light + dark)
import os, csv, time, platform, psutil, math
from collections import defaultdict
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import pandas as pd

CSV = os.environ.get('TTS_CSV_OUTPUT', 'tts_results.csv')

def read_results():
    if not os.path.exists(CSV):
        print('No results CSV found:', CSV)
        return []
    rows = []
    with open(CSV, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for r in reader:
            rows.append(r)
    return rows

def to_float(x):
    try:
        return float(x)
    except:
        return None

def summarize(rows):
    # group by provider + mode (note)
    groups = {}
    for r in rows:
        provider = r.get('provider','')
        note = r.get('note','').strip() or 'unknown'
        key = (provider, note)
        if key not in groups:
            groups[key] = {'latencies': [], 'sizes': [], 'counts':0, 'last_ts':None, 'text_len':0}
        lat = to_float(r.get('request_latency_s',''))
        size = to_float(r.get('file_size_kb',''))
        if lat is not None:
            groups[key]['latencies'].append(lat)
        if size is not None:
            groups[key]['sizes'].append(size)
        groups[key]['counts'] += 1
        groups[key]['last_ts'] = r.get('timestamp') or groups[key]['last_ts']
        tl = r.get('text_len_chars','')
        try:
            groups[key]['text_len'] = int(tl) if tl else groups[key]['text_len']
        except:
            pass
    # build summary rows
    summary = []
    for (provider,note), v in groups.items():
        lat_list = v['latencies']
        avg = sum(lat_list)/len(lat_list) if lat_list else None
        mn = min(lat_list) if lat_list else None
        mx = max(lat_list) if lat_list else None
        last_size = v['sizes'][-1] if v['sizes'] else None
        words = (v['text_len']/5.0) if v['text_len'] else None
        wps = (words / avg) if (words and avg and avg>0) else None
        summary.append({
            'provider': provider,
            'mode': note,
            'avg_latency_s': round(avg,4) if avg is not None else '',
            'min_latency_s': round(mn,4) if mn is not None else '',
            'max_latency_s': round(mx,4) if mx is not None else '',
            'last_file_size_kb': round(last_size,1) if last_size is not None else '',
            'words_per_sec': round(wps,3) if wps is not None else '',
            'runs': v['counts'],
            'last_timestamp': v['last_ts'] or ''
        })
    return summary

def write_csv(summary, out='latency_report.csv'):
    df = pd.DataFrame(summary)
    df.to_csv(out, index=False)
    print('Wrote', out)
    return df

def system_info():
    info = {
        'platform': platform.platform(),
        'cpu_count': psutil.cpu_count(logical=True),
        'memory_total_gb': round(psutil.virtual_memory().total / (1024**3),2),
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
    }
    return info

def make_pdf(df, out_pdf='latency_report_light.pdf', dark=False):
    plt.close('all')
    if dark:
        plt.style.use('dark_background')
    else:
        plt.style.use('default')
    # create bar chart for avg latency
    fig, ax = plt.subplots(figsize=(10,6))
    labels = df['provider'] + ' (' + df['mode'] + ')'
    vals = pd.to_numeric(df['avg_latency_s'], errors='coerce').fillna(0.0)
    ax.bar(labels, vals)
    ax.set_ylabel('Avg Latency (s)')
    ax.set_title('TTS Average Latency per Provider (mode)')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    # save table as another page
    with PdfPages(out_pdf) as pdf:
        pdf.savefig(fig)
        plt.close(fig)
        # table page
        fig2, ax2 = plt.subplots(figsize=(10,6))
        ax2.axis('off')
        table = ax2.table(cellText=df.values, colLabels=df.columns, loc='center', cellLoc='center')
        table.auto_set_font_size(False)
        table.set_fontsize(8)
        table.scale(1, 1.2)
        pdf.savefig(fig2)
        plt.close(fig2)
    print('Wrote', out_pdf)

def main():
    rows = read_results()
    summary = summarize(rows)
    if not summary:
        print('No data to summarize. Exiting.')
        return
    df = write_csv(summary)
    info = system_info()
    print('System info:', info)
    make_pdf(df, out_pdf='latency_report_light.pdf', dark=False)
    make_pdf(df, out_pdf='latency_report_dark.pdf', dark=True)
    print('Reports generated.')

if __name__ == '__main__':
    main()
