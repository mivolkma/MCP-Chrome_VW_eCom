from __future__ import annotations

import argparse
import json
from pathlib import Path
import datetime

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        :root {
            --color-pass: #28a745;
            --color-fail: #dc3545;
            --color-warn: #ffc107;
            --color-neutral: #6c757d;
            
            /* Light Mode Defaults */
            --color-bg: #f8f9fa;
            --color-text: #212529;
            --color-surface: #fff;
            --color-border: #dee2e6;
            --color-th: #666;
            --color-placeholder-bg: #f1f3f5;
        }

        body.dark-mode {
            --color-bg: #1a1a1a;
            --color-text: #e0e0e0;
            --color-surface: #2c2c2c;
            --color-border: #444;
            --color-th: #aaa;
            --color-placeholder-bg: #333;
        }

        body {
            font-family: var(--font-family, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif);
            background-color: var(--color-bg);
            color: var(--color-text);
            margin: 0;
            padding: 2rem;
            transition: background-color 0.3s, color 0.3s;
        }
        header {
            border-bottom: 2px solid var(--color-border);
            padding-bottom: 1rem;
            margin-bottom: 2rem;
        }
        h1, h2, h3 {
            margin: 0;
            padding-bottom: 1rem;
        }
        .controls {
            margin: 1rem 0;
            padding: 1rem;
            background: var(--color-surface);
            border: 1px solid var(--color-border);
            border-radius: 8px;
            display: flex;
            align-items: center;
            gap: 1rem;
        }
        .controls button {
            padding: 0.5rem 1rem;
            font-size: 1rem;
            border-radius: 5px;
            border: 1px solid var(--color-neutral);
            cursor: pointer;
            background-color: var(--color-surface);
            color: var(--color-text);
        }
        .theme-switch-wrapper {
            display: flex;
            align-items: center;
            margin-left: auto; /* Pushes the switch to the right */
        }
        .theme-switch {
            display: inline-block;
            height: 34px;
            position: relative;
            width: 60px;
            margin-left: 8px;
        }
        .theme-switch input {
            display:none;
        }
        .slider {
            background-color: #ccc;
            bottom: 0;
            cursor: pointer;
            left: 0;
            position: absolute;
            right: 0;
            top: 0;
            transition: .4s;
        }
        .slider:before {
            background-color: #fff;
            bottom: 4px;
            content: "";
            height: 26px;
            left: 4px;
            position: absolute;
            transition: .4s;
            width: 26px;
        }
        input:checked + .slider {
            background-color: var(--color-pass);
        }
        input:checked + .slider:before {
            transform: translateX(26px);
        }
        .slider.round {
            border-radius: 34px;
        }
        .slider.round:before {
            border-radius: 50%;
        }
        .sheet-section {
            margin-bottom: 2rem;
        }
        details {
            background: var(--color-surface);
            border: 1px solid var(--color-border);
            border-radius: 8px;
            margin-bottom: 1rem;
            page-break-inside: avoid;
        }
        summary {
            padding: 1rem;
            font-weight: bold;
            cursor: pointer;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .details-content {
            padding: 0 1rem 1rem 1rem;
            border-top: 1px solid var(--color-border);
        }
        .status-badge {
            padding: 0.25em 0.6em;
            font-size: 0.8em;
            font-weight: 700;
            line-height: 1;
            color: #fff;
            text-align: center;
            white-space: nowrap;
            vertical-align: baseline;
            border-radius: 0.35rem;
        }
        .status-pass { background-color: var(--color-pass); }
        .status-fail { background-color: var(--color-fail); }
        .status-warn { background-color: var(--color-warn); }
        .status-neutral { background-color: var(--color-neutral); }
        table {
            width: 100%;
            border-collapse: collapse;
        }
        th, td {
            text-align: left;
            padding: 0.75rem;
            vertical-align: top;
            border-top: 1px solid var(--color-border);
        }
        th {
            width: 20%;
            font-weight: normal;
            color: var(--color-th);
        }
        .screenshot-placeholder {
            border: 2px dashed var(--color-border);
            padding: 2rem;
            text-align: center;
            margin-top: 1rem;
            border-radius: 5px;
            background: var(--color-placeholder-bg);
        }
        .screenshot-placeholder img {
            max-width: 100%;
            display: none; /* Hidden by default, shown if src is valid */
        }

        .checklist {
            list-style: none;
            padding: 0;
            margin: 1rem 0;
        }
        .checklist li {
            display: flex;
            align-items: center;
            padding: 0.5rem 0;
            border-bottom: 1px solid var(--color-border);
        }
        .checklist li:last-child {
            border-bottom: none;
        }
        .status-icon {
            font-size: 1.5rem;
            margin-right: 1rem;
            cursor: pointer;
            user-select: none; /* Prevents text selection on repeated clicks */
        }
        .status-icon[data-status="unknown"]:before { content: '❓'; }
        .status-icon[data-status="pass"]:before { content: '✅'; }
        .status-icon[data-status="fail"]:before { content: '❌'; }
        .status-icon[data-status="warn"]:before { content: '⚠️'; color: var(--color-warn); }

        #summary-report {
            background: var(--color-surface);
            border: 1px solid var(--color-border);
            border-radius: 8px;
            padding: 1.5rem;
            margin-bottom: 2rem;
        }
        .summary-stats {
            display: flex;
            justify-content: space-around;
            text-align: center;
            margin-bottom: 1.5rem;
        }
        .stat {
            flex: 1;
        }
        .stat-value {
            font-size: 2rem;
            font-weight: bold;
        }
        .stat-label {
            font-size: 0.9rem;
            color: var(--color-th);
        }
        #stat-passed { color: var(--color-pass); }
        #stat-failed { color: var(--color-fail); }
        #stat-warned { color: var(--color-warn); }
        
        .status-bar {
            height: 20px;
            display: flex;
            border-radius: 5px;
            overflow: hidden;
            background: #e9ecef;
            margin-bottom: 1rem;
        }
        .bar-segment {
            height: 100%;
            transition: width 0.5s ease-in-out;
        }
        .bar-passed { background-color: var(--color-pass); }
        .bar-failed { background-color: var(--color-fail); }
        .bar-warned { background-color: var(--color-warn); }

        #quick-nav ul {
            list-style: none;
            padding: 0;
            columns: 2;
            -webkit-columns: 2;
            -moz-columns: 2;
        }
        #quick-nav li a {
            text-decoration: none;
            color: var(--color-text);
            display: block;
            padding: 0.25rem 0;
        }
        #quick-nav li a:hover {
            text-decoration: underline;
        }

        @media print {
            body, details, .controls button {
                background-color: #fff !important;
                color: #000 !important;
            }
            body {
                padding: 0;
            }
            header, .controls {
                display: none;
            }
            details {
                border: 1px solid #ccc;
                box-shadow: none;
                page-break-before: auto;
            }
            details[open] {
                page-break-inside: avoid;
            }
            details summary {
                cursor: default;
            }
            .sheet-section {
                page-break-before: always;
            }
            .sheet-section:first-child {
                page-break-before: auto;
            }
            .status-badge {
                border: 1px solid #000;
                color: #000 !important;
                background-color: #fff !important;
            }
        }
    </style>
</head>
<body>
    <header>
        <h1>{title}</h1>
        <p>Generated on: <span id="generation-date">{generation_date}</span></p>
        <p>Source: {source_file}</p>
    </header>

    <section id="summary-report">
        <h2>Test Run Summary</h2>
        <div class="summary-stats">
            <div class="stat">
                <div class="stat-value" id="stat-total">0</div>
                <div class="stat-label">Total Cases</div>
            </div>
            <div class="stat">
                <div class="stat-value" id="stat-passed">0</div>
                <div class="stat-label">Passed</div>
            </div>
            <div class="stat">
                <div class="stat-value" id="stat-failed">0</div>
                <div class="stat-label">Failed</div>
            </div>
            <div class="stat">
                <div class="stat-value" id="stat-warned">0</div>
                <div class="stat-label">Warnings</div>
            </div>
            <div class="stat">
                <div class="stat-value" id="stat-duration">0s</div>
                <div class="stat-label">Duration</div>
            </div>
        </div>
        <div class="status-bar">
            <div class="bar-segment bar-passed" id="bar-passed" style="width: 0%;"></div>
            <div class="bar-segment bar-failed" id="bar-failed" style="width: 0%;"></div>
            <div class="bar-segment bar-warned" id="bar-warned" style="width: 0%;"></div>
        </div>
        <details>
            <summary>Quick Navigation</summary>
            <div id="quick-nav">
                <ul>
                    <!-- Quick navigation links will be inserted here -->
                </ul>
            </div>
        </details>
    </section>

    <div class="controls">
        <button id="btn-expand">Expand All</button>
        <button id="btn-collapse">Collapse All</button>
        <div class="theme-switch-wrapper">
            <span>Dark Mode</span>
            <label class="theme-switch" for="theme-checkbox">
                <input type="checkbox" id="theme-checkbox" />
                <div class="slider round"></div>
            </label>
        </div>
    </div>

    {body_content}

    <script>
        document.addEventListener('DOMContentLoaded', () => {
            const themeSwitch = document.getElementById('theme-checkbox');
            const currentTheme = localStorage.getItem('theme');

            if (currentTheme) {
                document.body.classList.add(currentTheme);
                if (currentTheme === 'dark-mode') {
                    themeSwitch.checked = true;
                }
            } else if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
                // Set default based on OS preference
                document.body.classList.add('dark-mode');
                themeSwitch.checked = true;
                localStorage.setItem('theme', 'dark-mode');
            }

            themeSwitch.addEventListener('change', function(e) {
                if(e.target.checked) {
                    document.body.classList.add('dark-mode');
                    localStorage.setItem('theme', 'dark-mode');
                } else {
                    document.body.classList.remove('dark-mode');
                    localStorage.setItem('theme', 'light-mode');
                }
            });

            document.getElementById('btn-expand').addEventListener('click', () => {
                document.querySelectorAll('details').forEach(d => d.open = true);
            });
            document.getElementById('btn-collapse').addEventListener('click', () => {
                document.querySelectorAll('details').forEach(d => d.open = false);
            });
            
            // For print, ensure all details are open
            window.addEventListener('beforeprint', () => {
                document.querySelectorAll('details').forEach(d => d.open = true);
            });

            // Handle checklist status clicks
            document.querySelectorAll('.status-icon').forEach(icon => {
                icon.addEventListener('click', () => {
                    const currentStatus = icon.getAttribute('data-status');
                    let nextStatus;
                    switch (currentStatus) {
                        case 'unknown':
                            nextStatus = 'pass';
                            break;
                        case 'pass':
                            nextStatus = 'fail';
                            break;
                        case 'fail':
                            nextStatus = 'warn';
                            break;
                        case 'warn':
                            nextStatus = 'unknown';
                            break;
                        default:
                            nextStatus = 'unknown';
                    }
                    icon.setAttribute('data-status', nextStatus);
                    updateSummary();
                });
            });

            // Show screenshot image if src is valid
            document.querySelectorAll('.screenshot-placeholder img').forEach(img => {
                if (img.getAttribute('src')) {
                    img.style.display = 'block';
                    img.parentElement.style.padding = '0';
                    img.parentElement.style.border = '1px solid var(--color-border)';
                }
            });

            function updateSummary() {
                const all_cases = document.querySelectorAll('h3[id^="case-"]');
                const totalCases = all_cases.length;
                
                let passedCases = 0;
                let failedCases = 0;
                let warnedCases = 0;

                all_cases.forEach(caseHeader => {
                    const caseContainer = caseHeader.nextElementSibling;
                    const checklists = caseContainer.querySelectorAll('.checklist li');
                    if (checklists.length === 0) return;

                    let hasFail = false;
                    let hasWarn = false;
                    let hasUnknown = false;

                    checklists.forEach(item => {
                        const status = item.querySelector('.status-icon').getAttribute('data-status');
                        if (status === 'fail') hasFail = true;
                        if (status === 'warn') hasWarn = true;
                        if (status === 'unknown') hasUnknown = true;
                    });

                    if (hasFail) {
                        failedCases++;
                    } else if (hasWarn) {
                        warnedCases++;
                    } else if (!hasUnknown) {
                        passedCases++;
                    }
                });

                const notRunCases = totalCases - (passedCases + failedCases + warnedCases);

                document.getElementById('stat-total').textContent = totalCases;
                document.getElementById('stat-passed').textContent = passedCases;
                document.getElementById('stat-failed').textContent = failedCases;
                document.getElementById('stat-warned').textContent = warnedCases;

                const totalForBar = Math.max(1, passedCases + failedCases + warnedCases);
                const passedPercent = (passedCases / totalForBar) * 100;
                const failedPercent = (failedCases / totalForBar) * 100;
                const warnedPercent = (warnedCases / totalForBar) * 100;

                document.getElementById('bar-passed').style.width = `${passedPercent}%`;
                document.getElementById('bar-failed').style.width = `${failedPercent}%`;
                document.getElementById('bar-warned').style.width = `${warnedPercent}%`;
            }

            // Initial summary calculation
            updateSummary();
        });
    </script>
</body>
</html>
"""

def get_status_class(status: str) -> str:
    status_l = status.lower()
    if status_l in ("completed", "yes", "pass"):
        return "status-pass"
    if status_l in ("no", "failed", "fail"):
        return "status-fail"
    if "in progress" in status_l or status_l == "warn":
        return "status-warn"
    return "status-neutral"

def create_step_html(step: dict, case_id: str, scenario_name: str, step_num: int) -> str:
    action = step.get("action", "N/A")
    value = step.get("value", "")
    testid = step.get("data-testid", "")
    
    # Create a unique identifier for the step (must match execute_smoketest.py)
    step_id = f'{case_id}-Step{step_num}-{action.replace(" ", "")}'

    # For simplicity, we'll use the action as the main display line.
    # More complex data could be combined here.
    main_line = f'{action}: {value or testid}'

    # Screenshot placeholder logic
    img_filename = f"{step_id}.png"
    screenshot_html = f"""
    <div class="screenshot-placeholder">
        <p>Screenshot for {step_id}</p>
        <img src="./screenshots/{img_filename}" alt="Screenshot for {step_id}" onerror="this.style.display='none'; this.parentElement.querySelector('p').style.display='block';" onload="this.style.display='block'; this.parentElement.querySelector('p').style.display='none';">
        <small>To display an image, place '{img_filename}' in a 'screenshots' subfolder.</small>
    </div>
    """

    return f"""
    <details>
        <summary>
            <span>{main_line}</span>
            <span id="badge-{step_id}" class="status-badge status-neutral">Not Run</span>
        </summary>
        <div class="details-content">
            <table>
                <tr><th>Scenario</th><td>{scenario_name}</td></tr>
                <tr><th>Test Case ID</th><td>{case_id}</td></tr>
                <tr><th>Action</th><td>{action}</td></tr>
                <tr><th>Value</th><td>{value}</td></tr>
                <tr><th>Data Test ID</th><td>{testid}</td></tr>
            </table>
            {screenshot_html}
        </div>
    </details>
    """

def create_environment_section(env_data: dict) -> str:
    if not env_data:
        return ""

    env_details = "".join(f"<tr><th>{key.replace('_', ' ').title()}</th><td>{value}</td></tr>" for key, value in env_data.items() if not isinstance(value, dict))
    
    for key, value in env_data.items():
        if isinstance(value, dict):
            env_details += f"<tr><th colspan='2' style='padding-top: 1rem; font-weight:bold;'>{key.replace('_', ' ').title()}</th></tr>"
            env_details += "".join(f"<tr><th style='padding-left: 2rem;'>{sub_key.replace('_', ' ').title()}</th><td>{sub_value}</td></tr>" for sub_key, sub_value in value.items())

    return f"""
    <section class="sheet-section">
        <h2>Test Environment</h2>
        <details open>
            <summary>Environment Details</summary>
            <div class="details-content">
                <table>
                    {env_details}
                </table>
            </div>
        </details>
    </section>
    """

def main():
    parser = argparse.ArgumentParser(description="Generate an HTML report from JSON test data.")
    parser.add_argument(
        "--input",
        type=Path,
        required=True,
        help="Path to the input JSON file (e.g., charter.json).",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        required=True,
        help="Directory to save the HTML report in.",
    )
    parser.add_argument(
        "--environment",
        type=Path,
        help="Optional path to the environment snapshot JSON file.",
    )
    parser.add_argument(
        "--title",
        type=str,
        default="BTO Test Report",
        help="Optional title for the report.",
    )
    args = parser.parse_args()

    if not args.input.exists():
        raise SystemExit(f"Error: Input file not found at {args.input}")

    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "screenshots").mkdir(exist_ok=True)  # Ensure screenshots dir exists

    # Read environment data if provided
    env_data = {}
    if args.environment and args.environment.exists():
        with args.environment.open("r", encoding="utf-8") as f:
            env_data = json.load(f)

    with args.input.open("r", encoding="utf-8") as f:
        test_scenarios = json.load(f)

    # Start building body content
    body_content = create_environment_section(env_data)
    quick_nav_links = []
    
    for scenario in test_scenarios:
        scenario_name = scenario.get("testScenario", "Unnamed Scenario")
        body_content += f'<section class="sheet-section" id="scenario-{scenario_name.replace(" ", "-")}"><h2>{scenario_name}</h2>'

        for test_case in scenario.get("testCases", []):
            case_id = test_case.get("id", "N/A")
            description = test_case.get("description", "")
            case_anchor = f"case-{case_id}"
            quick_nav_links.append(f'<li><a href="#{case_anchor}">{case_id}: {scenario_name}</a></li>')

            # Create checklist from description
            checklist_items = []
            # Handle multiline descriptions, splitting by newline
            for line in description.splitlines():
                line = line.strip()
                if line.startswith('-'):
                    clean_line = line.strip('- ').replace('<', '&lt;').replace('>', '&gt;')
                    checklist_items.append(
                        f'<li><span class="status-icon" data-status="unknown"></span><span>{clean_line}</span></li>'
                    )

            if checklist_items:
                checklist_html = f"<ul class=\"checklist\">{''.join(checklist_items)}</ul>"
            else:
                description_safe = description.replace('<', '&lt;').replace('>', '&gt;').replace('\n', '<br>')
                checklist_html = f"<p>{description_safe}</p>"

            body_content += f'<h3 id="{case_anchor}">Test Case: {case_id}</h3>'
            body_content += f'<div><strong>Description:</strong>{checklist_html}</div>'

            for step_num, step in enumerate(test_case.get("steps", []), start=1):
                body_content += create_step_html(step, case_id, scenario_name, step_num)

        body_content += '</section>'

    generation_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    source_file = args.input.name
    
    # Replace placeholders in the main template
    # Ensure title includes generation date/time for traceability.
    report_title = f"{args.title} ({generation_date})"
    final_html = HTML_TEMPLATE.replace('{title}', report_title)
    final_html = final_html.replace('{generation_date}', generation_date)
    final_html = final_html.replace('{source_file}', source_file)
    final_html = final_html.replace('{body_content}', body_content)
    
    # Insert quick navigation links
    final_html = final_html.replace('<!-- Quick navigation links will be inserted here -->', "".join(quick_nav_links))

    output_path = args.output_dir / "BTO_Test_Report_v1.0.html"
    output_path.write_text(final_html, encoding="utf-8")

    print(f"Successfully generated HTML report: {output_path}")



if __name__ == "__main__":
    main()
