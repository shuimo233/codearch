#!/usr/bin/env python3
"""
CodeArch SVG Generator — Zero-dependency architecture diagram from system-data.json.
Usage: python generate-arch.py system-data.json [output.svg]
"""
import json, sys, math, os

# ── Color Palette ──
LAYER_COLORS = {
    'frontend': {'bg': '#f5eef8', 'stroke': '#8e44ad', 'text': '#4a235a', 'label': '🟣 Frontend'},
    'entry':    {'bg': '#d6eaf8', 'stroke': '#2e86c1', 'text': '#1a5276', 'label': '🔵 Entry'},
    'service':  {'bg': '#d5f5e3', 'stroke': '#27ae60', 'text': '#1e8449', 'label': '🟢 Service'},
    'data':     {'bg': '#fef9e7', 'stroke': '#f39c12', 'text': '#9a7d0a', 'label': '🟡 Data'},
    'infra':    {'bg': '#fdebd0', 'stroke': '#e67e22', 'text': '#6e2f1a', 'label': '⚙️ Infra'},
    'external': {'bg': '#fdebd0', 'stroke': '#e67e22', 'text': '#6e2f1a', 'label': '🔗 External'},
    'job':      {'bg': '#e8f8f5', 'stroke': '#1abc9c', 'text': '#0e6251', 'label': '⏰ Job'},
    'event':    {'bg': '#fdedec', 'stroke': '#e74c3c', 'text': '#7b241c', 'label': '📡 Event'},
}

TYPE_COLORS = {
    'Controller': '#3498db', 'Service': '#27ae60', 'Repository': '#f39c12',
    'Entity': '#9b59b6', 'Config': '#7f8c8d', 'Client': '#e67e22',
    'Consumer': '#e74c3c', 'Job': '#16a085', 'Router': '#2980b9',
    'View': '#8e44ad', 'Handler': '#3498db', 'Component': '#1abc9c',
}

LAYER_ORDER = ['frontend', 'entry', 'service', 'data', 'infra', 'external', 'job', 'event']

# ── Layout Constants ──
NODE_W, NODE_H = 170, 60
NODE_GAP_X, NODE_GAP_Y = 20, 16
LAYER_PAD = 40
MARGIN = 30
HEADER_H = 32
CANVAS_W = 1400

def esc(s):
    return str(s).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')

def read_data(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def build_svg(data):
    comps = data.get('components', [])
    deps = data.get('dependencies', [])

    # Group by layer
    by_layer = {}
    for c in comps:
        l = c.get('layer', 'service')
        by_layer.setdefault(l, []).append(c)

    # Calculate layout
    layers_used = [l for l in LAYER_ORDER if l in by_layer]
    node_positions = {}  # id -> (x, y, w, h)

    total_h = MARGIN
    layer_bounds = []

    for layer_name in layers_used:
        items = by_layer[layer_name]
        cols = max(1, int((CANVAS_W - 2 * MARGIN) / (NODE_W + NODE_GAP_X)))
        rows = math.ceil(len(items) / cols)

        layer_y = total_h
        layer_h = HEADER_H + rows * (NODE_H + NODE_GAP_Y) + LAYER_PAD
        layer_bounds.append((layer_name, layer_y, layer_h))

        content_y = layer_y + HEADER_H + 8
        for i, comp in enumerate(items):
            col = i % cols
            row = i // cols
            x = MARGIN + col * (NODE_W + NODE_GAP_X)
            y = content_y + row * (NODE_H + NODE_GAP_Y)
            node_positions[comp['id']] = (x, y, NODE_W, NODE_H)

        total_h = layer_y + layer_h

    total_h += MARGIN
    svg_w = CANVAS_W

    # Build SVG
    lines = []
    lines.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {svg_w} {total_h}" width="100%" height="100%">')
    lines.append('<defs>')

    # Arrow marker
    for color in ['#bdc3c7', '#3498db']:
        lines.append(f'<marker id="arrow-{color[1:]}" markerWidth="8" markerHeight="6" refX="8" refY="3" orient="auto">')
        lines.append(f'  <path d="M0,0 L8,3 L0,6 Z" fill="{color}"/>')
        lines.append(f'</marker>')

    # Shadow filter
    lines.append('<filter id="shadow"><feDropShadow dx="1" dy="2" stdDeviation="2" flood-opacity="0.1"/></filter>')
    lines.append('</defs>')

    # Background
    lines.append(f'<rect width="{svg_w}" height="{total_h}" fill="#f0f4f8"/>')

    # Draw layers
    for layer_name, ly, lh in layer_bounds:
        cfg = LAYER_COLORS.get(layer_name, LAYER_COLORS['service'])
        lines.append(f'<rect x="8" y="{ly}" width="{svg_w-16}" height="{lh}" rx="8" fill="{cfg["bg"]}" stroke="{cfg["stroke"]}" stroke-width="1.5" opacity="0.3"/>')
        # Layer header
        label = cfg.get('label', layer_name)
        count = len(by_layer[layer_name])
        lines.append(f'<text x="20" y="{ly + 22}" font-size="13" font-weight="700" fill="{cfg["text"]}" font-family="system-ui,sans-serif">{label} ({count})</text>')

    # Draw dependency edges first (behind nodes)
    dep_by_from = {}
    for d in deps:
        dep_by_from.setdefault(d['from'], []).append(d)

    for dep in deps:
        fid = dep['from']
        tid = dep['to']
        if fid not in node_positions or tid not in node_positions:
            continue
        x1, y1, w1, h1 = node_positions[fid]
        x2, y2, w2, h2 = node_positions[tid]

        # Start from bottom center of source, end at top center of target
        sx, sy = x1 + w1/2, y1 + h1
        ex, ey = x2 + w2/2, y2

        # Curved path
        mid_y = (sy + ey) / 2
        color = '#bdc3c7'
        dash = ''
        if dep.get('type') in ('uses', 'stores'):
            dash = 'stroke-dasharray="5,4"'

        lines.append(f'<path d="M{sx},{sy} C{sx},{mid_y} {ex},{mid_y} {ex},{ey}" '
                     f'fill="none" stroke="{color}" stroke-width="1.5" {dash} '
                     f'marker-end="url(#arrow-bdc3c7)" opacity="0.6"/>')

    # Draw nodes
    for comp_id, (x, y, w, h) in node_positions.items():
        comp = next((c for c in comps if c['id'] == comp_id), None)
        if not comp:
            continue
        layer = comp.get('layer', 'service')
        cfg = LAYER_COLORS.get(layer, LAYER_COLORS['service'])
        type_color = TYPE_COLORS.get(comp.get('type', ''), '#95a5a6')

        # Node rect
        rx = 6
        lines.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" '
                     f'fill="white" stroke="{cfg["stroke"]}" stroke-width="1.5" '
                     f'filter="url(#shadow)"/>')
        # Left color bar
        lines.append(f'<rect x="{x}" y="{y}" width="4" height="{h}" rx="2" fill="{type_color}"/>')

        # Type tag
        ctype = comp.get('type', '')
        lines.append(f'<text x="{x+10}" y="{y+16}" font-size="9" fill="#95a5a6" '
                     f'font-family="system-ui,sans-serif" font-weight="600">{esc(ctype)}</text>')

        # Name
        name = comp.get('name', comp_id)
        if len(name) > 22:
            name = name[:20] + '..'
        lines.append(f'<text x="{x+10}" y="{y+34}" font-size="13" fill="#2c3e50" '
                     f'font-family="system-ui,sans-serif" font-weight="600">{esc(name)}</text>')

        # Routes badge
        routes = comp.get('routes', [])
        if routes:
            rtext = f'{len(routes)} API' if len(routes) > 1 else routes[0].get('path', '')[:18]
            lines.append(f'<text x="{x+10}" y="{y+50}" font-size="10" fill="{type_color}" '
                         f'font-family="monospace">{esc(rtext)}</text>')

        # Domain badge
        domain = comp.get('domain', '')
        if domain:
            lines.append(f'<rect x="{x+w-60}" y="{y+4}" width="52" height="16" rx="8" '
                         f'fill="{cfg["bg"]}" stroke="{cfg["stroke"]}" stroke-width="1"/>')
            lines.append(f'<text x="{x+w-34}" y="{y+16}" font-size="9" fill="{cfg["text"]}" '
                         f'font-family="system-ui,sans-serif" text-anchor="middle">{esc(domain)}</text>')

    # Title
    meta = data.get('meta', {})
    title = f'{meta.get("projectName", "Project")} — Architecture ({meta.get("nodeCount", 0)} components)'
    lines.append(f'<text x="{svg_w/2}" y="{total_h-10}" font-size="11" fill="#95a5a6" '
                 f'font-family="system-ui,sans-serif" text-anchor="middle">Generated by CodeArch · {meta.get("generatedAt", "")}</text>')

    lines.append('</svg>')
    return '\n'.join(lines), svg_w, total_h

def main():
    if len(sys.argv) < 2:
        print("Usage: python generate-arch.py system-data.json [output.svg]")
        sys.exit(1)

    input_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else input_path.replace('.json', '.svg')

    data = read_data(input_path)
    svg, w, h = build_svg(data)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(svg)

    print(f"[OK] Architecture SVG generated: {output_path}")
    print(f"     Size: {w}x{h} px, {len(svg)} bytes")

    # Also generate HTML wrapper with interactive features
    html_path = output_path.replace('.svg', '.html')
    generate_html(data, svg, html_path)

def generate_html(data, svg_content, html_path):
    """Generate an interactive HTML wrapper around the SVG"""
    meta = data.get('meta', {})
    comps = data.get('components', [])

    comp_index = {c['id']: c for c in comps}

    # Build a simple component index for hover tooltips
    comp_json = json.dumps({c['id']: {'name': c.get('name',''), 'type': c.get('type',''),
                          'layer': c.get('layer',''), 'domain': c.get('domain',''),
                          'file': c.get('file',''), 'routes': c.get('routes',[])}
                          for c in comps}, ensure_ascii=False)

    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>CodeArch — {esc(meta.get('projectName', 'Architecture'))}</title>
<style>
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{ font-family:system-ui,'PingFang SC','Microsoft YaHei',sans-serif; background:#f0f4f8; color:#2c3e50; }}
.header {{ background:#fff; padding:12px 20px; border-bottom:1px solid #dde3ec; display:flex; gap:12px; align-items:center; }}
.header h1 {{ font-size:16px; color:#3498db; }}
.header .meta {{ font-size:11px; color:#95a5a6; margin-left:auto; }}
.toolbar {{ display:flex; gap:6px; align-items:center; }}
.toolbar button {{ padding:5px 12px; border:1px solid #dde3ec; border-radius:6px; background:#fff; cursor:pointer; font-size:12px; }}
.toolbar button:hover {{ border-color:#3498db; color:#3498db; }}
.svg-wrap {{ overflow:auto; height:calc(100vh - 60px); padding:20px; }}
.svg-wrap svg {{ min-width:100%; }}
.tooltip {{ position:fixed; background:#2c3e50; color:#fff; padding:8px 14px; border-radius:8px; font-size:12px; pointer-events:none; opacity:0; transition:opacity 0.15s; z-index:100; max-width:300px; }}
.tooltip.show {{ opacity:1; }}
.tooltip .tt-name {{ font-weight:700; font-size:13px; margin-bottom:4px; }}
.tooltip .tt-meta {{ color:#bdc3c7; font-size:10px; }}
</style>
</head>
<body>
<div class="header">
    <h1>📘 {esc(meta.get('projectName', 'Architecture'))}</h1>
    <div class="toolbar">
        <button onclick="zoomIn()">+ 放大</button>
        <button onclick="zoomOut()">- 缩小</button>
        <button onclick="resetZoom()">适应</button>
    </div>
    <span class="meta">{meta.get('nodeCount', 0)} components · {len(data.get('dependencies', []))} dependencies · {len(data.get('domains', []))} domains</span>
</div>
<div class="svg-wrap" id="svgWrap">
    {svg_content}
</div>
<div class="tooltip" id="tooltip"></div>
<script>
const compData = {comp_json};
let scale = 1;

// Add hover effects to all node rects
document.querySelectorAll('svg rect[filter="url(#shadow)"]').forEach(rect => {{
    rect.style.cursor = 'pointer';
    rect.addEventListener('mouseenter', function(e) {{
        this.setAttribute('stroke-width', '2.5');
        // Find component ID by position
        const x = parseFloat(this.getAttribute('x'));
        const y = parseFloat(this.getAttribute('y'));
        // Search for component near this position
        for (const [id, c] of Object.entries(compData)) {{
            if (Math.abs(x - (c._x || 0)) < 5 && Math.abs(y - (c._y || 0)) < 5) {{
                showTooltip(e, c);
                break;
            }}
        }}
    }});
    rect.addEventListener('mouseleave', function() {{
        this.setAttribute('stroke-width', '1.5');
        hideTooltip();
    }});
}});

function showTooltip(e, comp) {{
    const tt = document.getElementById('tooltip');
    const routes = (comp.routes || []).slice(0, 3).map(r => r.method + ' ' + r.path).join('<br>');
    tt.innerHTML = `<div class="tt-name">${{comp.name}}</div>
        <div class="tt-meta">${{comp.type}} · ${{comp.layer}} · ${{comp.domain || ''}}</div>
        ${{routes ? '<div class="tt-meta" style="margin-top:3px">' + routes + '</div>' : ''}}
        <div class="tt-meta">${{comp.file || ''}}</div>`;
    tt.classList.add('show');
    tt.style.left = (e.clientX + 12) + 'px';
    tt.style.top = (e.clientY - 10) + 'px';
}}

function hideTooltip() {{
    document.getElementById('tooltip').classList.remove('show');
}}

function zoomIn() {{ scale = Math.min(3, scale + 0.15); applyZoom(); }}
function zoomOut() {{ scale = Math.max(0.3, scale - 0.15); applyZoom(); }}
function resetZoom() {{ scale = 1; applyZoom(); }}
function applyZoom() {{
    const svg = document.querySelector('.svg-wrap svg');
    if (svg) svg.style.transform = 'scale(' + scale + ')';
    svg.style.transformOrigin = 'top left';
}}
</script>
</body>
</html>'''

    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"[OK] Interactive HTML generated: {html_path}")

if __name__ == '__main__':
    main()
