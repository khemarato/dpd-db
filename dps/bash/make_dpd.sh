#!/usr/bin/env bash

# generate dictionaries

set -e
python -c "from tools.configger import print_config_settings; print_config_settings(['dictionary', 'goldendict', 'exporter'])"

python -c "from tools.configger import config_update; config_update('exporter', 'language', 'en')"

scripts/bash/generate_components.sh

db/frequency/ebt_calculation.py

dps/scripts/change_ebt_count.py

exporter/grammar_dict/grammar_dict.py

exporter/goldendict/main.py
exporter/deconstructor/deconstructor_exporter.py

# exporter/tpr/tpr_exporter.py
exporter/ebook/ebook_exporter.py

scripts/zip_goldendict_mdict.py

dps/scripts/move_mdict.py

# Check if the configuration setting
if python -c "from tools.configger import config_test; result = config_test('dictionary', 'show_ebt_count', 'no'); print('show_ebt_count is False') if result == 'no' else exit(not result)"; then
    # Do nothing if the condition is False
    echo 'scripts/zip_goldendict_mdict.py and db/frequency/ebt_calculation.py are disabled'
else
    # Run if the condition is True
    scripts/zip_goldendict_mdict.py
    db/frequency/ebt_calculation.py
fi

# Update the show_ebt_count setting to 'no' if it was 'yes'
if python -c "from tools.configger import config_test; exit(not config_test('dictionary', 'show_ebt_count', 'yes'))"; then

    python -c "from tools.configger import config_update; config_update('dictionary', 'show_ebt_count', 'no')"

fi

git checkout -- pyproject.toml

git checkout -- db/sanskrit/root_families_sanskrit.tsv

git checkout -- exporter/goldendict/javascript/family_compound_json.js
git checkout -- exporter/goldendict/javascript/family_idiom_json.js
git checkout -- exporter/goldendict/javascript/family_root_json.js
git checkout -- exporter/goldendict/javascript/family_set_json.js
git checkout -- exporter/goldendict/javascript/family_word_json.js




