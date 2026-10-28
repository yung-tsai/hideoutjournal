"""Build Hideout: runs src/assemble.py (which runs every pass), then wraps the result into index.html for Vercel.
   python3 build.py          (needs Python 3 with Pillow: pip install pillow)"""
import os, re, subprocess, sys, shutil
ROOT = os.path.dirname(os.path.abspath(__file__))
os.makedirs(os.path.join(ROOT, 'build'), exist_ok=True)
subprocess.run([sys.executable, os.path.join(ROOT, 'src', 'assemble.py')], check=True)
frag = open(os.path.join(ROOT, 'build', 'fragment.html')).read()

HEAD = '''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="theme-color" content="#fbfaf7">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="default">
<meta name="description" content="A calm journal by a stream.">
</head>
<body>
'''
open(os.path.join(ROOT, 'index.html'), 'w').write(HEAD + frag + '\n</body>\n</html>\n')

# syntax check the script, if Node is installed
if shutil.which('node'):
    js = '\n'.join(re.findall(r'<script>(.*?)</script>', frag, re.S))
    p = os.path.join(ROOT, 'build', 'check.js'); open(p, 'w').write(js)
    r = subprocess.run(['node', '--check', p], capture_output=True, text=True)
    if r.returncode: sys.exit('JavaScript syntax error:\n' + r.stderr[-2000:])
    print('script syntax ok')
print('built index.html', round(os.path.getsize(os.path.join(ROOT, 'index.html')) / 1e6, 1), 'MB')
