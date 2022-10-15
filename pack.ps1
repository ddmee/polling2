rm -force -recurse dist -ErrorAction silentlycontinue
venv\scripts\activate.ps1
python setup.py test
python setup.py bdist_wheel --universal sdist
write-host 'python -m twine upload dist/* -u "<value>" -p "<value>"' -BackgroundColor DarkGray
