Application Requirements:
- Python 3.12 (or any Python 3.8+ should work, but developed/tested on 3.12)
- Tkinter (bundled with most Python installs see note below if missing)
- 'cryptography' library (for Fernet password encryption)

Install Python 3.12 [python.org](https://www.python.org/downloads/).

Install the 'cryptography' library (this provides Fernet, used to encrypt stored passwords):

   pip install cryptography

   If you have multiple Python versions installed, you may need to be explicit:
   python3 -m pip install cryptography

   On Windows:
   py -m pip install cryptography

On first launch, no 'users.txt' or 'check_ins.txt' files exist yet, the app creates these automatically once you sign up and complete your first check-in.

A 'secret.key' file is also generated on first run to encrypt/decrypt stored passwords. Keep this file safe. if it's lost or deleted, all previously stored passwords become permanently unreadable and accounts will need to be recreated.
IF 'secret.key' contents have been deleted, delete the file from the folder and run the application again. A new 'secret.key' should be created,


Acknowledgements:

- Icons/emojis: https://unicode.org/emoji/charts/full-emoji-list.html
- Flowcharts: draw.io
- Project management: Trello.com
- GUI Wireframe: Canva.com