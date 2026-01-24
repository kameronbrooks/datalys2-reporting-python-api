import json
import re
import os
import glob

def update_versions():
    # Load config
    with open('versions.json', 'r') as f:
        config = json.load(f)

    pkg_version = config.get('package_version')
    dl2_version = config.get('dl2_version')

    print(f"Updating project to Package Version: {pkg_version}, DL2 Version: {dl2_version}")

    # 1. Update pyproject.toml
    pyproject_path = 'pyproject.toml'
    with open(pyproject_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Regex for: version = "0.2.7"
    new_content = re.sub(
        r'version = "[^"]+"',
        f'version = "{pkg_version}"',
        content
    )
    
    if content != new_content:
        with open(pyproject_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Updated {pyproject_path}")
    else:
        print(f"No changes needed for {pyproject_path}")

    # 2. Update dl2_reports/report.py
    report_path = os.path.join('dl2_reports', 'report.py')
    with open(report_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Regex for: DL2_VERSION = "0.2.7"
    new_content = re.sub(
        r'DL2_VERSION = "[^"]+"',
        f'DL2_VERSION = "{dl2_version}"',
        content
    )

    if content != new_content:
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Updated {report_path}")
    else:
        print(f"No changes needed for {report_path}")

    # 3. Update README.md
    readme_path = 'README.md'
    with open(readme_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Regex for: **Version 0.2.6**
    content = re.sub(
        r'\*\*Version [0-9.]+\*\*',
        f'**Version {pkg_version}**',
        content
    )
    # Regex for: Compatible with dl2 version 0.2.6
    new_content = re.sub(
        r'Compatible with dl2 version [0-9.]+',
        f'Compatible with dl2 version {dl2_version}',
        content
    )
    
    if content != new_content:
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Updated {readme_path}")
    else:
        print(f"No changes needed for {readme_path}")

    # 4. Update DOCUMENTATION.md
    doc_path = 'DOCUMENTATION.md'
    with open(doc_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Regex for: **Version 0.2.5**
    content = re.sub(
        r'\*\*Version [0-9.]+\*\*',
        f'**Version {pkg_version}**',
        content
    )
    # Regex for: <meta name="dl-version" content="0.2.2">
    new_content = re.sub(
        r'<meta name="dl-version" content="[0-9.]+">',
        f'<meta name="dl-version" content="{dl2_version}">',
        content
    )

    if content != new_content:
        with open(doc_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Updated {doc_path}")
    else:
        print(f"No changes needed for {doc_path}")

    # 5. Update expected HTML test output
    # If the version changes, the <meta name="dl-version"> tag in goldens needs updating or tests compare fail.
    # Note: In a stricter environment, you might mock the version in tests instead of updating goldens.
    expected_files = glob.glob(os.path.join('tests', 'data', 'expected', '*.html'))
    
    for file_path in expected_files:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Regex for: <meta name="dl-version" content="0.2.7">
        new_content = re.sub(
            r'<meta name="dl-version" content="[^"]+">',
            f'<meta name="dl-version" content="{dl2_version}">',
            content
        )

        if content != new_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"Updated golden file: {file_path}")

if __name__ == "__main__":
    update_versions()
