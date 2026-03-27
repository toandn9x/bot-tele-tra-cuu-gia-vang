# Bot Tra Cuu Gia Vang

Telegram Bot tra cuu gia vang, gia xang dau va ty gia ngoai te theo thoi gian thuc.

## Tinh nang

- `/gold` — Gia vang (SJC, DOJI, PNJ, the gioi...)
- `/xang` — Gia xang dau Petrolimex (Vung 1 & Vung 2)
- `/usd` — Ty gia USD (VND, EUR, JPY)
- `/info` — Thong tin tac gia & ung ho
- Menu nut bam inline, tu dong dang ky lenh

## Cai dat

```bash
pip install -r requirements.txt
```

## Cau hinh

Dien bot token vao `config.py`:

```python
TELEGRAM_BOT_TOKEN = "your-bot-token-here"
```

## Chay

```bash
python main.py
```

## Cau truc

```text
config.py      — Cau hinh dich vu & bot token
main.py        — Khoi chay bot Telegram
models.py      — Model ProviderConfig (Pydantic)
providers.py   — Cac provider lay du lieu (JSON, Petrolimex, Scraper)
```

## Them dich vu moi

Them mot `ProviderConfig` vao danh sach `SERVICES` trong `config.py`:

```python
ProviderConfig(
    name="Ten hien thi",
    command="lenh",
    url="https://api.example.com/data",
    data_path="data.items",
    fields={
        "Cot 1": "field_name_1",
        "Cot 2": "field_name_2"
    }
)
```

## Yeu cau

- Python 3.10+
- Bot token tu [@BotFather](https://t.me/BotFather)

## Tac gia & Ung ho

- Tac gia: **Toandn**
- Ngan hang: **BIDV** — `1222172532`
