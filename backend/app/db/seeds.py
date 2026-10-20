import asyncio

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Organisation, Setting, Unit
from app.db.session import async_session_factory

KERALA_DISTRICTS = [
    {"name": "Thiruvananthapuram", "name_ml": "തിരുവനന്തപുരം", "code": "KLTVC", "path": "kerala.tvm"},
    {"name": "Kollam", "name_ml": "കൊല്ലം", "code": "KLKLM", "path": "kerala.klm"},
    {"name": "Pathanamthitta", "name_ml": "പത്തനംതിട്ട", "code": "KLPTA", "path": "kerala.pta"},
    {"name": "Alappuzha", "name_ml": "ആലപ്പുഴ", "code": "KLALP", "path": "kerala.alp"},
    {"name": "Kottayam", "name_ml": "കോട്ടയം", "code": "KLKTM", "path": "kerala.ktm"},
    {"name": "Idukki", "name_ml": "ഇടുക്കി", "code": "KLIDK", "path": "kerala.idk"},
    {"name": "Ernakulam", "name_ml": "എറണാകുളം", "code": "KLEKM", "path": "kerala.ekm"},
    {"name": "Thrissur", "name_ml": "തൃശ്ശൂർ", "code": "KLTSR", "path": "kerala.tsr"},
    {"name": "Palakkad", "name_ml": "പാലക്കാട്", "code": "KLPKD", "path": "kerala.pkd"},
    {"name": "Malappuram", "name_ml": "മലപ്പുറം", "code": "KLMLP", "path": "kerala.mlp"},
    {"name": "Kozhikode", "name_ml": "കോഴിക്കോട്", "code": "KLKKD", "path": "kerala.kkd"},
    {"name": "Wayanad", "name_ml": "വയനാട്", "code": "KLWYD", "path": "kerala.wyd"},
    {"name": "Kannur", "name_ml": "കണ്ണൂർ", "code": "KLKNR", "path": "kerala.knr"},
    {"name": "Kasaragod", "name_ml": "കാസർഗോഡ്", "code": "KLKSD", "path": "kerala.ksd"},
]

DEFAULT_SETTINGS = [
    {
        "key": "module_autopay",
        "value": {"enabled": False},
        "description": "UPI Autopay mandate recurring subscription (deferred in pilot)",
    },
    {
        "key": "module_automated_lapse",
        "value": {"enabled": False, "grace_period_months": 6},
        "description": "Automatic membership lapse engine (off by default)",
    },
    {
        "key": "module_grievance_filing",
        "value": {"enabled": False, "contacts_display": True},
        "description": "Online grievance ticketing (contacts display only during pilot)",
    },
    {
        "key": "fee_structure",
        "value": {
            "registration_fee": 100,
            "monthly_fee": 10,
            "default_advance_months": 6,
            "total_initial_amount": 160,
        },
        "description": "Statutory pilot fee: Rs 100 registration + 6 months subscription (Rs 60)",
    },
]


async def seed_database(session: AsyncSession) -> None:
    # 1. Seed Organisation
    org_stmt = select(Organisation).limit(1)
    org_res = await session.execute(org_stmt)
    if not org_res.scalar_one_or_none():
        org = Organisation(
            name="Kerala State Gig & Platform Workers Union (CITU)",
            name_ml="കേരള സ്റ്റേറ്റ് ഗിഗ് & പ്ലാറ്റ്‌ഫോം വർക്കേഴ്സ് യൂണിയൻ (സി.ഐ.ടി.യു)",
            registration_number="CITU/KL/GIG/2026/04",
            default_language="ml",
        )
        session.add(org)

    # 2. Seed State Unit
    state_stmt = select(Unit).where(Unit.code == "KLSTATE")
    state_res = await session.execute(state_stmt)
    if not state_res.scalar_one_or_none():
        state_unit = Unit(
            name="Kerala State Committee",
            name_ml="കേരള സംസ്ഥാന കമ്മിറ്റി",
            code="KLSTATE",
            path="kerala",
            level="state",
        )
        session.add(state_unit)

    # 3. Seed 14 Districts
    for dist in KERALA_DISTRICTS:
        dist_stmt = select(Unit).where(Unit.code == dist["code"])
        dist_res = await session.execute(dist_stmt)
        if not dist_res.scalar_one_or_none():
            unit = Unit(
                name=dist["name"],
                name_ml=dist["name_ml"],
                code=dist["code"],
                path=dist["path"],
                level="district",
            )
            session.add(unit)

    # 4. Seed Settings
    for s in DEFAULT_SETTINGS:
        setting_stmt = select(Setting).where(Setting.key == s["key"])
        setting_res = await session.execute(setting_stmt)
        if not setting_res.scalar_one_or_none():
            setting = Setting(
                key=s["key"],
                value=s["value"],
                description=s["description"],
            )
            session.add(setting)

    await session.commit()


if __name__ == "__main__":
    async def main():
        async with async_session_factory() as session:
            await seed_database(session)
            print("Successfully seeded CITU Organisation, Units & Settings.")

    asyncio.run(main())
