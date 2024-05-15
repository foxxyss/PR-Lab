# Laboratorul 5 - Email Client
# Utilizaera

Inainte de utilizare trebuie instalata libraria Flask (pentru interfata) folosind comanda:
```bash
pip install Flask
```
sau indirect prin:
```bash
pip install -r .\requirements.txt
```
Dupa care run la program:
```bash
python run.py
```

## Info
Fisierul `run.py` contine serverul Flask care este doar o interfata pentru a interactiona cu clientul de email, iar fisierul `email_client.py` contine insusi laboratorul, in el se afla logica pentru trimitere email, reply, primire a mesajelor pe IMAP sau POP3 etc.

Clientul email poate fi folosit oriunde (interfata, consola etc) deoarece este independent de interfata.

Se poate folosi important clasa `EmailClient` din `email_client.py` pentru a trimite emailuri, a primi emailuri, a face reply la emailuri etc.
```python
from email_client import EmailClient
```
`Important` - Pentru a folosi clientul de email trebuie sa aveti un cont de email valid, in fisierul `email_client.py` se afla variabilele `EMAIL` si `PASSWORD` care trebuie completate cu datele voastre. (pentru password se poate folosi si un token de securitate daca aveti activat 2FA pe contul de email, in cazul gmail se poate genera unul aici: https://myaccount.google.com/apppasswords , dar deja depinde de profil, unele conturi nu au aceasta optiune activata)